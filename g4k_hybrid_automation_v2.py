#!/usr/bin/env python3
"""
G4K 방문예약 하이브리드 자동화 시스템 v2
스텔스 브라우저 통합 버전
"""

import time
import logging
from datetime import datetime
from typing import Dict, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from stealth_browser import StealthBrowser, G4KStealthAutomation
from profile_manager import ConfigManager
from auto_input_handler import AutoInputHandler
from calendar_refresher import CalendarRefresher
from adaptive_calendar_refresher import AdaptiveCalendarRefresher, ultra_fast_calendar_monitor
from ticketing_strategy import ticketing_automation

logger = logging.getLogger(__name__)


class G4KHybridAutomationV2(G4KStealthAutomation):
    """개선된 하이브리드 자동화 클래스"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.auto_input_handler = None
        
    def initialize(self) -> bool:
        """초기화 (스텔스 브라우저 포함)"""
        if not super().initialize():
            return False
            
        # 자동 입력 핸들러 초기화
        self.auto_input_handler = AutoInputHandler(
            self.driver,
            self.config_manager
        )
        
        return True
    
    def wait_for_calendar(self) -> bool:
        """캘린더 나타날 때까지 대기"""
        try:
            logger.info("캘린더 대기 중...")
            
            # 여러 선택자 시도
            calendar_selectors = [
                (By.CLASS_NAME, "calendar"),
                (By.CLASS_NAME, "ui-datepicker"),
                (By.CLASS_NAME, "calendar-container"),
                (By.ID, "calendar"),
                (By.CSS_SELECTOR, "[class*='calendar']"),
                (By.CSS_SELECTOR, "[id*='calendar']")
            ]
            
            wait = WebDriverWait(self.driver, 30)
            
            for selector_type, selector_value in calendar_selectors:
                try:
                    element = wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    logger.info(f"캘린더 발견: {selector_type}={selector_value}")
                    return True
                except TimeoutException:
                    continue
            
            logger.error("캘린더를 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"캘린더 대기 중 오류: {e}")
            return False
    
    def detect_available_dates(self) -> list:
        """예약 가능한 날짜 감지"""
        try:
            available_dates = []
            
            # 캘린더에서 활성화된 날짜 찾기
            date_selectors = [
                "td.available",
                "td.selectable",
                "td:not(.disabled)",
                ".calendar-day.available",
                "[data-handler='selectDay']"
            ]
            
            for selector in date_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"{len(elements)}개의 가능한 날짜 발견 (선택자: {selector})")
                    
                    for element in elements:
                        try:
                            date_text = element.text.strip()
                            if date_text and date_text.isdigit():
                                available_dates.append({
                                    'element': element,
                                    'date': date_text
                                })
                        except:
                            continue
                    
                    if available_dates:
                        break
            
            return available_dates
            
        except Exception as e:
            logger.error(f"날짜 감지 중 오류: {e}")
            return []
    
    def select_date(self, date_info: dict) -> bool:
        """날짜 선택"""
        try:
            element = date_info['element']
            date = date_info['date']
            
            logger.info(f"날짜 선택 시도: {date}일")
            
            # 인간같은 클릭
            self.browser.human_like_click(self.driver, element)
            
            # 선택 확인
            self.browser.human_like_delay(0.5, 1.0)
            
            return True
            
        except Exception as e:
            logger.error(f"날짜 선택 실패: {e}")
            return False
    
    def fill_passport_info(self) -> bool:
        """여권 정보 자동 입력"""
        try:
            profile = self.config_manager.profile_manager.get_active_profile()
            if not profile:
                logger.error("활성 프로필이 없습니다")
                return False
            
            # 여권번호 입력 필드 찾기
            passport_selectors = [
                "input[name*='passport']",
                "input[id*='passport']",
                "input[placeholder*='여권']",
                "#passportNo",
                "input.passport-input"
            ]
            
            for selector in passport_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    element = elements[0]
                    passport_number = profile.get('id_number', '')
                    
                    if passport_number:
                        logger.info("여권번호 입력 중...")
                        self.browser.human_like_type(element, passport_number)
                        return True
            
            logger.error("여권번호 입력 필드를 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"여권 정보 입력 실패: {e}")
            return False
    
    def monitor_and_act(self):
        """캘린더 새로고침 기능이 포함된 향상된 모니터링"""
        logger.info("향상된 모니터링 시작...")
        
        # CalendarRefresher 초기화
        calendar_refresher = CalendarRefresher(
            self.driver, 
            self.browser  # StealthBrowser 인스턴스
        )
        
        # 먼저 캘린더가 로드될 때까지 대기
        if not self.wait_for_calendar():
            logger.error("캘린더를 찾을 수 없습니다")
            return
        
        logger.info("캘린더 감지됨. 모니터링 시작...")
        
        # 지속적인 모니터링 (5초마다 체크, 30초마다 새로고침)
        available_dates = calendar_refresher.continuous_monitor_with_refresh(
            check_interval=5,      # 5초마다 날짜 체크
            refresh_interval=30    # 30초마다 캘린더 새로고침
        )
        
        if available_dates:
            logger.info(f"🎉 {len(available_dates)}개의 예약 가능한 날짜 발견!")
            
            # 첫 번째 날짜 선택
            if self.select_date(available_dates[0]):
                logger.info("날짜 선택 완료")
                
                # 여권 정보 입력
                self.browser.human_like_delay(1, 2)
                
                if self.fill_passport_info():
                    logger.info("여권 정보 입력 완료")
                    
                    # 성공 알림
                    print("\n" + "="*50)
                    print("✅ 예약 가능한 날짜를 발견하여 선택했습니다!")
                    print("✅ 여권 정보 입력을 완료했습니다!")
                    print("나머지 단계를 수동으로 진행해주세요.")
                    print("="*50)
                else:
                    logger.warning("여권 정보 입력 실패")
            else:
                logger.warning("날짜 선택 실패")
        else:
            logger.info("모니터링 종료 (예약 가능한 날짜 없음)")
    
    def manual_refresh_mode(self):
        """수동 새로고침 모드 (대안)"""
        logger.info("수동 새로고침 모드 시작...")
        
        print("\n" + "="*50)
        print("📅 수동 새로고침 모드")
        print("1. F5 키를 눌러 페이지를 새로고침하세요")
        print("2. 또는 캘린더에서 다음달 → 이전달 클릭")
        print("3. 예약 가능한 날짜가 보이면 Enter 키")
        print("="*50)
        
        input("\n준비되면 Enter 키를 누르세요...")
        
        # 일반 모니터링 시작
        self.monitor_and_act()
    
    def run_automated_process(self):
        """자동화 프로세스 실행"""
        try:
            print("\n" + "="*50)
            print("3단계(날짜 선택) 페이지까지 수동으로 진행해주세요.")
            print("준비가 되면 Enter 키를 눌러주세요...")
            print("="*50)
            
            input()
            
            # 모드 선택
            print("\n" + "="*50)
            print("새로고침 모드를 선택하세요:")
            print("1. 🎫 티켓팅 모드 (9시 오픈용) - 정시 집중 공략")
            print("2. ⚡ 초고속 모드 - 1-3초 간격")
            print("3. 🔄 일반 모드 - 5-30초 간격")
            print("4. 🖱️ 수동 모드 - 직접 새로고침")
            print("="*50)
            
            choice = input("선택 (1-4, 기본값 2): ").strip() or "2"
            
            if choice == "1":
                self.run_ticketing_mode()
            elif choice == "2":
                self.run_ultra_fast_mode()
            elif choice == "3":
                self.monitor_and_act()
            else:
                self.manual_refresh_mode()
            
        except Exception as e:
            logger.error(f"자동화 프로세스 오류: {e}")
    
    def run_ultra_fast_mode(self):
        """초고속 모드 실행"""
        logger.info("🚀 초고속 모드 시작!")
        
        # 먼저 캘린더 확인
        if not self.wait_for_calendar():
            logger.error("캘린더를 찾을 수 없습니다")
            return
        
        print("\n" + "="*50)
        print("⚡ 초고속 모드 실행 중...")
        print("- 처음 30초: 버스트 모드 (1-2초 간격)")
        print("- 이후: 적응형 모드 (서버 상태에 따라 조절)")
        print("="*50)
        
        # 초고속 모니터링 실행
        available_dates = ultra_fast_calendar_monitor(
            self.driver,
            self.browser
        )
        
        if available_dates:
            logger.info(f"🎯 {len(available_dates)}개의 예약 가능한 날짜 발견!")
            
            # 첫 번째 날짜 선택
            if self.select_date(available_dates[0]):
                logger.info("날짜 선택 완료")
                
                # 여권 정보 입력
                self.browser.human_like_delay(1, 2)
                
                if self.fill_passport_info():
                    print("\n" + "="*50)
                    print("✅ 초고속 모드 성공!")
                    print("✅ 예약 가능한 날짜 선택 완료!")
                    print("✅ 여권 정보 입력 완료!")
                    print("나머지 단계를 수동으로 진행해주세요.")
                    print("="*50)
    
    def run_ticketing_mode(self):
        """티켓팅 모드 실행"""
        logger.info("🎫 티켓팅 모드 선택")
        
        # 티켓팅 자동화 실행
        ticketing_automation(self.driver, self.browser)


def main():
    """메인 실행 함수"""
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('g4k_automation_v2.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    automation = G4KHybridAutomationV2()
    
    try:
        # 1. 초기화
        if not automation.initialize():
            logger.error("초기화 실패")
            return
        
        # 2. 메인 페이지 로드
        if not automation.browser.safe_page_load(
            automation.driver, 
            "https://www.g4k.go.kr"
        ):
            logger.error("메인 페이지 로드 실패")
            return
        
        # 3. 로그인 대기
        if not automation.login_wait():
            logger.error("로그인 실패")
            return
        
        # 4. 자동화 프로세스 실행
        automation.run_automated_process()
        
    except Exception as e:
        logger.error(f"실행 중 오류: {e}")
    finally:
        input("\n종료하려면 Enter 키를 누르세요...")
        automation.browser.close()


if __name__ == "__main__":
    main()
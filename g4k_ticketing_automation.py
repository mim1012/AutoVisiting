#!/usr/bin/env python3
"""
G4K 티켓팅 전용 자동화 시스템
9시 오픈 전쟁을 위한 최적화 버전
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from stealth_browser import StealthBrowser
from profile_manager import ConfigManager
from ticketing_strategy import TicketingStrategy, G4KTicketingMode
from adaptive_calendar_refresher import AdaptiveCalendarRefresher
from optimized_ticketing_flow import OptimizedTicketingFlow, enhanced_ticketing_execution

logger = logging.getLogger(__name__)


class G4KTicketingAutomation:
    """G4K 티켓팅 전용 자동화"""
    
    def __init__(self):
        self.browser = StealthBrowser(use_debug_port=True)
        self.driver = None
        self.config_manager = ConfigManager()
        
    def initialize(self) -> bool:
        """초기화"""
        try:
            logger.info("🎫 G4K 티켓팅 시스템 초기화")
            self.driver = self.browser.create_driver()
            return True
        except Exception as e:
            logger.error(f"초기화 실패: {e}")
            return False
    
    def prepare_for_war(self):
        """전쟁 준비 - 로그인 및 대기 화면까지"""
        print("\n" + "="*60)
        print("🎫 G4K 예약 전쟁 준비")
        print("="*60)
        print("1️⃣ G4K 사이트에서 로그인하세요")
        print("2️⃣ 방문예약 → 주의사항 동의 → 서비스 선택")
        print("3️⃣ 날짜 선택 화면까지 진행")
        print("4️⃣ 준비 완료 후 Enter")
        print("="*60)
        
        # 메인 페이지 로드
        self.browser.safe_page_load(self.driver, "https://www.g4k.go.kr")
        
        input("\n✅ 준비 완료 시 Enter...")
        
        # 현재 URL 저장 (새로고침용)
        self.target_url = self.driver.current_url
        logger.info(f"대기 URL: {self.target_url}")
    
    def select_strategy(self) -> dict:
        """전략 선택"""
        print("\n" + "="*60)
        print("⚔️ 전투 전략 선택")
        print("="*60)
        print("1. 정시 공략 (9:00:00) - 기본")
        print("2. 사용자 지정 시간")
        print("3. 즉시 공략 (테스트/연습)")
        print("="*60)
        
        choice = input("선택 (1-3, 기본값 1): ").strip() or "1"
        
        if choice == "1":
            return {'mode': 'scheduled', 'hour': 9, 'minute': 0}
        elif choice == "2":
            hour = int(input("시간 (0-23): "))
            minute = int(input("분 (0-59): "))
            return {'mode': 'scheduled', 'hour': hour, 'minute': minute}
        else:
            return {'mode': 'immediate'}
    
    def execute_ticketing_war(self, strategy: dict):
        """티켓팅 전쟁 실행"""
        ticketing = G4KTicketingMode(self.driver, self.browser)
        
        if strategy['mode'] == 'scheduled':
            # 정시 공략
            target_time = datetime.now().replace(
                hour=strategy['hour'], 
                minute=strategy['minute'], 
                second=0, 
                microsecond=0
            )
            
            # 이미 지났으면 다음날
            if target_time < datetime.now():
                target_time += timedelta(days=1)
            
            print(f"\n⏰ 목표 시간: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 워밍업 및 카운트다운
            ticketing.strategy.pre_warming(target_time)
            ticketing.strategy.network_optimization()
            
            # 멀티탭 준비 (선택적)
            remaining = (target_time - datetime.now()).seconds
            if remaining > 60:
                print("\n📑 멀티탭 전략 준비 중...")
                ticketing.strategy.multi_tab_strategy(3)
            
            # 카운트다운
            ticketing.strategy.countdown_refresh(target_time)
            
        else:
            # 즉시 실행
            print("\n💥 즉시 공략 시작!")
            time.sleep(1)
        
        # 초고속 클릭 전략
        success = self._rapid_war_click()
        
        if success:
            self._handle_success()
        else:
            self._fallback_strategy()
    
    def _rapid_war_click(self) -> bool:
        """전투 클릭 - 최적화된 플로우 사용"""
        logger.info("⚔️ 전투 시작!")
        
        try:
            # 프로필에서 여권번호 가져오기
            profile = self.config_manager.profile_manager.get_active_profile()
            if not profile:
                logger.error("활성 프로필이 없습니다")
                return False
            
            passport_number = profile.get('id_number', '')
            if not passport_number:
                logger.error("여권번호가 설정되지 않았습니다")
                return False
            
            # 최적화된 플로우 실행
            success = enhanced_ticketing_execution(self.driver, passport_number)
            
            return success
            
        except Exception as e:
            logger.error(f"전투 실행 실패: {e}")
            return False
    
    def _handle_success(self):
        """성공 처리"""
        # 최적화된 플로우에서 이미 처리됨
        pass
    
    def _fill_passport(self) -> bool:
        """여권번호 빠른 입력"""
        try:
            profile = self.config_manager.profile_manager.get_active_profile()
            if not profile:
                return False
            
            passport_number = profile.get('id_number', '')
            if not passport_number:
                return False
            
            # 여권번호 필드 찾기
            passport_field = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    "input[name*='passport'], input[id*='passport'], input[placeholder*='여권']"
                ))
            )
            
            # 빠른 입력
            passport_field.clear()
            passport_field.send_keys(passport_number)
            
            return True
            
        except Exception as e:
            logger.error(f"여권번호 입력 실패: {e}")
            return False
    
    def _fallback_strategy(self):
        """실패 시 폴백 전략"""
        print("\n⚠️ 첫 시도 실패! 지속 공략 모드 전환...")
        
        # 적응형 새로고침으로 전환
        refresher = AdaptiveCalendarRefresher(self.driver, self.browser)
        
        # 30초간 버스트 모드
        dates = refresher.burst_mode(30)
        
        if dates:
            # 날짜 클릭
            self.browser.human_like_click(self.driver, dates[0]['element'])
            self._handle_success()
        else:
            print("\n😢 예약 가능한 날짜가 없습니다.")
            print("다음 기회를 노려보세요...")
    
    def run(self):
        """메인 실행"""
        try:
            # 1. 초기화
            if not self.initialize():
                return
            
            # 2. 전쟁 준비
            self.prepare_for_war()
            
            # 3. 전략 선택
            strategy = self.select_strategy()
            
            # 4. 전투 실행
            self.execute_ticketing_war(strategy)
            
        except Exception as e:
            logger.error(f"실행 중 오류: {e}")
        finally:
            input("\n종료하려면 Enter...")
            self.browser.close()


def main():
    """메인 함수"""
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('g4k_ticketing.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 배너
    print("\n" + "="*60)
    print("🎫 G4K 티켓팅 전용 시스템 v2.0 🎫")
    print("="*60)
    print("💡 9시 정각 예약 전쟁을 위한 최적화 버전")
    print("⚡ 0.05초의 차이가 승부를 가릅니다!")
    print("="*60)
    
    # 실행
    automation = G4KTicketingAutomation()
    automation.run()


if __name__ == "__main__":
    main()
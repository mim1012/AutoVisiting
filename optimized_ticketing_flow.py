#!/usr/bin/env python3
"""
최적화된 티켓팅 플로우
3단계 캘린더 → 날짜 클릭 → 4단계 여권번호 입력
"""

import time
import logging
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

logger = logging.getLogger(__name__)


class OptimizedTicketingFlow:
    """최적화된 티켓팅 플로우"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.quick_wait = WebDriverWait(driver, 2)
        
    def ultra_fast_calendar_click(self) -> bool:
        """초고속 캘린더 감지 및 클릭"""
        logger.info("⚡ 초고속 캘린더 감지 시작")
        
        # JavaScript 기반 초고속 감지
        calendar_script = """
        // 성공 플래그 초기화
        window.calendarClicked = false;
        window.clickedDate = null;
        
        // 초고속 감지 함수
        function ultraFastDetect() {
            // 다양한 캘린더 선택자
            const selectors = [
                'td.available:not(.disabled)',
                'td[data-handler="selectDay"]:not(.ui-state-disabled)',
                'td.selectable:not(.disabled)',
                '.calendar-day.available',
                'td:not(.disabled):not(.off)',
                '[data-available="true"]'
            ];
            
            for (let selector of selectors) {
                const dates = document.querySelectorAll(selector);
                
                for (let date of dates) {
                    // 숫자인지 확인 (1-31)
                    const text = date.textContent.trim();
                    if (/^[0-9]+$/.test(text)) {
                        const num = parseInt(text);
                        if (num >= 1 && num <= 31) {
                            // 클릭!
                            date.click();
                            window.calendarClicked = true;
                            window.clickedDate = num;
                            console.log('날짜 클릭 성공:', num);
                            return true;
                        }
                    }
                }
            }
            return false;
        }
        
        // 20ms 간격으로 초고속 체크
        const checkInterval = setInterval(() => {
            if (ultraFastDetect()) {
                clearInterval(checkInterval);
            }
        }, 20);
        
        // 10초 후 자동 중지
        setTimeout(() => {
            clearInterval(checkInterval);
            if (!window.calendarClicked) {
                console.log('타임아웃: 예약 가능한 날짜 없음');
            }
        }, 10000);
        """
        
        try:
            # 스크립트 실행
            self.driver.execute_script(calendar_script)
            
            # 결과 확인 (최대 10초)
            for i in range(500):  # 20ms * 500 = 10초
                try:
                    clicked = self.driver.execute_script("return window.calendarClicked || false")
                    if clicked:
                        date = self.driver.execute_script("return window.clickedDate")
                        logger.info(f"🎯 날짜 클릭 성공: {date}일")
                        return True
                except:
                    pass
                time.sleep(0.02)  # 20ms
                
            logger.warning("예약 가능한 날짜를 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"캘린더 클릭 중 오류: {e}")
            return False
    
    def wait_for_page_transition(self, timeout: int = 10) -> bool:
        """페이지 전환 대기"""
        logger.info("페이지 전환 대기 중...")
        
        try:
            # 현재 URL 저장
            current_url = self.driver.current_url
            
            # URL 변경 감지
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.current_url != current_url
            )
            
            logger.info(f"페이지 전환 감지: {self.driver.current_url}")
            
            # 페이지 로드 완료 대기
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            return True
            
        except TimeoutException:
            logger.warning("페이지 전환 타임아웃")
            return False
    
    def smart_passport_input(self, passport_number: str) -> bool:
        """스마트 여권번호 입력 (4단계 페이지)"""
        logger.info("🔍 4단계 페이지에서 여권번호 필드 찾기")
        
        # 여권번호 입력 필드 선택자들
        passport_selectors = [
            # ID 기반
            "#passportNo",
            "#passport_no",
            "#passport",
            
            # Name 속성
            "input[name='passportNo']",
            "input[name='passport_no']",
            "input[name='passport']",
            
            # 플레이스홀더
            "input[placeholder*='여권']",
            "input[placeholder*='passport']",
            
            # 클래스
            "input.passport-input",
            "input.passport-number",
            
            # 타입과 조합
            "input[type='text'][name*='passport']",
            "input[type='text'][id*='passport']",
            
            # 레이블 연관
            "input[aria-label*='여권']",
            
            # 일반적인 패턴
            "input[class*='passport']",
            "input[id*='passport']"
        ]
        
        # 여권번호 필드 찾기 시도
        for selector in passport_selectors:
            try:
                # 필드가 나타날 때까지 대기
                element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                # 입력 가능한지 확인
                if element.is_displayed() and element.is_enabled():
                    logger.info(f"✅ 여권번호 필드 발견: {selector}")
                    
                    # 기존 값 클리어
                    element.clear()
                    time.sleep(0.1)
                    
                    # JavaScript로 직접 입력 (더 빠름)
                    self.driver.execute_script(
                        "arguments[0].value = arguments[1]; "
                        "arguments[0].dispatchEvent(new Event('input', {bubbles: true})); "
                        "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                        element, passport_number
                    )
                    
                    logger.info(f"✅ 여권번호 입력 완료: {passport_number}")
                    
                    # 입력 확인
                    time.sleep(0.2)
                    entered_value = element.get_attribute('value')
                    if entered_value == passport_number:
                        return True
                    else:
                        logger.warning(f"입력값 불일치: {entered_value} != {passport_number}")
                        
            except TimeoutException:
                continue
            except Exception as e:
                logger.debug(f"선택자 {selector} 실패: {e}")
                continue
        
        logger.error("❌ 여권번호 입력 필드를 찾을 수 없습니다")
        return False
    
    def execute_optimized_flow(self, passport_number: str) -> bool:
        """최적화된 전체 플로우 실행"""
        logger.info("🚀 최적화된 티켓팅 플로우 시작")
        
        # 1단계: 초고속 캘린더 클릭
        if not self.ultra_fast_calendar_click():
            logger.error("캘린더 클릭 실패")
            return False
        
        # 2단계: 페이지 전환 대기
        if not self.wait_for_page_transition():
            logger.warning("페이지 전환 감지 실패. 계속 진행...")
            # 페이지 전환이 빠를 수 있으므로 계속 진행
        
        # 3단계: 잠시 대기 (페이지 렌더링)
        time.sleep(0.5)
        
        # 4단계: 여권번호 입력
        max_attempts = 5
        for attempt in range(max_attempts):
            if self.smart_passport_input(passport_number):
                logger.info("✅ 여권번호 입력 성공!")
                return True
            
            logger.info(f"재시도 {attempt + 1}/{max_attempts}")
            time.sleep(0.5)
        
        logger.error("❌ 여권번호 입력 최종 실패")
        return False
    
    def verify_step4_page(self) -> bool:
        """4단계 페이지 확인"""
        try:
            # 4단계 페이지 특징적인 요소들
            step4_indicators = [
                "h2:contains('개인정보')",
                "h3:contains('신청자 정보')",
                ".step-4",
                ".step.active:contains('4')",
                "div:contains('여권번호')"
            ]
            
            for indicator in step4_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        logger.info("✅ 4단계 페이지 확인됨")
                        return True
                except:
                    continue
                    
            # URL 확인
            if 'step=4' in self.driver.current_url or 'applicant' in self.driver.current_url:
                logger.info("✅ 4단계 페이지 확인됨 (URL)")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"4단계 페이지 확인 실패: {e}")
            return False


# 기존 자동화에 통합할 함수
def enhanced_ticketing_execution(driver, passport_number):
    """향상된 티켓팅 실행"""
    flow = OptimizedTicketingFlow(driver)
    
    # 전체 플로우 실행
    success = flow.execute_optimized_flow(passport_number)
    
    if success:
        print("\n" + "🎉" * 20)
        print("✅ 티켓팅 성공!")
        print("✅ 날짜 선택 완료!")
        print("✅ 여권번호 입력 완료!")
        print("⚡ 나머지 정보를 빠르게 입력하세요!")
        print("🎉" * 20)
    else:
        print("\n⚠️ 일부 단계에서 문제가 발생했습니다.")
        print("수동으로 진행해주세요.")
    
    return success
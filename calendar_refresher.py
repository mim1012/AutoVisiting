#!/usr/bin/env python3
"""
G4K 캘린더 새로고침 모듈
다음달/이전달 이동으로 캘린더 데이터 갱신
"""

import time
import random
import logging
from typing import Optional, List, Dict
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class CalendarRefresher:
    """캘린더 새로고침 및 날짜 감지 클래스"""
    
    def __init__(self, driver: webdriver.Chrome, stealth_browser=None):
        self.driver = driver
        self.stealth_browser = stealth_browser
        self.current_month = None
        self.refresh_count = 0
        
    def find_calendar_navigation(self) -> Dict[str, any]:
        """캘린더 네비게이션 버튼 찾기"""
        nav_buttons = {
            'prev': None,
            'next': None,
            'current_month': None
        }
        
        # 이전/다음 버튼 선택자들
        prev_selectors = [
            "a.ui-datepicker-prev",
            "button.prev-month",
            ".calendar-prev",
            "[aria-label*='이전']",
            "[title*='이전']",
            "button[class*='prev']",
            "a[class*='prev']",
            ".fc-prev-button",
            "[data-handler='prev']"
        ]
        
        next_selectors = [
            "a.ui-datepicker-next",
            "button.next-month",
            ".calendar-next",
            "[aria-label*='다음']",
            "[title*='다음']",
            "button[class*='next']",
            "a[class*='next']",
            ".fc-next-button",
            "[data-handler='next']"
        ]
        
        # 현재 월 표시 선택자들
        month_selectors = [
            ".ui-datepicker-title",
            ".calendar-title",
            ".calendar-month",
            ".month-year",
            "[class*='datepicker-title']",
            ".fc-toolbar-title"
        ]
        
        # 이전 버튼 찾기
        for selector in prev_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    nav_buttons['prev'] = elements[0]
                    logger.info(f"이전 버튼 발견: {selector}")
                    break
            except:
                continue
        
        # 다음 버튼 찾기
        for selector in next_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    nav_buttons['next'] = elements[0]
                    logger.info(f"다음 버튼 발견: {selector}")
                    break
            except:
                continue
        
        # 현재 월 찾기
        for selector in month_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    nav_buttons['current_month'] = elements[0]
                    self.current_month = elements[0].text
                    logger.info(f"현재 월: {self.current_month}")
                    break
            except:
                continue
        
        return nav_buttons
    
    def navigate_month(self, direction: str = 'next') -> bool:
        """월 이동"""
        try:
            nav_buttons = self.find_calendar_navigation()
            
            if direction == 'next' and nav_buttons['next']:
                logger.info("다음달로 이동")
                if self.stealth_browser:
                    self.stealth_browser.human_like_click(self.driver, nav_buttons['next'])
                else:
                    nav_buttons['next'].click()
                    
            elif direction == 'prev' and nav_buttons['prev']:
                logger.info("이전달로 이동")
                if self.stealth_browser:
                    self.stealth_browser.human_like_click(self.driver, nav_buttons['prev'])
                else:
                    nav_buttons['prev'].click()
            else:
                logger.warning(f"{direction} 버튼을 찾을 수 없습니다")
                return False
            
            # 이동 후 대기
            time.sleep(random.uniform(0.5, 1.0))
            
            # 새로운 월 확인
            new_nav = self.find_calendar_navigation()
            if new_nav['current_month']:
                new_month = new_nav['current_month'].text
                if new_month != self.current_month:
                    logger.info(f"월 변경됨: {self.current_month} → {new_month}")
                    self.current_month = new_month
                    return True
            
            return True
            
        except Exception as e:
            logger.error(f"월 이동 중 오류: {e}")
            return False
    
    def refresh_calendar_by_navigation(self) -> bool:
        """네비게이션을 통한 캘린더 새로고침"""
        try:
            logger.info("캘린더 새로고침 시작")
            self.refresh_count += 1
            
            # 1. 다음달로 이동
            if not self.navigate_month('next'):
                return False
            
            # 2. 잠시 대기 (AJAX 로딩)
            time.sleep(random.uniform(1.0, 2.0))
            
            # 3. 이전달로 돌아오기
            if not self.navigate_month('prev'):
                return False
            
            logger.info(f"캘린더 새로고침 완료 (횟수: {self.refresh_count})")
            return True
            
        except Exception as e:
            logger.error(f"캘린더 새로고침 실패: {e}")
            return False
    
    def find_available_dates_with_refresh(self, max_attempts: int = 3) -> List[Dict]:
        """새로고침하면서 예약 가능한 날짜 찾기"""
        available_dates = []
        
        for attempt in range(max_attempts):
            logger.info(f"날짜 찾기 시도 {attempt + 1}/{max_attempts}")
            
            # 현재 캘린더에서 날짜 찾기
            available_dates = self._find_available_dates()
            
            if available_dates:
                logger.info(f"{len(available_dates)}개의 예약 가능한 날짜 발견!")
                return available_dates
            
            # 날짜가 없으면 새로고침
            if attempt < max_attempts - 1:
                logger.info("예약 가능한 날짜 없음. 캘린더 새로고침...")
                if not self.refresh_calendar_by_navigation():
                    # 네비게이션 실패 시 페이지 새로고침 시도
                    self._refresh_by_page_reload()
                
                # 새로고침 후 대기
                time.sleep(random.uniform(2.0, 3.0))
        
        return available_dates
    
    def _find_available_dates(self) -> List[Dict]:
        """현재 캘린더에서 예약 가능한 날짜 찾기"""
        available_dates = []
        
        # 다양한 선택자 시도
        date_selectors = [
            # 활성화된 날짜
            "td.available:not(.disabled)",
            "td.selectable:not(.disabled)",
            "td[data-handler='selectDay']:not(.disabled)",
            
            # 클래스 기반
            ".calendar-day.available",
            ".day.available",
            ".date.available",
            
            # 속성 기반
            "td[class*='available']:not([class*='disabled'])",
            "td:not(.disabled):not(.unselectable):not(.off)",
            
            # jQuery UI datepicker
            ".ui-datepicker-calendar td:not(.ui-state-disabled)",
            
            # 커스텀 캘린더
            "[role='gridcell'][aria-disabled='false']",
            "[data-available='true']"
        ]
        
        for selector in date_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    try:
                        # 요소가 보이고 클릭 가능한지 확인
                        if element.is_displayed() and element.is_enabled():
                            date_text = element.text.strip()
                            
                            # 날짜 텍스트가 유효한지 확인 (1-31)
                            if date_text and date_text.isdigit():
                                date_num = int(date_text)
                                if 1 <= date_num <= 31:
                                    # 추가 속성 확인
                                    classes = element.get_attribute('class') or ''
                                    
                                    # 명확히 비활성화된 것은 제외
                                    if 'disabled' not in classes and 'off' not in classes:
                                        available_dates.append({
                                            'element': element,
                                            'date': date_text,
                                            'classes': classes,
                                            'selector': selector
                                        })
                                        
                    except Exception as e:
                        continue
                
                if available_dates:
                    logger.info(f"선택자 '{selector}'로 {len(available_dates)}개 날짜 발견")
                    break
                    
            except Exception as e:
                continue
        
        return available_dates
    
    def _refresh_by_page_reload(self):
        """페이지 새로고침으로 캘린더 갱신"""
        try:
            logger.info("페이지 새로고침 시도")
            current_url = self.driver.current_url
            self.driver.refresh()
            
            # 페이지 로드 대기
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 캘린더 다시 로드 대기
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"페이지 새로고침 실패: {e}")
    
    def continuous_monitor_with_refresh(self, check_interval: int = 5, refresh_interval: int = 30):
        """지속적인 모니터링 (주기적 새로고침 포함)"""
        last_refresh_time = time.time()
        monitoring = True
        
        while monitoring:
            try:
                # 새로고침 타이밍 체크
                current_time = time.time()
                if current_time - last_refresh_time > refresh_interval:
                    logger.info(f"{refresh_interval}초 경과. 캘린더 새로고침...")
                    self.refresh_calendar_by_navigation()
                    last_refresh_time = current_time
                
                # 예약 가능한 날짜 찾기
                available_dates = self._find_available_dates()
                
                if available_dates:
                    logger.info(f"🎉 {len(available_dates)}개의 예약 가능한 날짜 발견!")
                    return available_dates
                else:
                    logger.info(f"예약 가능한 날짜 없음. {check_interval}초 후 재확인...")
                
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("모니터링 중단")
                monitoring = False
                break
            except Exception as e:
                logger.error(f"모니터링 중 오류: {e}")
                time.sleep(check_interval)
        
        return []


# 개선된 자동화 클래스에 통합할 메서드
def enhanced_monitor_and_act(self):
    """캘린더 새로고침 기능이 추가된 모니터링"""
    logger.info("향상된 모니터링 시작...")
    
    # CalendarRefresher 초기화
    calendar_refresher = CalendarRefresher(
        self.driver, 
        self.browser  # StealthBrowser 인스턴스
    )
    
    # 지속적인 모니터링 (5초마다 체크, 30초마다 새로고침)
    available_dates = calendar_refresher.continuous_monitor_with_refresh(
        check_interval=5,
        refresh_interval=30
    )
    
    if available_dates:
        # 첫 번째 날짜 선택
        if self.select_date(available_dates[0]):
            logger.info("날짜 선택 완료")
            
            # 여권 정보 입력
            self.browser.human_like_delay(1, 2)
            if self.fill_passport_info():
                logger.info("✅ 예약 프로세스 완료!")
                return True
    
    return False
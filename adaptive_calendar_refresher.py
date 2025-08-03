#!/usr/bin/env python3
"""
적응형 캘린더 새로고침 모듈
서버 부하와 경쟁 상황을 고려한 지능형 새로고침
"""

import time
import random
import logging
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
from collections import deque
import statistics

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class ServerLoadAnalyzer:
    """서버 부하 분석 및 최적 타이밍 계산"""
    
    def __init__(self):
        self.response_times = deque(maxlen=20)  # 최근 20개 응답시간
        self.request_history = deque(maxlen=100)  # 최근 100개 요청 기록
        self.error_count = 0
        self.success_count = 0
        
    def record_request(self, response_time: float, success: bool = True):
        """요청 기록"""
        self.request_history.append({
            'timestamp': time.time(),
            'response_time': response_time,
            'success': success
        })
        
        if success:
            self.response_times.append(response_time)
            self.success_count += 1
        else:
            self.error_count += 1
    
    def get_optimal_interval(self) -> float:
        """최적 새로고침 간격 계산"""
        # 기본값
        base_interval = 3.0
        
        # 응답 시간 기반 조정
        if self.response_times:
            avg_response = statistics.mean(self.response_times)
            
            # 서버가 빠르면 간격 줄임
            if avg_response < 0.5:
                base_interval = 2.0
            elif avg_response < 1.0:
                base_interval = 2.5
            elif avg_response > 3.0:
                base_interval = 5.0
        
        # 에러율 기반 조정
        total_requests = self.success_count + self.error_count
        if total_requests > 10:
            error_rate = self.error_count / total_requests
            if error_rate > 0.2:  # 20% 이상 에러
                base_interval *= 1.5  # 간격 증가
        
        # 랜덤 요소 추가 (±20%)
        variation = base_interval * 0.2
        return base_interval + random.uniform(-variation, variation)
    
    def is_peak_time(self) -> bool:
        """피크 시간대 판단"""
        current_hour = datetime.now().hour
        # 오전 9-11시, 오후 2-4시를 피크타임으로 가정
        return (9 <= current_hour <= 11) or (14 <= current_hour <= 16)


class AdaptiveCalendarRefresher:
    """적응형 캘린더 새로고침 클래스"""
    
    def __init__(self, driver: webdriver.Chrome, stealth_browser=None):
        self.driver = driver
        self.stealth_browser = stealth_browser
        self.load_analyzer = ServerLoadAnalyzer()
        self.refresh_count = 0
        self.last_refresh_time = 0
        self.consecutive_empty_count = 0
        
        # 새로고침 전략 설정
        self.strategies = {
            'aggressive': {'min_interval': 1.5, 'max_interval': 3.0},
            'normal': {'min_interval': 2.5, 'max_interval': 5.0},
            'conservative': {'min_interval': 5.0, 'max_interval': 10.0}
        }
        self.current_strategy = 'normal'
        
    def smart_refresh(self) -> bool:
        """지능형 새로고침"""
        start_time = time.time()
        
        try:
            # 새로고침 방법 선택
            refresh_methods = [
                self._refresh_by_navigation,
                self._refresh_by_date_change,
                self._refresh_by_filter_toggle
            ]
            
            # 랜덤하게 방법 선택 (탐지 회피)
            method = random.choice(refresh_methods)
            success = method()
            
            # 응답 시간 기록
            response_time = time.time() - start_time
            self.load_analyzer.record_request(response_time, success)
            
            if success:
                self.refresh_count += 1
                self.last_refresh_time = time.time()
                logger.info(f"새로고침 성공 (방법: {method.__name__}, 시간: {response_time:.2f}초)")
            
            return success
            
        except Exception as e:
            logger.error(f"새로고침 실패: {e}")
            self.load_analyzer.record_request(0, False)
            return False
    
    def _refresh_by_navigation(self) -> bool:
        """월 네비게이션으로 새로고침"""
        try:
            # 다음달 버튼 찾기
            next_btn = self._find_navigation_button('next')
            if not next_btn:
                return False
            
            # 인간같은 클릭
            self._human_like_navigation(next_btn)
            
            # 짧은 대기
            time.sleep(random.uniform(0.8, 1.5))
            
            # 이전달로 돌아오기
            prev_btn = self._find_navigation_button('prev')
            if prev_btn:
                self._human_like_navigation(prev_btn)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"네비게이션 새로고침 실패: {e}")
            return False
    
    def _refresh_by_date_change(self) -> bool:
        """날짜 선택으로 새로고침 (더 자연스러움)"""
        try:
            # 현재 선택된 날짜 찾기
            current_date = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".ui-state-active, .selected-date, [class*='selected']"
            )
            
            if current_date:
                # 다른 날짜 클릭
                other_dates = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "td:not(.ui-state-disabled):not(.selected)"
                )
                
                if other_dates:
                    random_date = random.choice(other_dates[:5])  # 처음 5개 중 선택
                    self._human_like_click(random_date)
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    # 원래 날짜로 돌아오기
                    if current_date[0].is_displayed():
                        self._human_like_click(current_date[0])
                    
                    return True
                    
            return False
            
        except Exception:
            return False
    
    def _refresh_by_filter_toggle(self) -> bool:
        """필터나 옵션 토글로 새로고침"""
        try:
            # 시간대 필터, 센터 선택 등의 옵션 찾기
            filters = self.driver.find_elements(
                By.CSS_SELECTOR,
                "input[type='checkbox'], select.filter, .time-filter"
            )
            
            if filters:
                # 랜덤 필터 토글
                filter_element = random.choice(filters)
                
                if filter_element.get_attribute('type') == 'checkbox':
                    self._human_like_click(filter_element)
                    time.sleep(0.5)
                    self._human_like_click(filter_element)  # 다시 원상복구
                    
                return True
                
            return False
            
        except Exception:
            return False
    
    def _find_navigation_button(self, direction: str):
        """네비게이션 버튼 찾기"""
        selectors = {
            'next': [
                "a.ui-datepicker-next:not(.ui-state-disabled)",
                "button.next-month:not(:disabled)",
                "[aria-label*='다음']:not([disabled])",
                ".calendar-nav-next:not(.disabled)"
            ],
            'prev': [
                "a.ui-datepicker-prev:not(.ui-state-disabled)",
                "button.prev-month:not(:disabled)",
                "[aria-label*='이전']:not([disabled])",
                ".calendar-nav-prev:not(.disabled)"
            ]
        }
        
        for selector in selectors.get(direction, []):
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements and elements[0].is_displayed() and elements[0].is_enabled():
                return elements[0]
        
        return None
    
    def _human_like_navigation(self, element):
        """인간같은 네비게이션"""
        if self.stealth_browser:
            self.stealth_browser.human_like_click(self.driver, element)
        else:
            # 마우스 움직임 시뮬레이션
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            
            # 랜덤 시작점
            actions.move_by_offset(random.randint(100, 300), random.randint(100, 300))
            
            # 요소로 이동 (곡선 경로)
            for _ in range(random.randint(2, 4)):
                actions.move_by_offset(
                    random.randint(-50, 50),
                    random.randint(-50, 50)
                )
            
            actions.move_to_element(element)
            actions.pause(random.uniform(0.1, 0.3))
            actions.click()
            actions.perform()
    
    def _human_like_click(self, element):
        """인간같은 클릭"""
        if self.stealth_browser:
            self.stealth_browser.human_like_click(self.driver, element)
        else:
            element.click()
    
    def adaptive_monitor(self, initial_check_callback=None):
        """적응형 모니터링"""
        logger.info("적응형 모니터링 시작...")
        
        monitoring = True
        found_dates = []
        last_check_time = time.time()
        
        while monitoring:
            try:
                current_time = time.time()
                
                # 최적 간격 계산
                optimal_interval = self.load_analyzer.get_optimal_interval()
                
                # 전략 조정
                self._adjust_strategy()
                
                # 새로고침 타이밍 결정
                time_since_refresh = current_time - self.last_refresh_time
                min_interval = self.strategies[self.current_strategy]['min_interval']
                max_interval = self.strategies[self.current_strategy]['max_interval']
                
                # 동적 새로고침
                should_refresh = False
                
                if time_since_refresh > max_interval:
                    # 최대 간격 초과
                    should_refresh = True
                elif time_since_refresh > min_interval:
                    # 연속 빈 결과시 더 자주 새로고침
                    if self.consecutive_empty_count > 2:
                        should_refresh = True
                    # 피크 시간대는 더 공격적
                    elif self.load_analyzer.is_peak_time():
                        should_refresh = True
                
                if should_refresh:
                    logger.info(f"새로고침 실행 (전략: {self.current_strategy}, 간격: {time_since_refresh:.1f}초)")
                    self.smart_refresh()
                
                # 날짜 체크
                if initial_check_callback:
                    found_dates = initial_check_callback()
                    
                    if found_dates:
                        logger.info(f"🎯 {len(found_dates)}개 날짜 발견!")
                        self.consecutive_empty_count = 0
                        return found_dates
                    else:
                        self.consecutive_empty_count += 1
                
                # 대기
                sleep_time = max(0.5, optimal_interval - (time.time() - last_check_time))
                time.sleep(sleep_time)
                last_check_time = time.time()
                
            except KeyboardInterrupt:
                logger.info("사용자 중단")
                monitoring = False
                break
            except Exception as e:
                logger.error(f"모니터링 오류: {e}")
                time.sleep(2)
        
        return found_dates
    
    def _adjust_strategy(self):
        """전략 동적 조정"""
        # 에러율 기반
        total = self.load_analyzer.success_count + self.load_analyzer.error_count
        if total > 10:
            error_rate = self.load_analyzer.error_count / total
            
            if error_rate > 0.3:
                self.current_strategy = 'conservative'
                logger.warning("높은 에러율 감지. Conservative 모드로 전환")
            elif error_rate < 0.1 and self.consecutive_empty_count > 5:
                self.current_strategy = 'aggressive'
                logger.info("안정적 상태. Aggressive 모드로 전환")
            else:
                self.current_strategy = 'normal'
        
        # 시간대 기반
        if self.load_analyzer.is_peak_time():
            if self.current_strategy == 'conservative':
                self.current_strategy = 'normal'  # 피크시간에는 최소 normal
    
    def burst_mode(self, duration: int = 30):
        """버스트 모드 - 짧은 시간 집중 새로고침"""
        logger.info(f"⚡ 버스트 모드 시작 ({duration}초)")
        
        end_time = time.time() + duration
        burst_count = 0
        
        while time.time() < end_time:
            # 1-2초 간격으로 빠른 새로고침
            self.smart_refresh()
            burst_count += 1
            
            # 날짜 체크
            dates = self._quick_date_check()
            if dates:
                logger.info(f"버스트 모드에서 날짜 발견! (새로고침 {burst_count}회)")
                return dates
            
            time.sleep(random.uniform(1.0, 2.0))
        
        logger.info(f"버스트 모드 종료 (새로고침 {burst_count}회)")
        return []
    
    def _quick_date_check(self) -> List[Dict]:
        """빠른 날짜 체크 (간소화)"""
        try:
            # 가장 빠른 선택자만 사용
            elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "td.available:not(.disabled), td[data-handler='selectDay']:not(.ui-state-disabled)"
            )
            
            return [{'element': el, 'date': el.text} for el in elements if el.text.strip().isdigit()]
            
        except Exception:
            return []


# 메인 통합 함수
def ultra_fast_calendar_monitor(driver, stealth_browser=None):
    """초고속 캘린더 모니터링"""
    refresher = AdaptiveCalendarRefresher(driver, stealth_browser)
    
    # 초기 버스트 모드 (30초간 집중 공략)
    logger.info("초기 버스트 모드 실행...")
    dates = refresher.burst_mode(30)
    
    if not dates:
        # 적응형 모니터링으로 전환
        logger.info("적응형 모니터링으로 전환...")
        dates = refresher.adaptive_monitor(
            initial_check_callback=refresher._quick_date_check
        )
    
    return dates
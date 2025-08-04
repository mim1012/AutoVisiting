#!/usr/bin/env python3
"""
인간처럼 빠른 새로고침 전략
자연스러우면서도 초고속 반응
"""

import time
import random
import logging
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

logger = logging.getLogger(__name__)


class HumanLikeFastRefresher:
    """인간처럼 빠른 새로고침"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.last_action_time = 0
        self.action_count = 0
        self.burst_mode = False
        
        # 인간 행동 패턴
        self.human_patterns = {
            'anxious_clicker': {  # 조급한 클릭러 (대부분의 사용자)
                'min_interval': 0.8,
                'max_interval': 2.0,
                'burst_clicks': 3,
                'burst_interval': 0.3
            },
            'steady_refresher': {  # 일정한 새로고침
                'min_interval': 1.5,
                'max_interval': 3.0,
                'burst_clicks': 1,
                'burst_interval': 0.5
            },
            'panic_mode': {  # 패닉 모드 (9시 정각)
                'min_interval': 0.5,
                'max_interval': 1.0,
                'burst_clicks': 5,
                'burst_interval': 0.2
            }
        }
        
        # 현재 패턴 (시간대에 따라 변경)
        self.current_pattern = self._select_pattern()
    
    def _select_pattern(self) -> Dict:
        """시간대에 따른 패턴 선택"""
        from datetime import datetime
        now = datetime.now()
        
        # 9시 직전/직후 (8:59~9:01)
        if (now.hour == 8 and now.minute >= 59) or (now.hour == 9 and now.minute <= 1):
            logger.info("🔥 패닉 모드 활성화!")
            return self.human_patterns['panic_mode']
        
        # 일반 시간대
        elif random.random() < 0.7:  # 70%는 조급한 클릭러
            return self.human_patterns['anxious_clicker']
        else:
            return self.human_patterns['steady_refresher']
    
    def natural_fast_refresh(self) -> bool:
        """자연스럽지만 빠른 새로고침"""
        pattern = self.current_pattern
        
        # 버스트 모드 결정 (가끔 연속 클릭)
        if random.random() < 0.3:  # 30% 확률로 버스트
            self._burst_refresh(pattern)
        else:
            self._single_refresh(pattern)
        
        return True
    
    def _burst_refresh(self, pattern: Dict):
        """연속 빠른 새로고침 (인간의 조급함 모방)"""
        logger.info("💨 버스트 모드: 연속 새로고침")
        
        burst_count = random.randint(2, pattern['burst_clicks'])
        
        for i in range(burst_count):
            # 빠른 월 이동
            self._quick_month_navigation()
            
            # 짧은 간격
            time.sleep(pattern['burst_interval'] + random.uniform(-0.1, 0.1))
            
            # 가끔 실수 (너무 빨리 클릭)
            if random.random() < 0.1:
                logger.debug("실수 클릭 시뮬레이션")
                time.sleep(0.1)
    
    def _single_refresh(self, pattern: Dict):
        """단일 새로고침"""
        # 간격 계산 (자연스러운 변화)
        interval = random.uniform(pattern['min_interval'], pattern['max_interval'])
        
        # 행동 선택
        actions = [
            self._quick_month_navigation,     # 40% - 빠른 월 이동
            self._nervous_date_clicking,      # 30% - 신경질적 클릭
            self._impatient_scrolling,        # 20% - 조급한 스크롤
            self._rapid_filter_toggle         # 10% - 빠른 필터 토글
        ]
        
        weights = [0.4, 0.3, 0.2, 0.1]
        action = random.choices(actions, weights=weights)[0]
        
        # 실행
        action()
        
        # 자연스러운 대기
        time.sleep(interval)
    
    def _quick_month_navigation(self):
        """빠른 월 이동 (가장 일반적)"""
        try:
            # 다음 버튼 찾기 (캐싱으로 속도 향상)
            next_btn = self.driver.find_element(By.CSS_SELECTOR, 
                "a.ui-datepicker-next, button.next-month, [aria-label*='다음']"
            )
            
            # 빠른 클릭 (하지만 자연스럽게)
            self._human_quick_click(next_btn)
            
            # 매우 짧은 대기 (인간의 반응 속도)
            time.sleep(random.uniform(0.3, 0.5))
            
            # 즉시 이전으로
            prev_btn = self.driver.find_element(By.CSS_SELECTOR,
                "a.ui-datepicker-prev, button.prev-month, [aria-label*='이전']"
            )
            
            self._human_quick_click(prev_btn)
            
        except Exception as e:
            logger.debug(f"월 이동 실패: {e}")
    
    def _nervous_date_clicking(self):
        """신경질적인 날짜 클릭 (조급한 사용자)"""
        try:
            # 아무 날짜나 빠르게 클릭
            dates = self.driver.find_elements(By.CSS_SELECTOR, "td:not(.disabled)")
            
            if dates:
                # 2-3개 날짜 빠르게 클릭
                for _ in range(random.randint(2, 3)):
                    date = random.choice(dates)
                    self._human_quick_click(date)
                    time.sleep(random.uniform(0.2, 0.4))
                    
        except Exception as e:
            logger.debug(f"날짜 클릭 실패: {e}")
    
    def _impatient_scrolling(self):
        """조급한 스크롤 (캘린더 영역)"""
        try:
            # 캘린더 영역에서 빠른 스크롤
            calendar = self.driver.find_element(By.CSS_SELECTOR, 
                ".ui-datepicker, .calendar, [class*='calendar']"
            )
            
            # 위아래로 빠르게 스크롤
            self.driver.execute_script("""
                arguments[0].scrollTop += 50;
                setTimeout(() => arguments[0].scrollTop -= 50, 100);
            """, calendar)
            
        except Exception:
            pass
    
    def _rapid_filter_toggle(self):
        """빠른 필터 토글"""
        try:
            # 옵션이나 필터 빠르게 변경
            filters = self.driver.find_elements(By.CSS_SELECTOR, 
                "input[type='checkbox'], select"
            )
            
            if filters:
                filter_elem = random.choice(filters)
                self._human_quick_click(filter_elem)
                time.sleep(0.2)
                self._human_quick_click(filter_elem)  # 다시 원상복구
                
        except Exception:
            pass
    
    def _human_quick_click(self, element):
        """인간처럼 빠른 클릭"""
        actions = ActionChains(self.driver)
        
        # 약간의 오프셋 (정확한 중앙 클릭 X)
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        
        # 빠르지만 자연스러운 이동
        actions.move_to_element_with_offset(element, offset_x, offset_y)
        actions.pause(random.uniform(0.05, 0.1))  # 아주 짧은 멈춤
        actions.click()
        actions.perform()
    
    def adaptive_speed_control(self):
        """상황에 따른 속도 조절"""
        current_time = time.time()
        
        # 최근 10초간 액션 수 계산
        recent_actions = [t for t in self.action_history 
                         if current_time - t < 10]
        
        # 너무 많으면 잠시 쉬기 (봇 탐지 회피)
        if len(recent_actions) > 15:
            logger.warning("액션 과다 - 잠시 쉬기")
            time.sleep(random.uniform(2, 3))
            self.action_history.clear()
        
        # 너무 적으면 속도 높이기
        elif len(recent_actions) < 5:
            self.current_pattern = self.human_patterns['panic_mode']


class UltraFastHumanLikeStrategy:
    """초고속 인간형 전략"""
    
    def __init__(self, driver):
        self.driver = driver
        self.refresher = HumanLikeFastRefresher(driver)
        
    def execute_human_panic_mode(self):
        """인간의 패닉 모드 실행"""
        logger.info("😰 인간 패닉 모드 시작!")
        
        # 1. 초반 30초는 미친듯이
        end_time = time.time() + 30
        
        while time.time() < end_time:
            # 0.5~1초 간격으로 새로고침
            self.refresher._quick_month_navigation()
            
            # 20ms 간격으로 날짜 체크
            if self._ultra_fast_date_check():
                return True
                
            time.sleep(random.uniform(0.5, 1.0))
        
        # 2. 이후엔 조금 진정 (1~2초)
        logger.info("😤 조금 진정... 하지만 여전히 빠르게")
        
        while True:
            self.refresher.natural_fast_refresh()
            
            if self._ultra_fast_date_check():
                return True
                
            time.sleep(random.uniform(1.0, 2.0))
    
    def _ultra_fast_date_check(self) -> bool:
        """초고속 날짜 체크 (JavaScript)"""
        check_script = """
        var dates = document.querySelectorAll(
            'td.available:not(.disabled), ' +
            'td[data-handler="selectDay"]:not(.ui-state-disabled)'
        );
        
        if (dates.length > 0) {
            dates[0].click();
            return true;
        }
        return false;
        """
        
        try:
            return self.driver.execute_script(check_script)
        except:
            return False
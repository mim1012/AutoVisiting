#!/usr/bin/env python3
"""
G4K 티켓팅 전략 모듈
콘서트 예약 시스템의 전략을 G4K에 적용
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
from concurrent.futures import ThreadPoolExecutor
import queue

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class TicketingStrategy:
    """티켓팅 전략 클래스"""
    
    def __init__(self, driver: webdriver.Chrome, stealth_browser=None):
        self.driver = driver
        self.stealth_browser = stealth_browser
        self.success_queue = queue.Queue()
        
    def pre_warming(self, target_time: datetime):
        """사전 워밍업 - 서버 연결 최적화"""
        logger.info("🔥 사전 워밍업 시작")
        
        # 목표 시간 5분 전부터 준비
        warmup_start = target_time - timedelta(minutes=5)
        
        while datetime.now() < warmup_start:
            logger.info(f"워밍업 대기 중... {(warmup_start - datetime.now()).seconds}초 남음")
            time.sleep(10)
        
        logger.info("워밍업 단계 진입")
        
        # 1. DNS 프리페칭
        self._dns_prefetch()
        
        # 2. 연결 유지 (Keep-Alive)
        self._maintain_connection()
        
        # 3. 캐시 프리로드
        self._preload_resources()
        
        # 4. 서버 타이밍 동기화
        self._sync_server_time()
    
    def _dns_prefetch(self):
        """DNS 미리 조회"""
        try:
            # DNS 프리페칭 스크립트
            dns_script = """
            // DNS 프리페칭
            var link = document.createElement('link');
            link.rel = 'dns-prefetch';
            link.href = '//www.g4k.go.kr';
            document.head.appendChild(link);
            
            // 프리커넥트
            var preconnect = document.createElement('link');
            preconnect.rel = 'preconnect';
            preconnect.href = 'https://www.g4k.go.kr';
            document.head.appendChild(preconnect);
            """
            self.driver.execute_script(dns_script)
            logger.info("DNS 프리페칭 완료")
        except Exception as e:
            logger.error(f"DNS 프리페칭 실패: {e}")
    
    def _maintain_connection(self):
        """연결 유지 (페이지 새로고침 없이)"""
        try:
            # AJAX 핑으로 연결 유지
            ping_script = """
            fetch('/api/keepalive', {
                method: 'HEAD',
                cache: 'no-cache'
            }).catch(() => {});
            """
            
            # 30초마다 핑
            for _ in range(10):
                self.driver.execute_script(ping_script)
                time.sleep(30)
                
            logger.info("연결 유지 완료")
        except Exception as e:
            logger.error(f"연결 유지 실패: {e}")
    
    def _preload_resources(self):
        """리소스 미리 로드"""
        try:
            # 캘린더 관련 리소스 프리로드
            preload_script = """
            // 이미지 프리로드
            var images = ['/images/calendar.png', '/images/next.png', '/images/prev.png'];
            images.forEach(src => {
                var img = new Image();
                img.src = src;
            });
            
            // 스크립트 프리로드
            var scripts = document.querySelectorAll('script[src*="calendar"], script[src*="datepicker"]');
            scripts.forEach(script => {
                fetch(script.src).catch(() => {});
            });
            """
            self.driver.execute_script(preload_script)
            logger.info("리소스 프리로드 완료")
        except Exception as e:
            logger.error(f"리소스 프리로드 실패: {e}")
    
    def _sync_server_time(self):
        """서버 시간 동기화"""
        try:
            # 서버 시간 확인
            server_time_script = """
            return new Date().toISOString();
            """
            
            server_times = []
            for _ in range(5):
                server_time = self.driver.execute_script(server_time_script)
                server_times.append(server_time)
                time.sleep(0.2)
            
            logger.info(f"서버 시간 동기화: {server_times[-1]}")
            
        except Exception as e:
            logger.error(f"시간 동기화 실패: {e}")
    
    def countdown_refresh(self, target_time: datetime):
        """정시 새로고침 전략"""
        logger.info(f"⏰ 목표 시간: {target_time.strftime('%H:%M:%S')}")
        
        # 카운트다운
        while True:
            now = datetime.now()
            remaining = (target_time - now).total_seconds()
            
            if remaining <= 0:
                break
                
            if remaining > 60:
                logger.info(f"대기 중... {int(remaining//60)}분 {int(remaining%60)}초 남음")
                time.sleep(10)
            elif remaining > 10:
                logger.info(f"준비... {int(remaining)}초 남음")
                time.sleep(1)
            else:
                # 마지막 10초 정밀 카운트다운
                logger.info(f"🚀 {remaining:.1f}초!")
                time.sleep(0.1)
        
        # 정시 실행
        self._execute_at_exact_time()
    
    def _execute_at_exact_time(self):
        """정확한 시간에 실행"""
        logger.info("💥 실행!")
        
        # 다중 스레드로 동시 새로고침
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            # 전략 1: 페이지 새로고침
            futures.append(executor.submit(self._strategy_page_refresh))
            
            # 전략 2: 캘린더 네비게이션
            futures.append(executor.submit(self._strategy_calendar_nav))
            
            # 전략 3: AJAX 직접 호출
            futures.append(executor.submit(self._strategy_ajax_call))
            
            # 첫 번째 성공 대기
            for future in futures:
                try:
                    result = future.result(timeout=5)
                    if result:
                        logger.info("✅ 새로고침 성공!")
                        break
                except Exception as e:
                    logger.error(f"전략 실행 오류: {e}")
    
    def _strategy_page_refresh(self):
        """전략 1: 페이지 새로고침"""
        try:
            self.driver.refresh()
            time.sleep(0.5)
            return True
        except:
            return False
    
    def _strategy_calendar_nav(self):
        """전략 2: 캘린더 네비게이션"""
        try:
            # 다음달 버튼 찾아서 클릭
            next_btn = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-next")
            next_btn.click()
            time.sleep(0.2)
            
            # 이전달로 돌아오기
            prev_btn = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-prev")
            prev_btn.click()
            return True
        except:
            return False
    
    def _strategy_ajax_call(self):
        """전략 3: AJAX 직접 호출"""
        try:
            # 캘린더 데이터 직접 요청
            ajax_script = """
            $.ajax({
                url: '/api/calendar/available-dates',
                method: 'GET',
                cache: false,
                success: function(data) {
                    // 캘린더 업데이트 트리거
                    $(document).trigger('calendar:update', data);
                }
            });
            """
            self.driver.execute_script(ajax_script)
            return True
        except:
            return False
    
    def multi_tab_strategy(self, num_tabs: int = 3):
        """멀티탭 전략 - 여러 탭에서 동시 시도"""
        logger.info(f"🔄 멀티탭 전략 ({num_tabs}개 탭)")
        
        tabs = []
        original_tab = self.driver.current_window_handle
        
        # 새 탭 열기
        for i in range(num_tabs - 1):
            self.driver.execute_script("window.open('');")
            tabs.append(self.driver.window_handles[-1])
        
        # 각 탭에서 같은 페이지 로드
        current_url = self.driver.current_url
        for tab in tabs:
            self.driver.switch_to.window(tab)
            self.driver.get(current_url)
            time.sleep(0.5)
        
        # 원래 탭으로 돌아가기
        self.driver.switch_to.window(original_tab)
        
        return tabs
    
    def rapid_click_strategy(self):
        """초고속 클릭 전략"""
        logger.info("⚡ 초고속 클릭 모드")
        
        # 클릭 가능한 날짜 미리 찾기
        clickable_script = """
        var dates = [];
        document.querySelectorAll('td:not(.disabled)').forEach(function(td) {
            if (td.textContent.match(/^[0-9]+$/)) {
                dates.push({
                    text: td.textContent,
                    x: td.getBoundingClientRect().x + td.offsetWidth/2,
                    y: td.getBoundingClientRect().y + td.offsetHeight/2
                });
            }
        });
        return dates;
        """
        
        # 0.1초마다 체크하고 즉시 클릭
        for _ in range(50):  # 5초간
            try:
                dates = self.driver.execute_script(clickable_script)
                
                if dates:
                    # 첫 번째 가능한 날짜 즉시 클릭
                    first_date = dates[0]
                    
                    # JavaScript로 직접 클릭 (더 빠름)
                    click_script = f"""
                    document.elementFromPoint({first_date['x']}, {first_date['y']}).click();
                    """
                    self.driver.execute_script(click_script)
                    
                    logger.info(f"🎯 날짜 클릭 성공: {first_date['text']}일")
                    return True
                    
            except Exception as e:
                pass
            
            time.sleep(0.1)
        
        return False
    
    def network_optimization(self):
        """네트워크 최적화"""
        # 불필요한 리소스 차단
        block_script = """
        // 이미지 로딩 차단
        Object.defineProperty(HTMLImageElement.prototype, 'src', {
            set: function(url) {
                if (!url.includes('calendar') && !url.includes('important')) {
                    return;
                }
                this.setAttribute('src', url);
            }
        });
        
        // 폰트 로딩 차단
        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
            if (link.href.includes('font')) {
                link.remove();
            }
        });
        """
        
        try:
            self.driver.execute_script(block_script)
            logger.info("네트워크 최적화 완료")
        except:
            pass


class G4KTicketingMode:
    """G4K 티켓팅 모드"""
    
    def __init__(self, driver, stealth_browser=None):
        self.driver = driver
        self.stealth_browser = stealth_browser
        self.strategy = TicketingStrategy(driver, stealth_browser)
        
    def run_ticketing_mode(self, target_hour: int = 9, target_minute: int = 0):
        """티켓팅 모드 실행"""
        logger.info("🎫 G4K 티켓팅 모드 시작")
        
        # 목표 시간 설정
        now = datetime.now()
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        # 만약 이미 지났다면 다음날로
        if target_time < now:
            target_time += timedelta(days=1)
        
        logger.info(f"목표 시간: {target_time}")
        
        # 1단계: 사전 준비 (5분 전)
        self.strategy.pre_warming(target_time)
        
        # 2단계: 네트워크 최적화
        self.strategy.network_optimization()
        
        # 3단계: 멀티탭 준비 (선택적)
        if (target_time - datetime.now()).seconds > 60:
            self.strategy.multi_tab_strategy(3)
        
        # 4단계: 카운트다운 및 정시 실행
        self.strategy.countdown_refresh(target_time)
        
        # 5단계: 초고속 클릭
        success = self.strategy.rapid_click_strategy()
        
        if success:
            logger.info("🎉 티켓팅 성공!")
            return True
        else:
            logger.warning("티켓팅 실패. 일반 모드로 전환...")
            return False
    
    def practice_mode(self):
        """연습 모드 - 실제 시간 전 테스트"""
        logger.info("🎯 연습 모드 시작")
        
        # 30초 후를 목표로 연습
        target_time = datetime.now() + timedelta(seconds=30)
        
        logger.info(f"연습 목표 시간: {target_time.strftime('%H:%M:%S')}")
        
        # 축약된 워밍업
        logger.info("빠른 워밍업...")
        self.strategy._dns_prefetch()
        self.strategy._preload_resources()
        
        # 카운트다운
        self.strategy.countdown_refresh(target_time)
        
        # 테스트 클릭
        logger.info("테스트 완료!")


# 메인 통합 함수
def ticketing_automation(driver, stealth_browser=None):
    """티켓팅 자동화 메인 함수"""
    mode = G4KTicketingMode(driver, stealth_browser)
    
    print("\n" + "="*60)
    print("🎫 G4K 티켓팅 모드")
    print("="*60)
    print("1. 실전 모드 (9시 정각)")
    print("2. 커스텀 시간 설정")
    print("3. 연습 모드 (30초 후)")
    print("="*60)
    
    choice = input("선택 (1-3): ").strip()
    
    if choice == "1":
        mode.run_ticketing_mode(9, 0)
    elif choice == "2":
        hour = int(input("시간 (0-23): "))
        minute = int(input("분 (0-59): "))
        mode.run_ticketing_mode(hour, minute)
    else:
        mode.practice_mode()
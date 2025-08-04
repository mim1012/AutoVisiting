#!/usr/bin/env python3
"""
8명 동시 예약을 위한 멀티 프로필 티켓팅 시스템
캘린더 렉 극복 + 동시 다발 공격
"""

import asyncio
import threading
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import time
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import random
import os
import json

logger = logging.getLogger(__name__)


class MultiProfileTicketing:
    """8명 동시 예약 시스템"""
    
    def __init__(self, profiles: List[Dict]):
        self.profiles = profiles  # 8명의 프로필
        self.success_count = 0
        self.results = {}
        self.lock = threading.Lock()
        
        # 브라우저별 다른 전략
        self.strategies = [
            'aggressive',    # 공격적 (0.5초)
            'normal',        # 일반 (1초)
            'stealth',       # 은밀 (2초)
            'burst'          # 버스트 (0.2초 x 5)
        ]
        
    def create_browser_pool(self) -> List[webdriver.Chrome]:
        """8개 브라우저 풀 생성"""
        browsers = []
        
        for i, profile in enumerate(self.profiles):
            logger.info(f"브라우저 #{i+1} 생성 중...")
            
            # 각 브라우저마다 다른 설정
            options = uc.ChromeOptions()
            
            # 프로필별 독립 데이터 디렉토리
            profile_dir = f"./chrome_profiles/profile_{i}"
            os.makedirs(profile_dir, exist_ok=True)
            options.add_argument(f'--user-data-dir={profile_dir}')
            
            # 렉 감소 설정
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-web-security')
            
            # 리소스 차단 (속도 향상)
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values": {
                    "images": 2,      # 이미지 차단
                    "plugins": 2,     # 플러그인 차단
                    "popups": 2,      # 팝업 차단
                    "media_stream": 2,  # 미디어 차단
                }
            })
            
            # 위치 분산 (프록시)
            if i < 4:  # 절반은 프록시 사용
                proxy = self.get_proxy(i)
                if proxy:
                    options.add_argument(f'--proxy-server={proxy}')
            
            try:
                driver = uc.Chrome(options=options, version_main=120)
                browsers.append(driver)
            except Exception as e:
                logger.error(f"브라우저 #{i+1} 생성 실패: {e}")
        
        return browsers
    
    def get_proxy(self, index: int) -> Optional[str]:
        """프록시 서버 할당"""
        proxies = [
            "socks5://127.0.0.1:1080",  # 로컬 프록시
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            None  # 직접 연결
        ]
        return proxies[index % len(proxies)]
    
    async def parallel_calendar_attack(self, browsers: List[webdriver.Chrome]):
        """병렬 캘린더 공격"""
        logger.info("🚀 8개 브라우저 동시 공격 시작!")
        
        # 프로세스 풀로 CPU 코어 최대 활용
        with ProcessPoolExecutor(max_workers=8) as executor:
            futures = []
            
            for i, (browser, profile) in enumerate(zip(browsers, self.profiles)):
                # 각 브라우저마다 다른 전략
                strategy = self.strategies[i % len(self.strategies)]
                
                future = executor.submit(
                    self.single_browser_attack,
                    i,
                    browser,
                    profile,
                    strategy
                )
                futures.append(future)
            
            # 결과 수집
            for future in futures:
                try:
                    result = future.result()
                    if result['success']:
                        self.success_count += 1
                        logger.info(f"✅ 프로필 {result['profile_name']} 성공!")
                except Exception as e:
                    logger.error(f"프로세스 오류: {e}")
    
    def single_browser_attack(self, index: int, browser, profile: Dict, strategy: str):
        """단일 브라우저 공격"""
        result = {
            'profile_name': profile['name'],
            'success': False,
            'timestamp': None
        }
        
        try:
            # 1. 캘린더 페이지까지 이동 (이미 로그인된 상태 가정)
            logger.info(f"[{profile['name']}] 캘린더 공격 준비...")
            
            # 2. 전략별 실행
            if strategy == 'aggressive':
                success = self.aggressive_strategy(browser, profile)
            elif strategy == 'burst':
                success = self.burst_strategy(browser, profile)
            elif strategy == 'stealth':
                success = self.stealth_strategy(browser, profile)
            else:
                success = self.normal_strategy(browser, profile)
            
            result['success'] = success
            result['timestamp'] = time.time()
            
        except Exception as e:
            logger.error(f"[{profile['name']}] 오류: {e}")
        
        return result
    
    def aggressive_strategy(self, browser, profile: Dict) -> bool:
        """공격적 전략 - 최단 간격"""
        logger.info(f"[{profile['name']}] 공격적 전략 실행")
        
        # JavaScript로 초고속 실행
        attack_script = """
        // 렉 무시하고 강제 실행
        var attackInterval = setInterval(function() {
            // 캘린더 새로고침 시도
            try {
                // 다음달 버튼 강제 클릭
                var nextBtn = document.querySelector('.ui-datepicker-next');
                if (nextBtn) nextBtn.click();
                
                setTimeout(function() {
                    // 이전달 복귀
                    var prevBtn = document.querySelector('.ui-datepicker-prev');
                    if (prevBtn) prevBtn.click();
                }, 200);
            } catch(e) {}
            
            // 날짜 감지 및 클릭
            var dates = document.querySelectorAll('td.available:not(.disabled)');
            if (dates.length > 0) {
                dates[0].click();
                clearInterval(attackInterval);
                window.reservationSuccess = true;
            }
        }, 500);  // 0.5초마다
        
        // 30초 후 중단
        setTimeout(function() {
            clearInterval(attackInterval);
        }, 30000);
        """
        
        browser.execute_script(attack_script)
        
        # 결과 대기
        for _ in range(60):  # 30초 대기
            try:
                success = browser.execute_script("return window.reservationSuccess || false")
                if success:
                    return self.complete_reservation(browser, profile)
            except:
                pass
            time.sleep(0.5)
        
        return False
    
    def burst_strategy(self, browser, profile: Dict) -> bool:
        """버스트 전략 - 순간 폭발"""
        logger.info(f"[{profile['name']}] 버스트 전략 실행")
        
        for burst in range(3):  # 3번의 버스트
            logger.info(f"[{profile['name']}] 버스트 #{burst+1}")
            
            # 5연속 초고속 클릭
            for _ in range(5):
                try:
                    # 강제 새로고침
                    browser.execute_script("""
                        document.querySelector('.ui-datepicker-next')?.click();
                        setTimeout(() => {
                            document.querySelector('.ui-datepicker-prev')?.click();
                        }, 100);
                    """)
                    
                    # 즉시 날짜 체크
                    dates = browser.find_elements(By.CSS_SELECTOR, "td.available")
                    if dates:
                        dates[0].click()
                        return self.complete_reservation(browser, profile)
                    
                except:
                    pass
                
                time.sleep(0.2)  # 0.2초 간격
            
            # 버스트 후 잠시 쉬기
            time.sleep(2)
        
        return False
    
    def stealth_strategy(self, browser, profile: Dict) -> bool:
        """은밀한 전략 - 탐지 회피"""
        logger.info(f"[{profile['name']}] 은밀한 전략 실행")
        
        # 인간처럼 행동
        for _ in range(15):  # 30초간
            try:
                # 랜덤한 행동
                action = random.choice([
                    lambda: browser.execute_script("window.scrollBy(0, 50)"),
                    lambda: browser.find_element(By.TAG_NAME, "body").click(),
                    lambda: None  # 가만히 있기
                ])
                action()
                
                # 자연스러운 새로고침
                if random.random() < 0.3:
                    next_btn = browser.find_element(By.CSS_SELECTOR, ".ui-datepicker-next")
                    next_btn.click()
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    prev_btn = browser.find_element(By.CSS_SELECTOR, ".ui-datepicker-prev")
                    prev_btn.click()
                
                # 날짜 확인
                dates = browser.find_elements(By.CSS_SELECTOR, "td.available")
                if dates:
                    # 인간같은 고민
                    time.sleep(random.uniform(0.3, 0.8))
                    dates[0].click()
                    return self.complete_reservation(browser, profile)
                
            except:
                pass
            
            time.sleep(random.uniform(1.5, 2.5))
        
        return False
    
    def normal_strategy(self, browser, profile: Dict) -> bool:
        """일반 전략"""
        logger.info(f"[{profile['name']}] 일반 전략 실행")
        
        for _ in range(30):  # 30초간
            try:
                # 새로고침
                browser.refresh()
                time.sleep(0.5)
                
                # 날짜 찾기
                dates = browser.find_elements(By.CSS_SELECTOR, "td.available")
                if dates:
                    dates[0].click()
                    return self.complete_reservation(browser, profile)
                
            except:
                pass
            
            time.sleep(1.0)
        
        return False
    
    def complete_reservation(self, browser, profile: Dict) -> bool:
        """예약 완료 처리"""
        try:
            # 4단계로 이동 대기
            time.sleep(1.0)
            
            # 여권번호 입력
            passport_field = browser.find_element(By.CSS_SELECTOR, "input[name*='passport']")
            passport_field.clear()
            passport_field.send_keys(profile['id_number'])
            
            logger.info(f"✅ [{profile['name']}] 예약 완료!")
            return True
            
        except Exception as e:
            logger.error(f"[{profile['name']}] 예약 완료 실패: {e}")
            return False
    
    def run_multi_profile_attack(self):
        """8명 동시 예약 실행"""
        logger.info("="*60)
        logger.info("🎫 8명 동시 예약 시스템 시작!")
        logger.info("="*60)
        
        # 1. 브라우저 풀 생성
        browsers = self.create_browser_pool()
        logger.info(f"✅ {len(browsers)}개 브라우저 준비 완료")
        
        # 2. 각 브라우저에서 로그인 대기
        logger.info("\n⚠️  각 브라우저에서 로그인 후 캘린더 페이지까지 이동하세요!")
        input("준비 완료 시 Enter...")
        
        # 3. 동시 공격 실행
        asyncio.run(self.parallel_calendar_attack(browsers))
        
        # 4. 결과 보고
        logger.info("\n" + "="*60)
        logger.info(f"🏆 최종 결과: {self.success_count}/8명 성공")
        logger.info("="*60)
        
        # 5. 브라우저 정리
        for browser in browsers:
            try:
                browser.quit()
            except:
                pass


# 최적화된 캘린더 렉 극복 함수
def overcome_calendar_lag():
    """캘린더 렉 극복 전용 스크립트"""
    lag_buster_script = """
    // 렉 극복 스크립트
    (function() {
        // 1. 애니메이션 비활성화
        var style = document.createElement('style');
        style.innerHTML = '* { animation: none !important; transition: none !important; }';
        document.head.appendChild(style);
        
        // 2. 불필요한 이벤트 리스너 제거
        var elements = document.querySelectorAll('*');
        elements.forEach(function(el) {
            var clone = el.cloneNode(true);
            el.parentNode.replaceChild(clone, el);
        });
        
        // 3. 강제 렌더링 최적화
        document.body.style.transform = 'translateZ(0)';
        
        // 4. 가비지 컬렉션 강제
        if (window.gc) window.gc();
    })();
    """
    
    return lag_buster_script


# 실행 예시
def main():
    # 8명의 프로필 준비
    profiles = []
    for i in range(8):
        profiles.append({
            'name': f'사용자{i+1}',
            'id_number': f'M1234567{i}',
            'phone': f'010-1234-567{i}'
        })
    
    # 멀티 프로필 시스템 실행
    system = MultiProfileTicketing(profiles)
    system.run_multi_profile_attack()


if __name__ == "__main__":
    main()
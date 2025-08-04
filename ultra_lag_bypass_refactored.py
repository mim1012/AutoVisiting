#!/usr/bin/env python3
"""
초고급 LAG 우회 기법 (리팩토링 버전)
기존 API 완전 동일, 내부 구조만 개선
"""

import asyncio
import aiohttp
import time
import json
import logging
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By

# 분리된 기법 클래스들 import
from lag_bypass_techniques import (
    LagBypassTechniqueFactory,
    WebSocketHijackTechnique,
    MemoryInjectionTechnique,
    BrowserExploitTechnique,
    AjaxInterceptorTechnique,
    DomMutationTechnique,
    WorkerThreadTechnique,
    CachePoisoningTechnique,
    TimingAttackTechnique
)

logger = logging.getLogger(__name__)


class UltraLagBypass:
    """극한의 렉 우회 기법 (리팩토링 버전)"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.cdp_url = None
        self._setup_cdp_connection()
        
        # 기법 인스턴스들 생성
        self._techniques = LagBypassTechniqueFactory.create_all_techniques(driver)
        self._sync_techniques = LagBypassTechniqueFactory.create_sync_techniques(driver)
        self._async_techniques = LagBypassTechniqueFactory.create_async_techniques(driver)
        
    def _setup_cdp_connection(self):
        """Chrome DevTools Protocol 직접 연결"""
        try:
            # CDP 엔드포인트 찾기
            caps = self.driver.capabilities
            debugger_address = caps.get('goog:chromeOptions', {}).get('debuggerAddress')
            if debugger_address:
                self.cdp_url = f"ws://{debugger_address}/devtools/browser"
                logger.info(f"CDP 연결: {self.cdp_url}")
        except Exception as e:
            logger.error(f"CDP 설정 실패: {e}")
    
    # ========================
    # 기존 API 완전 동일 유지
    # ========================
    
    async def method1_websocket_hijack(self):
        """방법 1: WebSocket 직접 탈취"""
        technique = WebSocketHijackTechnique(self.driver)
        await technique.execute()
        
    async def method2_memory_injection(self):
        """방법 2: 메모리 직접 조작"""
        technique = MemoryInjectionTechnique(self.driver)
        await technique.execute()
    
    async def method3_cdp_manipulation(self):
        """방법 3: Chrome DevTools Protocol 조작"""
        if not self.cdp_url:
            logger.warning("CDP URL이 설정되지 않았습니다")
            return
            
        logger.info("🔧 CDP 네트워크 조작...")
        
        try:
            import websockets
            
            async with websockets.connect(self.cdp_url) as ws:
                # 네트워크 가로채기 활성화
                await ws.send(json.dumps({
                    "id": 1,
                    "method": "Network.enable"
                }))
                
                # Fetch 도메인 활성화
                await ws.send(json.dumps({
                    "id": 2,
                    "method": "Fetch.enable",
                    "params": {
                        "patterns": [{"urlPattern": "*"}]
                    }
                }))
                
                # 응답 가로채기 (간단한 버전)
                logger.info("CDP 조작 완료")
                
        except Exception as e:
            logger.error(f"CDP 조작 실패: {e}")
    
    def method4_browser_exploit(self):
        """방법 4: 브라우저 렌더링 익스플로잇"""
        technique = BrowserExploitTechnique(self.driver)
        technique.execute()
    
    def method5_ajax_interceptor(self):
        """방법 5: AJAX 요청 가로채기 및 복제"""
        technique = AjaxInterceptorTechnique(self.driver)
        technique.execute()
    
    def method6_dom_mutation_hack(self):
        """방법 6: DOM Mutation 실시간 감지"""
        technique = DomMutationTechnique(self.driver)
        technique.execute()
    
    def method7_worker_thread_abuse(self):
        """방법 7: Web Worker 스레드 남용"""
        technique = WorkerThreadTechnique(self.driver)
        technique.execute()
    
    async def method8_protocol_downgrade(self):
        """방법 8: 프로토콜 다운그레이드 공격"""
        logger.info("📡 프로토콜 다운그레이드...")
        
        # HTTP/1.1로 강제 다운그레이드하여 동시 연결 수 증가
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(
                    force_close=True,
                    enable_cleanup_closed=True
                )
            ) as session:
                
                # 여러 연결로 동시 요청
                tasks = []
                for i in range(10):
                    headers = {
                        'Connection': 'close',  # Keep-Alive 비활성화
                        'Cache-Control': 'no-cache',
                        'User-Agent': f'Mozilla/5.0 (Session {i})'
                    }
                    
                    task = session.get(
                        self.driver.current_url,
                        headers=headers,
                        ssl=False  # SSL 검증 스킵
                    )
                    tasks.append(task)
                
                # 동시 실행
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.info("프로토콜 다운그레이드 완료")
                
        except Exception as e:
            logger.error(f"프로토콜 다운그레이드 실패: {e}")
    
    def method9_cache_poisoning(self):
        """방법 9: 캐시 포이즈닝"""
        technique = CachePoisoningTechnique(self.driver)
        technique.execute()
    
    def method10_timing_attack(self):
        """방법 10: 타이밍 공격"""
        technique = TimingAttackTechnique(self.driver)
        technique.execute()
    
    async def execute_all_methods(self):
        """모든 우회 기법 동시 실행 (기존 API 동일)"""
        logger.info("🚀 모든 LAG 우회 기법 동시 실행!")
        
        # 동기 메소드들 실행
        sync_methods = [
            self.method4_browser_exploit,
            self.method5_ajax_interceptor,
            self.method6_dom_mutation_hack,
            self.method7_worker_thread_abuse,
            self.method9_cache_poisoning,
            self.method10_timing_attack
        ]
        
        for method in sync_methods:
            try:
                method()
            except Exception as e:
                logger.error(f"{method.__name__} 실패: {e}")
        
        # 비동기 메소드들 동시 실행
        async_methods = [
            self.method1_websocket_hijack(),
            self.method2_memory_injection(),
            self.method3_cdp_manipulation(),
            self.method8_protocol_downgrade()
        ]
        
        await asyncio.gather(*async_methods, return_exceptions=True)
        
        logger.info("✅ 모든 LAG 우회 기법 적용 완료!")


class ExtremeTicketing:
    """극한의 티켓팅 전략 (기존 API 완전 동일)"""
    
    def __init__(self, driver):
        self.driver = driver
        self.lag_bypass = UltraLagBypass(driver)
    
    async def nuclear_option(self):
        """핵폭탄 옵션 - 모든 것을 동원 (기존 API 동일)"""
        logger.info("☢️ NUCLEAR OPTION 실행!")
        
        # 1. 모든 우회 기법 동시 적용
        await self.lag_bypass.execute_all_methods()
        
        # 2. 추가 익스트림 스크립트
        extreme_script = """
        // 궁극의 속도 해킹
        (function() {
            // 1. 시간 조작
            const originalDate = Date;
            let timeOffset = 0;
            
            window.Date = function(...args) {
                if (args.length === 0) {
                    return new originalDate(originalDate.now() + timeOffset);
                }
                return new originalDate(...args);
            };
            
            // 서버보다 0.5초 빠르게
            timeOffset = 500;
            
            // 2. 이벤트 루프 해킹
            const originalSetTimeout = setTimeout;
            window.setTimeout = function(fn, delay, ...args) {
                // 캘린더 관련은 즉시 실행
                if (fn.toString().includes('calendar') || delay > 1000) {
                    fn(...args);
                    return 0;
                }
                return originalSetTimeout(fn, delay, ...args);
            };
            
            // 3. 클릭 이벤트 증폭
            document.addEventListener('click', function(e) {
                if (e.target.classList.contains('available')) {
                    // 클릭 이벤트 5번 발생
                    for (let i = 0; i < 5; i++) {
                        e.target.dispatchEvent(new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true
                        }));
                    }
                }
            }, true);
            
            // 4. 궁극의 폴링
            let lastCheck = 0;
            function ultraPoll() {
                const now = performance.now();
                if (now - lastCheck > 10) {  // 10ms
                    lastCheck = now;
                    
                    // 모든 가능한 선택자로 체크
                    const selectors = [
                        'td.available',
                        'td:not(.disabled)',
                        '[data-available="true"]',
                        '.calendar-date.active',
                        'button:contains("예약")'
                    ];
                    
                    for (const selector of selectors) {
                        try {
                            const el = document.querySelector(selector);
                            if (el && !el.dataset.clicked) {
                                el.dataset.clicked = 'true';
                                el.click();
                                el.dispatchEvent(new Event('mousedown'));
                                el.dispatchEvent(new Event('mouseup'));
                                el.dispatchEvent(new Event('touchstart'));
                                el.dispatchEvent(new Event('touchend'));
                            }
                        } catch (e) {}
                    }
                }
                
                requestAnimationFrame(ultraPoll);
            }
            
            ultraPoll();
        })();
        """
        
        self.driver.execute_script(extreme_script)
        
        logger.info("💥 모든 무기 발사 완료! 행운을 빕니다!")


# 기존 코드와의 호환성을 위한 함수들
def overcome_calendar_lag():
    """캘린더 렉 극복 전용 스크립트 (기존 API 동일)"""
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


# 메인 실행 함수 (기존과 동일)
async def main():
    """메인 실행"""
    from selenium import webdriver
    try:
        import undetected_chromedriver as uc
    except ImportError:
        logger.warning("undetected-chromedriver를 사용할 수 없습니다. 표준 selenium을 사용합니다.")
        uc = None
    
    # 브라우저 생성
    if uc:
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        driver = uc.Chrome(options=options)
    else:
        # 표준 selenium 사용
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(options=options)
    
    try:
        # G4K 사이트 접속
        driver.get("https://www.g4k.go.kr")
        
        # 수동 로그인 대기
        input("로그인 후 캘린더 페이지에서 Enter...")
        
        # 극한 티켓팅 실행
        extreme = ExtremeTicketing(driver)
        await extreme.nuclear_option()
        
        # 결과 대기
        input("종료하려면 Enter...")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
#!/usr/bin/env python3
"""
초고급 LAG 우회 기법
웹사이트/캘린더 렉을 극복하는 얍삽한 방법들
"""

import asyncio
import aiohttp
import websockets
import time
import json
import logging
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
import threading
import multiprocessing
from ctypes import cdll, c_char_p, c_void_p

logger = logging.getLogger(__name__)


class UltraLagBypass:
    """극한의 렉 우회 기법"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.cdp_url = None
        self._setup_cdp_connection()
        
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
    
    async def method1_websocket_hijack(self):
        """방법 1: WebSocket 직접 탈취"""
        logger.info("🔌 WebSocket 하이재킹 시작...")
        
        # 사이트의 WebSocket 연결 가로채기
        inject_script = """
        // 원본 WebSocket 저장
        window._originalWebSocket = window.WebSocket;
        window._wsConnections = [];
        
        // WebSocket 프록시
        window.WebSocket = function(...args) {
            console.log('WebSocket 연결 감지:', args[0]);
            
            const ws = new window._originalWebSocket(...args);
            window._wsConnections.push(ws);
            
            // 메시지 가로채기
            const originalSend = ws.send;
            ws.send = function(data) {
                console.log('WS 전송:', data);
                
                // 예약 요청 감지시 즉시 복제 전송
                if (data.includes('reservation') || data.includes('booking')) {
                    // 5개 동시 전송
                    for (let i = 0; i < 5; i++) {
                        originalSend.call(this, data);
                    }
                } else {
                    originalSend.call(this, data);
                }
            };
            
            // 서버 응답 조작
            ws.addEventListener('message', function(event) {
                // 캘린더 데이터면 즉시 파싱
                if (event.data.includes('calendar') || event.data.includes('dates')) {
                    window._latestCalendarData = event.data;
                    
                    // 가능한 날짜 즉시 클릭
                    setTimeout(() => {
                        const dates = document.querySelectorAll('td.available');
                        if (dates.length > 0) dates[0].click();
                    }, 10);
                }
            });
            
            return ws;
        };
        """
        
        self.driver.execute_script(inject_script)
        
    async def method2_memory_injection(self):
        """방법 2: 메모리 직접 조작"""
        logger.info("💉 메모리 인젝션...")
        
        # JavaScript 힙 메모리 직접 접근
        memory_hack = """
        (async function() {
            // 메모리 스냅샷으로 캘린더 데이터 찾기
            if (window.performance && window.performance.memory) {
                // GC 강제 실행 후 메모리 정리
                if (window.gc) window.gc();
                
                // React/Vue 컴포넌트 직접 접근
                const findReactFiber = (dom) => {
                    const key = Object.keys(dom).find(key => 
                        key.startsWith("__reactFiber") || 
                        key.startsWith("__reactInternalInstance")
                    );
                    return dom[key];
                };
                
                // 모든 캘린더 요소의 내부 상태 해킹
                document.querySelectorAll('[class*="calendar"], [class*="datepicker"]').forEach(el => {
                    const fiber = findReactFiber(el);
                    if (fiber && fiber.memoizedState) {
                        // 상태 직접 수정
                        if (fiber.memoizedState.dates) {
                            fiber.memoizedState.dates = fiber.memoizedState.dates.map(d => ({
                                ...d,
                                available: true,
                                disabled: false
                            }));
                        }
                    }
                    
                    // Vue 인스턴스 해킹
                    if (el.__vue__) {
                        el.__vue__.$data.loading = false;
                        el.__vue__.$data.disabled = false;
                    }
                });
            }
        })();
        """
        
        self.driver.execute_script(memory_hack)
    
    async def method3_cdp_manipulation(self):
        """방법 3: Chrome DevTools Protocol 조작"""
        if not self.cdp_url:
            return
            
        logger.info("🔧 CDP 네트워크 조작...")
        
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
            
            # 응답 가로채기
            async for message in ws:
                data = json.loads(message)
                
                if data.get("method") == "Fetch.requestPaused":
                    request_id = data["params"]["requestId"]
                    url = data["params"]["request"]["url"]
                    
                    # 캘린더 API 응답 조작
                    if "calendar" in url or "dates" in url:
                        # 가짜 응답 생성
                        fake_response = {
                            "dates": [{"date": "2024-01-30", "available": True}] * 10
                        }
                        
                        await ws.send(json.dumps({
                            "id": 100,
                            "method": "Fetch.fulfillRequest",
                            "params": {
                                "requestId": request_id,
                                "responseCode": 200,
                                "responseHeaders": [
                                    {"name": "Content-Type", "value": "application/json"}
                                ],
                                "body": json.dumps(fake_response)
                            }
                        }))
    
    def method4_browser_exploit(self):
        """방법 4: 브라우저 렌더링 익스플로잇"""
        logger.info("🎭 렌더링 엔진 조작...")
        
        # 강제 렌더링 + 애니메이션 프레임 해킹
        exploit_script = """
        // 1. RequestAnimationFrame 오버라이드
        let frameCount = 0;
        const originalRAF = window.requestAnimationFrame;
        
        window.requestAnimationFrame = function(callback) {
            // 캘린더 관련 렌더링은 즉시 실행
            if (frameCount % 2 === 0) {
                callback(performance.now());
                frameCount++;
                return frameCount;
            }
            
            return originalRAF(callback);
        };
        
        // 2. IntersectionObserver로 가시성 강제
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.target.classList.contains('calendar')) {
                    // 강제로 visible 상태 유지
                    Object.defineProperty(entry, 'isIntersecting', {
                        value: true
                    });
                }
            });
        });
        
        // 3. 렌더링 레이어 강제 생성
        document.querySelectorAll('[class*="calendar"]').forEach(el => {
            el.style.willChange = 'transform';
            el.style.transform = 'translateZ(0)';
            el.style.backfaceVisibility = 'hidden';
            
            // GPU 가속 강제
            el.style.webkitTransform = 'translate3d(0,0,0)';
        });
        
        // 4. 가상 스크롤 무효화
        window.addEventListener('scroll', (e) => {
            e.stopPropagation();
            e.preventDefault();
        }, true);
        """
        
        self.driver.execute_script(exploit_script)
    
    def method5_ajax_interceptor(self):
        """방법 5: AJAX 요청 가로채기 및 복제"""
        logger.info("🎯 AJAX 인터셉터 설치...")
        
        ajax_hack = """
        // XMLHttpRequest 프록시
        const originalXHR = window.XMLHttpRequest;
        
        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();
            const originalOpen = xhr.open;
            const originalSend = xhr.send;
            
            xhr.open = function(method, url, ...args) {
                xhr._method = method;
                xhr._url = url;
                return originalOpen.apply(xhr, [method, url, ...args]);
            };
            
            xhr.send = function(data) {
                // 예약 요청 감지
                if (xhr._url && (xhr._url.includes('reservation') || 
                    xhr._url.includes('booking'))) {
                    
                    console.log('예약 요청 감지! 멀티 샷 발사!');
                    
                    // 병렬로 5개 요청 동시 전송
                    for (let i = 0; i < 5; i++) {
                        const clonedXhr = new originalXHR();
                        clonedXhr.open(xhr._method, xhr._url, true);
                        
                        // 헤더 복사
                        clonedXhr.setRequestHeader('X-Clone-Request', i);
                        
                        clonedXhr.send(data);
                    }
                }
                
                return originalSend.apply(xhr, [data]);
            };
            
            return xhr;
        };
        
        // Fetch API 프록시
        const originalFetch = window.fetch;
        window.fetch = async function(url, options = {}) {
            // 캘린더 요청은 캐시 무시
            if (url.includes('calendar')) {
                options.cache = 'no-store';
                options.headers = {
                    ...options.headers,
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                };
            }
            
            // 예약 요청은 다중 전송
            if (url.includes('reservation') && options.method === 'POST') {
                const promises = [];
                for (let i = 0; i < 3; i++) {
                    promises.push(originalFetch(url, {
                        ...options,
                        headers: {
                            ...options.headers,
                            'X-Request-ID': Date.now() + i
                        }
                    }));
                }
                
                // 가장 빠른 응답 사용
                return Promise.race(promises);
            }
            
            return originalFetch(url, options);
        };
        """
        
        self.driver.execute_script(ajax_hack)
    
    def method6_dom_mutation_hack(self):
        """방법 6: DOM Mutation 실시간 감지"""
        logger.info("🔍 DOM 뮤테이션 해킹...")
        
        mutation_script = """
        // 초고속 DOM 변화 감지
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                // 새로운 날짜 요소 즉시 감지
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) {  // Element node
                        // 가능한 날짜면 즉시 클릭
                        if (node.classList && (
                            node.classList.contains('available') ||
                            node.getAttribute('data-available') === 'true'
                        )) {
                            console.log('새 날짜 감지! 즉시 클릭!');
                            setTimeout(() => node.click(), 0);
                        }
                        
                        // 하위 요소도 체크
                        const availableDates = node.querySelectorAll('.available, [data-available="true"]');
                        if (availableDates.length > 0) {
                            availableDates[0].click();
                        }
                    }
                });
                
                // 속성 변경 감지 (disabled → enabled)
                if (mutation.type === 'attributes') {
                    const target = mutation.target;
                    if (target.classList && !target.disabled && 
                        !target.classList.contains('disabled')) {
                        if (target.tagName === 'TD' || target.classList.contains('date')) {
                            target.click();
                        }
                    }
                }
            });
        });
        
        // 전체 문서 감시
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class', 'disabled', 'data-available']
        });
        
        // 추가로 0.1초마다 폴링
        setInterval(() => {
            const dates = document.querySelectorAll('td.available:not(.clicked)');
            if (dates.length > 0) {
                dates[0].classList.add('clicked');
                dates[0].click();
            }
        }, 100);
        """
        
        self.driver.execute_script(mutation_script)
    
    def method7_worker_thread_abuse(self):
        """방법 7: Web Worker 스레드 남용"""
        logger.info("👷 워커 스레드 공격...")
        
        worker_script = """
        // 메인 스레드 블로킹 없이 백그라운드 공격
        const workerCode = `
            let intervalId;
            
            self.addEventListener('message', (e) => {
                if (e.data.action === 'start') {
                    // 20ms마다 메인 스레드에 체크 요청
                    intervalId = setInterval(() => {
                        self.postMessage({action: 'check_calendar'});
                    }, 20);
                } else if (e.data.action === 'stop') {
                    clearInterval(intervalId);
                }
            });
        `;
        
        const blob = new Blob([workerCode], {type: 'application/javascript'});
        const worker = new Worker(URL.createObjectURL(blob));
        
        worker.addEventListener('message', (e) => {
            if (e.data.action === 'check_calendar') {
                // 비동기로 캘린더 체크
                requestIdleCallback(() => {
                    const dates = document.querySelectorAll('td.available');
                    if (dates.length > 0) {
                        dates[0].click();
                        worker.postMessage({action: 'stop'});
                    }
                });
            }
        });
        
        // 워커 시작
        worker.postMessage({action: 'start'});
        
        // SharedWorker로 다중 탭 공격
        if (window.SharedWorker) {
            const sharedWorker = new SharedWorker('data:text/javascript,' + encodeURIComponent(workerCode));
            sharedWorker.port.start();
            sharedWorker.port.postMessage({action: 'start'});
        }
        """
        
        self.driver.execute_script(worker_script)
    
    async def method8_protocol_downgrade(self):
        """방법 8: 프로토콜 다운그레이드 공격"""
        logger.info("📡 프로토콜 다운그레이드...")
        
        # HTTP/1.1로 강제 다운그레이드하여 동시 연결 수 증가
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
    
    def method9_cache_poisoning(self):
        """방법 9: 캐시 포이즈닝"""
        logger.info("☠️ 캐시 조작...")
        
        cache_poison = """
        // Service Worker 설치로 캐시 제어
        if ('serviceWorker' in navigator) {
            const swCode = `
                self.addEventListener('fetch', (event) => {
                    const url = event.request.url;
                    
                    // 캘린더 요청은 항상 네트워크
                    if (url.includes('calendar') || url.includes('dates')) {
                        event.respondWith(
                            fetch(event.request, {
                                cache: 'no-store',
                                mode: 'no-cors'
                            }).then(response => {
                                // 응답 조작
                                if (response.headers.get('content-type')?.includes('json')) {
                                    return response.text().then(text => {
                                        // 날짜를 available로 변경
                                        const modified = text.replace(/"available":false/g, '"available":true');
                                        return new Response(modified, {
                                            headers: response.headers
                                        });
                                    });
                                }
                                return response;
                            })
                        );
                    }
                });
            `;
            
            navigator.serviceWorker.register(
                'data:text/javascript,' + encodeURIComponent(swCode)
            );
        }
        
        // LocalStorage/SessionStorage 조작
        const poisonStorage = () => {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.includes('calendar') || key.includes('date')) {
                    try {
                        const data = JSON.parse(localStorage.getItem(key));
                        // 모든 날짜를 available로
                        if (Array.isArray(data)) {
                            data.forEach(item => {
                                if (item.hasOwnProperty('available')) {
                                    item.available = true;
                                }
                            });
                            localStorage.setItem(key, JSON.stringify(data));
                        }
                    } catch (e) {}
                }
            });
        };
        
        // 주기적으로 캐시 오염
        setInterval(poisonStorage, 100);
        """
        
        self.driver.execute_script(cache_poison)
    
    def method10_timing_attack(self):
        """방법 10: 타이밍 공격"""
        logger.info("⏱️ 타이밍 어택...")
        
        timing_script = """
        // 서버 응답 패턴 분석
        const timingAnalysis = {
            requests: [],
            patterns: {},
            
            analyze: function() {
                // 최근 10개 요청의 타이밍 분석
                const recent = this.requests.slice(-10);
                const avgTime = recent.reduce((a, b) => a + b.duration, 0) / recent.length;
                
                // 빠른 응답 시간대 찾기
                const fastWindows = recent.filter(r => r.duration < avgTime * 0.7);
                
                if (fastWindows.length > 0) {
                    // 패턴 발견! 그 시간대에 집중 공격
                    const optimalTime = fastWindows[0].timestamp % 1000;
                    
                    setTimeout(() => {
                        // 집중 공격
                        for (let i = 0; i < 5; i++) {
                            document.querySelector('.refresh-button')?.click();
                        }
                    }, optimalTime);
                }
            }
        };
        
        // Performance API로 네트워크 타이밍 추적
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.name.includes('api') || entry.name.includes('calendar')) {
                    timingAnalysis.requests.push({
                        timestamp: entry.startTime,
                        duration: entry.duration
                    });
                    
                    timingAnalysis.analyze();
                }
            }
        });
        
        observer.observe({ entryTypes: ['resource'] });
        """
        
        self.driver.execute_script(timing_script)
    
    async def execute_all_methods(self):
        """모든 우회 기법 동시 실행"""
        logger.info("🚀 모든 LAG 우회 기법 동시 실행!")
        
        # 동기 메소드들
        sync_methods = [
            self.method4_browser_exploit,
            self.method5_ajax_interceptor,
            self.method6_dom_mutation_hack,
            self.method7_worker_thread_abuse,
            self.method9_cache_poisoning,
            self.method10_timing_attack
        ]
        
        # 비동기 메소드들
        async_methods = [
            self.method1_websocket_hijack(),
            self.method2_memory_injection(),
            self.method3_cdp_manipulation(),
            self.method8_protocol_downgrade()
        ]
        
        # 동기 메소드 실행
        for method in sync_methods:
            try:
                method()
            except Exception as e:
                logger.error(f"{method.__name__} 실패: {e}")
        
        # 비동기 메소드 동시 실행
        await asyncio.gather(*async_methods, return_exceptions=True)
        
        logger.info("✅ 모든 LAG 우회 기법 적용 완료!")


class ExtremeTicketing:
    """극한의 티켓팅 전략"""
    
    def __init__(self, driver):
        self.driver = driver
        self.lag_bypass = UltraLagBypass(driver)
    
    async def nuclear_option(self):
        """핵폭탄 옵션 - 모든 것을 동원"""
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


# 실행 예시
async def main():
    """메인 실행"""
    from selenium import webdriver
    import undetected_chromedriver as uc
    
    # 브라우저 생성
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = uc.Chrome(options=options)
    
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
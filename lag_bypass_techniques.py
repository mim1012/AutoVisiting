#!/usr/bin/env python3
"""
LAG 우회 기법들을 별도 클래스로 분리
기존 기능 유지, 복잡도만 감소
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

logger = logging.getLogger(__name__)


class BaseLagBypassTechnique:
    """LAG 우회 기법 기본 클래스"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.technique_name = "기본 기법"
    
    def execute(self):
        """기법 실행 (하위 클래스에서 구현)"""
        raise NotImplementedError
    
    def log_start(self):
        """실행 시작 로그"""
        logger.info(f"🚀 {self.technique_name} 시작...")
    
    def log_complete(self):
        """실행 완료 로그"""
        logger.info(f"✅ {self.technique_name} 완료")


class WebSocketHijackTechnique(BaseLagBypassTechnique):
    """방법 1: WebSocket 직접 탈취"""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.technique_name = "WebSocket 하이재킹"
    
    async def execute(self):
        """WebSocket 하이재킹 실행"""
        self.log_start()
        
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
        self.log_complete()


class MemoryInjectionTechnique(BaseLagBypassTechnique):
    """방법 2: 메모리 직접 조작"""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.technique_name = "메모리 인젝션"
    
    async def execute(self):
        """메모리 조작 실행"""
        self.log_start()
        
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
        self.log_complete()


class BrowserExploitTechnique(BaseLagBypassTechnique):
    """방법 4: 브라우저 렌더링 익스플로잇"""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.technique_name = "브라우저 익스플로잇"
    
    def execute(self):
        """브라우저 렌더링 조작 실행"""
        self.log_start()
        
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
        self.log_complete()


class AjaxInterceptorTechnique(BaseLagBypassTechnique):
    """방법 5: AJAX 요청 가로채기 및 복제"""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.technique_name = "AJAX 인터셉터"
    
    def execute(self):
        """AJAX 인터셉터 실행"""
        self.log_start()
        
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
        self.log_complete()


class DomMutationTechnique(BaseLagBypassTechnique):
    """방법 6: DOM Mutation 실시간 감지"""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.technique_name = "DOM 뮤테이션 해킹"
    
    def execute(self):
        """DOM 뮤테이션 감지 실행"""
        self.log_start()
        
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
        self.log_complete()


class WorkerThreadTechnique(BaseLagBypassTechnique):
    """방법 7: Web Worker 스레드 남용"""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.technique_name = "워커 스레드 남용"
    
    def execute(self):
        """워커 스레드 실행"""
        self.log_start()
        
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
        self.log_complete()


class CachePoisoningTechnique(BaseLagBypassTechnique):
    """방법 9: 캐시 포이즈닝"""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.technique_name = "캐시 조작"
    
    def execute(self):
        """캐시 포이즈닝 실행"""
        self.log_start()
        
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
        self.log_complete()


class TimingAttackTechnique(BaseLagBypassTechnique):
    """방법 10: 타이밍 공격"""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.technique_name = "타이밍 어택"
    
    def execute(self):
        """타이밍 공격 실행"""
        self.log_start()
        
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
        self.log_complete()


class LagBypassTechniqueFactory:
    """LAG 우회 기법 팩토리"""
    
    @staticmethod
    def create_all_techniques(driver: webdriver.Chrome) -> List[BaseLagBypassTechnique]:
        """모든 기법 인스턴스 생성"""
        return [
            WebSocketHijackTechnique(driver),
            MemoryInjectionTechnique(driver),
            BrowserExploitTechnique(driver),
            AjaxInterceptorTechnique(driver),
            DomMutationTechnique(driver),
            WorkerThreadTechnique(driver),
            CachePoisoningTechnique(driver),
            TimingAttackTechnique(driver)
        ]
    
    @staticmethod
    def create_sync_techniques(driver: webdriver.Chrome) -> List[BaseLagBypassTechnique]:
        """동기 실행 기법들만 생성"""
        return [
            BrowserExploitTechnique(driver),
            AjaxInterceptorTechnique(driver),
            DomMutationTechnique(driver),
            WorkerThreadTechnique(driver),
            CachePoisoningTechnique(driver),
            TimingAttackTechnique(driver)
        ]
    
    @staticmethod
    def create_async_techniques(driver: webdriver.Chrome) -> List[BaseLagBypassTechnique]:
        """비동기 실행 기법들만 생성"""
        return [
            WebSocketHijackTechnique(driver),
            MemoryInjectionTechnique(driver)
        ]
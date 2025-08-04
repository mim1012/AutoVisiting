#!/usr/bin/env python3
"""
서버 과부하 극복 전략
개발자 관점의 고급 기법
"""

import asyncio
import httpx
import time
import random
import logging
from typing import List, Optional
import aiohttp
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ServerOverloadStrategy:
    """서버 과부하 극복 전략"""
    
    def __init__(self):
        self.base_url = "https://www.g4k.go.kr"
        self.healthy_servers = []
        self.connection_pool = []
        self.edge_servers = [
            "https://cdn.g4k.go.kr",
            "https://cache1.g4k.go.kr",
            "https://cache2.g4k.go.kr"
        ]
        
    async def prepare_assault(self):
        """공격 준비 - 연결 미리 수립"""
        logger.info("🔌 연결 풀 준비 중...")
        
        # 1. Keep-Alive 연결 10개 미리 생성
        for i in range(10):
            session = requests.Session()
            session.headers.update({
                'Connection': 'keep-alive',
                'Keep-Alive': 'timeout=600, max=100'
            })
            
            try:
                # 가벼운 요청으로 연결 수립
                session.head(self.base_url, timeout=2)
                self.connection_pool.append(session)
                logger.info(f"연결 #{i+1} 수립 완료")
            except:
                pass
        
        # 2. 건강한 서버 찾기
        await self._find_healthy_servers()
        
        # 3. DNS 프리페칭
        self._dns_prefetch()
    
    async def _find_healthy_servers(self):
        """살아있는 서버 찾기"""
        potential_servers = [
            f"https://srv{i}.g4k.go.kr" for i in range(1, 6)
        ] + self.edge_servers
        
        async with httpx.AsyncClient() as client:
            tasks = []
            for server in potential_servers:
                task = self._check_server_health(client, server)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for server, result in zip(potential_servers, results):
                if result is True:
                    self.healthy_servers.append(server)
                    logger.info(f"✅ 건강한 서버 발견: {server}")
    
    async def _check_server_health(self, client, server):
        """서버 상태 체크"""
        try:
            response = await client.head(server, timeout=1.0)
            return response.status_code < 500
        except:
            return False
    
    def _dns_prefetch(self):
        """DNS 미리 조회"""
        import socket
        domains = ['www.g4k.go.kr', 'cdn.g4k.go.kr', 'api.g4k.go.kr']
        
        for domain in domains:
            try:
                socket.gethostbyname(domain)
                logger.info(f"DNS 프리페치: {domain}")
            except:
                pass
    
    async def multi_vector_attack(self, reservation_data):
        """다중 벡터 동시 공격"""
        logger.info("🚀 다중 벡터 공격 시작!")
        
        strategies = [
            self._http2_multiplex_attack(reservation_data),
            self._edge_server_attack(reservation_data),
            self._connection_pool_attack(reservation_data),
            self._timing_exploit_attack(reservation_data)
        ]
        
        # 모든 전략 동시 실행
        tasks = [asyncio.create_task(strategy) for strategy in strategies]
        
        # 첫 번째 성공 대기
        done, pending = await asyncio.wait(
            tasks, 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # 나머지 취소
        for task in pending:
            task.cancel()
        
        # 성공한 결과 반환
        for task in done:
            result = await task
            if result:
                logger.info("✅ 예약 성공!")
                return result
        
        return None
    
    async def _http2_multiplex_attack(self, data):
        """HTTP/2 멀티플렉싱 공격"""
        logger.info("전략1: HTTP/2 멀티플렉싱")
        
        async with httpx.AsyncClient(http2=True) as client:
            # 단일 연결로 50개 요청
            tasks = []
            for i in range(50):
                headers = {
                    'X-Request-ID': f'h2-{i}',
                    'Priority': 'u=0, i'  # 최고 우선순위
                }
                
                task = client.post(
                    f"{self.base_url}/reservation/submit",
                    json=data,
                    headers=headers,
                    timeout=5.0
                )
                tasks.append(task)
            
            # 경쟁
            for coro in asyncio.as_completed(tasks):
                try:
                    response = await coro
                    if response.status_code == 200:
                        return response.json()
                except:
                    continue
        
        return None
    
    async def _edge_server_attack(self, data):
        """엣지 서버 공격"""
        logger.info("전략2: 엣지/CDN 서버 활용")
        
        if not self.healthy_servers:
            return None
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for server in self.healthy_servers[:3]:  # 상위 3개
                task = self._single_request(session, server, data)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, dict) and result.get('success'):
                    return result
        
        return None
    
    async def _single_request(self, session, server, data):
        """단일 요청"""
        try:
            url = f"{server}/reservation/submit"
            async with session.post(url, json=data, timeout=3) as response:
                if response.status == 200:
                    return await response.json()
        except:
            return None
    
    def _connection_pool_attack(self, data):
        """연결 풀 활용 공격"""
        logger.info("전략3: 기존 연결 재사용")
        
        if not self.connection_pool:
            return None
        
        # ThreadPool로 동시 실행
        with ThreadPoolExecutor(max_workers=len(self.connection_pool)) as executor:
            futures = []
            
            for session in self.connection_pool:
                future = executor.submit(
                    self._pool_request, 
                    session, 
                    data
                )
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=3)
                    if result:
                        return result
                except:
                    continue
        
        return None
    
    def _pool_request(self, session, data):
        """풀 요청"""
        try:
            response = session.post(
                f"{self.base_url}/reservation/submit",
                json=data,
                timeout=2
            )
            
            if response.status_code == 200:
                return response.json()
        except:
            return None
    
    async def _timing_exploit_attack(self, data):
        """타이밍 취약점 공격"""
        logger.info("전략4: 서버 타이밍 패턴 악용")
        
        # 서버 GC 주기 추정 (보통 30초)
        current_second = int(time.time()) % 30
        
        # GC 직후가 가장 여유로움
        if current_second > 25:
            wait_time = 30 - current_second + 0.1
            logger.info(f"GC 대기: {wait_time}초")
            await asyncio.sleep(wait_time)
        
        # GC 직후 요청
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/reservation/submit",
                json=data,
                headers={'X-Timing': 'gc-exploit'}
            )
            
            if response.status_code == 200:
                return response.json()
        
        return None
    
    def analyze_response_pattern(self):
        """서버 응답 패턴 분석"""
        logger.info("📊 서버 패턴 분석 중...")
        
        response_times = []
        
        for i in range(20):
            start = time.time()
            try:
                requests.head(self.base_url, timeout=2)
                response_time = time.time() - start
                response_times.append((i, response_time))
            except:
                response_times.append((i, 999))
            
            time.sleep(1)
        
        # 패턴 찾기
        fast_times = [t for t in response_times if t[1] < 0.5]
        if fast_times:
            logger.info(f"빠른 응답 시점: {[t[0] for t in fast_times]}")
        
        return response_times


# 실제 사용 예시
async def defeat_server_overload():
    """서버 과부하 극복 실행"""
    strategy = ServerOverloadStrategy()
    
    # 1. 사전 준비 (1분 전)
    await strategy.prepare_assault()
    
    # 2. 패턴 분석
    strategy.analyze_response_pattern()
    
    # 3. 9시 정각 - 다중 공격
    reservation_data = {
        'date': '2024-01-30',
        'time': '09:00',
        'passport': 'M12345678'
    }
    
    result = await strategy.multi_vector_attack(reservation_data)
    
    if result:
        logger.info("🎉 서버 과부하 속에서도 예약 성공!")
        return result
    else:
        logger.error("😢 모든 전략 실패")
        return None
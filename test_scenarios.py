#!/usr/bin/env python3
"""
다양한 테스트 시나리오 모음
실제 상황 시뮬레이션 및 안전 테스트
"""

import time
import random
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class TestScenarios:
    """테스트 시나리오 모음"""
    
    def __init__(self, driver):
        self.driver = driver
        self.test_results = []
    
    def scenario_1_gentle_monitoring(self):
        """시나리오 1: 부드러운 모니터링 (초보자용)"""
        logger.info("🌱 시나리오 1: 부드러운 모니터링")
        
        print("""
📋 시나리오 1: 부드러운 모니터링
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 특징:
   • 5-10초 간격으로 체크
   • 서버 부하 최소화
   • 봇 탐지 위험 낮음
   • 초보자 추천

⏱️  예상 소요시간: 30분-1시간
🎯 성공 확률: 중간 (취소표가 많을 때 유리)
        """)
        
        gentle_script = """
        let checkCount = 0;
        let foundCount = 0;
        
        function gentleMonitor() {
            checkCount++;
            console.log(`[GENTLE] 체크 #${checkCount} - ${new Date().toLocaleTimeString()}`);
            
            // 자연스러운 스크롤
            window.scrollBy(0, Math.random() * 100 - 50);
            
            // 부드럽게 날짜 찾기
            const dates = document.querySelectorAll('td.available:not(.disabled)');
            
            if (dates.length > 0) {
                foundCount++;
                console.log(`🎯 발견! ${dates.length}개 (총 ${foundCount}번째)`);
                
                // 발견 알림
                document.title = `🎯 취소표 발견! (${dates.length}개)`;
                
                return {
                    found: true,
                    count: dates.length,
                    dates: Array.from(dates).map(d => d.textContent.trim())
                };
            }
            
            return {found: false, count: 0};
        }
        
        // 5-10초 랜덤 간격
        window.gentleInterval = setInterval(() => {
            const result = gentleMonitor();
            if (result.found) {
                // 발견 시 알림
                if (window.Notification && Notification.permission === 'granted') {
                    new Notification('취소표 발견!', {
                        body: `${result.count}개 날짜 발견됨`,
                        icon: '/favicon.ico'
                    });
                }
            }
        }, Math.random() * 5000 + 5000); // 5-10초
        """
        
        self.driver.execute_script(gentle_script)
        return self.wait_for_user_decision("부드러운 모니터링")
    
    def scenario_2_smart_adaptive(self):
        """시나리오 2: 스마트 적응형 (중급자용)"""
        logger.info("🧠 시나리오 2: 스마트 적응형")
        
        print("""
📋 시나리오 2: 스마트 적응형
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 특징:
   • 서버 응답 속도에 따라 간격 조정
   • 피크 시간대 자동 감지
   • 실패 시 전략 변경
   • 중급자 추천

⏱️  예상 소요시간: 15-30분
🎯 성공 확률: 높음 (서버 패턴 학습)
        """)
        
        adaptive_script = """
        let adaptiveState = {
            interval: 3000,  // 시작 간격
            successCount: 0,
            failCount: 0,
            avgResponseTime: 0,
            responses: []
        };
        
        function measureResponse(callback) {
            const start = performance.now();
            
            // 가벼운 요청으로 응답시간 측정
            fetch(location.href, {method: 'HEAD'})
                .then(() => {
                    const responseTime = performance.now() - start;
                    adaptiveState.responses.push(responseTime);
                    
                    // 최근 5개 평균
                    if (adaptiveState.responses.length > 5) {
                        adaptiveState.responses.shift();
                    }
                    
                    adaptiveState.avgResponseTime = 
                        adaptiveState.responses.reduce((a,b) => a+b) / adaptiveState.responses.length;
                    
                    // 간격 조정
                    if (adaptiveState.avgResponseTime < 500) {
                        adaptiveState.interval = Math.max(2000, adaptiveState.interval - 200);
                    } else if (adaptiveState.avgResponseTime > 2000) {
                        adaptiveState.interval = Math.min(8000, adaptiveState.interval + 500);
                    }
                    
                    callback();
                })
                .catch(() => {
                    adaptiveState.failCount++;
                    adaptiveState.interval += 1000; // 실패 시 느리게
                    callback();
                });
        }
        
        function smartCheck() {
            console.log(`[SMART] 체크 - 간격: ${adaptiveState.interval}ms, 평균응답: ${adaptiveState.avgResponseTime.toFixed(0)}ms`);
            
            const dates = document.querySelectorAll('td.available:not(.disabled)');
            
            if (dates.length > 0) {
                console.log('🎯 SMART 모드에서 발견!');
                adaptiveState.successCount++;
                
                return {
                    found: true,
                    count: dates.length,
                    strategy: 'smart_adaptive'
                };
            }
            
            return {found: false};
        }
        
        function runAdaptive() {
            measureResponse(() => {
                const result = smartCheck();
                
                // 다음 체크 스케줄
                setTimeout(runAdaptive, adaptiveState.interval);
            });
        }
        
        // 시작
        runAdaptive();
        """
        
        self.driver.execute_script(adaptive_script)
        return self.wait_for_user_decision("스마트 적응형")
    
    def scenario_3_peak_time_warrior(self):
        """시나리오 3: 피크타임 전사 (고급자용)"""
        logger.info("⚔️ 시나리오 3: 피크타임 전사")
        
        print("""
📋 시나리오 3: 피크타임 전사 (9-11시, 14-16시)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 특징:
   • 피크 시간대 공격적 모니터링
   • 1-2초 간격 고속 체크
   • 멀티 스레드 감지
   • 고급자 전용

⏱️  예상 소요시간: 5-15분
🎯 성공 확률: 매우 높음 (위험도 높음)
        """)
        
        warrior_script = """
        const isPeakTime = () => {
            const hour = new Date().getHours();
            return (hour >= 9 && hour <= 11) || (hour >= 14 && hour <= 16);
        };
        
        let warriorState = {
            mode: isPeakTime() ? 'peak' : 'normal',
            rapidChecks: 0,
            victories: 0
        };
        
        function warriorCheck() {
            warriorState.rapidChecks++;
            
            const interval = warriorState.mode === 'peak' ? 1000 : 3000;
            const intensity = warriorState.mode === 'peak' ? '🔥' : '⚡';
            
            console.log(`${intensity} [WARRIOR] 체크 #${warriorState.rapidChecks} (${warriorState.mode} 모드)`);
            
            // 다중 선택자로 강력 스캔
            const selectors = [
                'td.available:not(.disabled)',
                'td[data-available="true"]',
                '.calendar-date.enabled',
                'button:not([disabled])[data-date]'
            ];
            
            let totalFound = 0;
            let foundElements = [];
            
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    totalFound += elements.length;
                    foundElements.push(...Array.from(elements));
                }
            });
            
            if (totalFound > 0) {
                warriorState.victories++;
                console.log(`⚔️ VICTORY! ${totalFound}개 발견 (총 ${warriorState.victories}승)`);
                
                // 승리 효과
                document.body.style.background = 'linear-gradient(45deg, #ff6b6b, #4ecdc4)';
                setTimeout(() => {
                    document.body.style.background = '';
                }, 2000);
                
                return {
                    found: true,
                    count: totalFound,
                    elements: foundElements,
                    mode: warriorState.mode
                };
            }
            
            return {found: false};
        }
        
        // 워리어 모드 시작
        const warriorInterval = setInterval(() => {
            // 시간대별 모드 업데이트
            warriorState.mode = isPeakTime() ? 'peak' : 'normal';
            
            const result = warriorCheck();
            
            // 연속 100회 체크 후 잠시 휴식
            if (warriorState.rapidChecks % 100 === 0) {
                console.log('⏸️ 전사 휴식 (5초)...');
                clearInterval(warriorInterval);
                setTimeout(() => {
                    // 다시 시작
                    setInterval(arguments.callee, 
                        warriorState.mode === 'peak' ? 1000 : 3000
                    );
                }, 5000);
            }
        }, warriorState.mode === 'peak' ? 1000 : 3000);
        """
        
        self.driver.execute_script(warrior_script)
        return self.wait_for_user_decision("피크타임 전사")
    
    def scenario_4_stealth_ninja(self):
        """시나리오 4: 스텔스 닌자 (은밀 작전)"""
        logger.info("🥷 시나리오 4: 스텔스 닌자")
        
        print("""
📋 시나리오 4: 스텔스 닌자 (은밀 작전)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 특징:
   • 불규칙 패턴으로 탐지 회피
   • 인간 행동 완벽 모방
   • 백그라운드 은밀 실행
   • 안전성 최우선

⏱️  예상 소요시간: 1-2시간
🎯 성공 확률: 중간 (안전성 보장)
        """)
        
        ninja_script = """
        let ninjaState = {
            lastAction: Date.now(),
            humanPatterns: [
                {action: 'scroll', weight: 0.3},
                {action: 'click_random', weight: 0.2},
                {action: 'pause', weight: 0.3},
                {action: 'check_date', weight: 0.2}
            ],
            stealthLevel: 100
        };
        
        function humanAction() {
            const rand = Math.random();
            let cumulative = 0;
            
            for (let pattern of ninjaState.humanPatterns) {
                cumulative += pattern.weight;
                if (rand <= cumulative) {
                    return pattern.action;
                }
            }
            return 'pause';
        }
        
        function executeNinjaAction(action) {
            switch(action) {
                case 'scroll':
                    window.scrollBy(0, Math.random() * 200 - 100);
                    break;
                    
                case 'click_random':
                    // 무해한 요소 클릭
                    const safeElements = document.querySelectorAll('div, span, p');
                    if (safeElements.length > 0) {
                        const randomEl = safeElements[Math.floor(Math.random() * safeElements.length)];
                        if (randomEl.offsetParent) { // 보이는 요소만
                            randomEl.click();
                        }
                    }
                    break;
                    
                case 'pause':
                    // 그냥 대기 (인간이 생각하는 시간)
                    break;
                    
                case 'check_date':
                    // 은밀하게 날짜 체크
                    const dates = document.querySelectorAll('td.available:not(.disabled)');
                    if (dates.length > 0) {
                        console.log(`🥷 닌자 발견: ${dates.length}개 (은밀)`);
                        ninjaState.stealthLevel = Math.max(0, ninjaState.stealthLevel - 5);
                        
                        return {
                            found: true,
                            count: dates.length,
                            stealth_level: ninjaState.stealthLevel
                        };
                    } else {
                        ninjaState.stealthLevel = Math.min(100, ninjaState.stealthLevel + 1);
                    }
                    break;
            }
            
            return {found: false};
        }
        
        function ninjaLoop() {
            const action = humanAction();
            const result = executeNinjaAction(action);
            
            // 은밀성 레벨에 따른 간격 조정
            const baseInterval = 5000;
            const stealthMultiplier = ninjaState.stealthLevel / 100;
            const interval = baseInterval * (0.5 + stealthMultiplier);
            
            console.log(`🥷 [NINJA] ${action} - 은밀도: ${ninjaState.stealthLevel}%`);
            
            // 다음 액션 스케줄
            setTimeout(ninjaLoop, interval + Math.random() * 2000);
            
            return result;
        }
        
        // 닌자 작전 시작
        ninjaLoop();
        """
        
        self.driver.execute_script(ninja_script)
        return self.wait_for_user_decision("스텔스 닌자")
    
    def scenario_5_last_resort(self):
        """시나리오 5: 최후의 수단 (올인 모드)"""
        logger.info("💥 시나리오 5: 최후의 수단")
        
        print("""
📋 시나리오 5: 최후의 수단 (올인 모드)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  주의: 매우 공격적인 모드!
✅ 특징:
   • 모든 기술 총동원
   • 0.5초 간격 초고속
   • 멀티 스레드 + 백그라운드
   • 성공 시까지 무한 시도

⏱️  예상 소요시간: 1-10분
🎯 성공 확률: 최고 (위험도 최고)
        """)
        
        choice = input("\n⚠️  정말 최후의 수단을 사용하시겠습니까? (yes/no): ")
        if choice.lower() != 'yes':
            print("❌ 최후의 수단 취소됨")
            return False
        
        last_resort_script = """
        console.log('💥 최후의 수단 활성화!');
        
        let lastResortState = {
            allInMode: true,
            attempts: 0,
            maxAttempts: 1000,
            intervals: []
        };
        
        // 다중 스레드 시뮬레이션
        function createMultipleCheckers() {
            // 0.5초 간격 메인 체커
            const mainChecker = setInterval(() => {
                lastResortState.attempts++;
                
                const dates = document.querySelectorAll('td.available:not(.disabled)');
                if (dates.length > 0) {
                    console.log('💥 최후의 수단 성공!');
                    
                    // 모든 인터벌 정리
                    lastResortState.intervals.forEach(clearInterval);
                    
                    // 승리 이펙트
                    document.body.innerHTML = '<h1 style="color:red;text-align:center;font-size:50px;">SUCCESS!</h1>' + document.body.innerHTML;
                    
                    return {found: true, method: 'last_resort'};
                }
                
                if (lastResortState.attempts >= lastResortState.maxAttempts) {
                    console.log('💥 최대 시도 횟수 도달');
                    lastResortState.intervals.forEach(clearInterval);
                }
            }, 500);
            
            // 백업 체커들
            const backup1 = setInterval(() => {
                document.querySelectorAll('td').forEach(td => {
                    if (td.textContent && !td.classList.contains('disabled')) {
                        td.style.border = '2px solid red';
                    }
                });
            }, 1000);
            
            const backup2 = setInterval(() => {
                // 강제 새로고침 시도
                if (Math.random() < 0.1) { // 10% 확률
                    location.reload();
                }
            }, 10000);
            
            lastResortState.intervals = [mainChecker, backup1, backup2];
        }
        
        createMultipleCheckers();
        """
        
        self.driver.execute_script(last_resort_script)
        return self.wait_for_user_decision("최후의 수단")
    
    def wait_for_user_decision(self, scenario_name: str):
        """사용자 결정 대기"""
        print(f"\n🎯 {scenario_name} 모드가 실행 중입니다...")
        print("\n⌨️  명령어:")
        print("   Enter: 상태 확인")
        print("   'q': 종료")
        print("   'r': 결과 보기")
        
        while True:
            try:
                user_input = input("\n> ").strip().lower()
                
                if user_input == 'q':
                    print("🛑 테스트 종료")
                    break
                elif user_input == 'r':
                    self.show_results()
                else:
                    self.check_current_status()
                    
            except KeyboardInterrupt:
                print("\n🛑 사용자 중단")
                break
        
        return True
    
    def check_current_status(self):
        """현재 상태 확인"""
        try:
            result = self.driver.execute_script("""
                // 각 시나리오별 상태 확인
                let status = {
                    url: location.href,
                    title: document.title,
                    foundDates: document.querySelectorAll('td.available:not(.disabled)').length,
                    timestamp: new Date().toLocaleTimeString()
                };
                
                // 시나리오별 추가 정보
                if (window.gentleInterval) status.mode = 'gentle';
                if (window.adaptiveState) status.mode = 'adaptive';
                if (window.warriorState) status.mode = 'warrior';
                if (window.ninjaState) status.mode = 'ninja';
                if (window.lastResortState) status.mode = 'last_resort';
                
                return status;
            """)
            
            print(f"\n📊 현재 상태 ({result['timestamp']}):")
            print(f"   모드: {result.get('mode', 'unknown')}")
            print(f"   발견된 날짜: {result['foundDates']}개")
            print(f"   페이지: {result['title'][:50]}")
            
        except Exception as e:
            print(f"❌ 상태 확인 실패: {e}")
    
    def show_results(self):
        """결과 보기"""
        try:
            result = self.driver.execute_script("""
                return {
                    dates: Array.from(document.querySelectorAll('td.available:not(.disabled)')).map(d => d.textContent.trim()),
                    totalElements: document.querySelectorAll('td').length,
                    pageReady: document.readyState
                };
            """)
            
            print(f"\n📋 테스트 결과:")
            print(f"   사용 가능한 날짜: {len(result['dates'])}개")
            if result['dates']:
                print(f"   날짜 목록: {', '.join(result['dates'][:5])}")
            print(f"   전체 셀: {result['totalElements']}개")
            print(f"   페이지 상태: {result['pageReady']}")
            
        except Exception as e:
            print(f"❌ 결과 조회 실패: {e}")


def main():
    """테스트 시나리오 실행"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🧪 테스트 시나리오 선택                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("1. 🌱 부드러운 모니터링 (초보자용)")
    print("2. 🧠 스마트 적응형 (중급자용)")
    print("3. ⚔️ 피크타임 전사 (고급자용)")
    print("4. 🥷 스텔스 닌자 (은밀 작전)")
    print("5. 💥 최후의 수단 (올인 모드)")
    
    choice = input("\n선택 (1-5): ")
    
    # 실제 테스트는 cancellation_hunter.py에서 실행
    print(f"\n✅ 시나리오 {choice} 선택됨")
    print("🚀 cancellation_hunter.py를 실행하여 테스트하세요!")


if __name__ == "__main__":
    main()
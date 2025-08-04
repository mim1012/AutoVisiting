#!/usr/bin/env python3
"""
취소표 헌터 - 실시간 취소표 감지 및 자동 예약
안전한 테스트 모드 포함
"""

import time
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from stealth_browser import StealthBrowser
from ultra_lag_bypass import UltraLagBypass
from adaptive_calendar_refresher import AdaptiveCalendarRefresher

logger = logging.getLogger(__name__)


class CancellationHunter:
    """취소표 실시간 헌터"""
    
    def __init__(self, test_mode: bool = True):
        self.test_mode = test_mode
        self.stealth_browser = StealthBrowser()
        self.driver = None
        self.found_dates = []
        self.attempt_count = 0
        self.last_check_time = time.time()
        
        # 테스트 설정
        self.test_config = {
            'safe_intervals': [2, 3, 4, 5],  # 안전한 간격들 (초)
            'max_attempts': 100 if test_mode else 1000,
            'log_everything': test_mode,
            'gentle_mode': test_mode  # 부드러운 모드
        }
        
    def setup_test_environment(self):
        """테스트 환경 설정"""
        if self.test_mode:
            print("\n🧪 테스트 모드 활성화")
            print("=" * 50)
            print("✅ 안전한 간격으로 동작")
            print("✅ 상세 로그 기록")
            print("✅ 최대 100회 시도 제한")
            print("✅ 서버 부하 최소화")
            print("=" * 50)
        
        # 테스트용 브라우저 설정
        self.driver = self.stealth_browser.create_driver()
        
        # 테스트 모드용 부드러운 스크립트
        gentle_script = """
        // 테스트 모드 - 부드러운 감지
        window.testMode = true;
        window.foundDates = [];
        window.checkCount = 0;
        
        function gentleCheck() {
            window.checkCount++;
            console.log(`[TEST] 체크 #${window.checkCount}`);
            
            // 부드럽게 날짜 찾기
            const dates = document.querySelectorAll('td.available:not(.disabled)');
            
            if (dates.length > 0) {
                console.log(`[TEST] 발견! ${dates.length}개 날짜`);
                window.foundDates = Array.from(dates).map(d => ({
                    text: d.textContent,
                    classes: d.className,
                    available: !d.classList.contains('disabled')
                }));
                return true;
            }
            return false;
        }
        
        // 테스트 모드는 천천히
        window.gentleInterval = setInterval(gentleCheck, 3000); // 3초마다
        """
        
        self.driver.execute_script(gentle_script)
    
    def safe_test_monitoring(self):
        """안전한 테스트 모니터링"""
        logger.info("🔍 안전 테스트 모니터링 시작...")
        
        print("\n📊 실시간 모니터링 현황")
        print("-" * 60)
        
        start_time = time.time()
        
        for i in range(self.test_config['max_attempts']):
            try:
                # 안전한 간격 대기
                interval = random.choice(self.test_config['safe_intervals'])
                time.sleep(interval)
                
                # 부드럽게 체크
                result = self.gentle_date_check()
                
                # 진행 상황 표시
                elapsed = int(time.time() - start_time)
                print(f"\r시도: {i+1:3d}/{self.test_config['max_attempts']} | "
                      f"경과: {elapsed:3d}초 | "
                      f"발견: {len(self.found_dates):2d}개", end='')
                
                if result:
                    print(f"\n✅ 취소표 발견! (시도 #{i+1})")
                    self.handle_found_dates(test_mode=True)
                    break
                    
                # 10번마다 상태 체크
                if (i + 1) % 10 == 0:
                    self.check_browser_health()
                    
            except KeyboardInterrupt:
                print("\n⏹️  사용자 중단")
                break
            except Exception as e:
                logger.error(f"모니터링 오류: {e}")
                time.sleep(5)  # 오류 시 더 오래 대기
        
        print(f"\n📊 테스트 완료! 총 {i+1}회 시도")
    
    def gentle_date_check(self) -> bool:
        """부드러운 날짜 체크"""
        try:
            # JavaScript에서 결과 가져오기
            result = self.driver.execute_script("""
                if (window.foundDates && window.foundDates.length > 0) {
                    const dates = window.foundDates;
                    window.foundDates = []; // 초기화
                    return dates;
                }
                return null;
            """)
            
            if result:
                self.found_dates = result
                return True
                
            # 추가로 직접 체크 (백업)
            elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "td.available:not(.disabled)"
            )
            
            if elements:
                self.found_dates = [
                    {
                        'text': el.text,
                        'element': el,
                        'available': True
                    }
                    for el in elements[:3]  # 처음 3개만
                ]
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"체크 오류: {e}")
            return False
    
    def handle_found_dates(self, test_mode: bool = True):
        """발견된 날짜 처리"""
        if not self.found_dates:
            return
            
        print(f"\n🎯 발견된 날짜들:")
        for i, date_info in enumerate(self.found_dates):
            print(f"  {i+1}. {date_info.get('text', 'N/A')} - "
                  f"Available: {date_info.get('available', False)}")
        
        if test_mode:
            print("\n🧪 테스트 모드 - 실제 클릭하지 않음")
            choice = input("실제로 예약을 시도하시겠습니까? (y/N): ")
            if choice.lower() != 'y':
                print("✅ 테스트 완료 - 실제 예약하지 않음")
                return
        
        # 실제 예약 시도
        self.attempt_reservation()
    
    def attempt_reservation(self):
        """실제 예약 시도"""
        if not self.found_dates:
            return False
            
        logger.info("🎯 예약 시도 중...")
        
        try:
            # 첫 번째 가능한 날짜 클릭
            date_info = self.found_dates[0]
            
            if 'element' in date_info:
                element = date_info['element']
                
                # 인간처럼 클릭
                self.stealth_browser.human_like_click(self.driver, element)
                
                # 잠시 대기
                time.sleep(1)
                
                # 다음 단계 확인
                return self.check_next_step()
            
        except Exception as e:
            logger.error(f"예약 시도 실패: {e}")
            return False
    
    def check_next_step(self) -> bool:
        """다음 단계 확인"""
        try:
            # URL 변화 체크
            current_url = self.driver.current_url
            
            # 예약 페이지로 이동했는지 확인
            if 'step' in current_url or 'reservation' in current_url:
                logger.info("✅ 예약 페이지로 이동 성공!")
                return True
            
            # 추가 확인 요소들
            success_indicators = [
                "여권번호",
                "passport",
                "개인정보",
                "예약자 정보"
            ]
            
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            for indicator in success_indicators:
                if indicator in page_text:
                    logger.info(f"✅ 성공 지표 발견: {indicator}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"다음 단계 확인 실패: {e}")
            return False
    
    def check_browser_health(self):
        """브라우저 상태 체크"""
        try:
            # 간단한 JavaScript 실행으로 상태 확인
            result = self.driver.execute_script("return document.readyState")
            
            if result != "complete":
                logger.warning("브라우저 상태 불안정")
                time.sleep(2)
            
            # 메모리 정리
            self.driver.execute_script("""
                if (window.gc) window.gc();
                console.clear();
            """)
            
        except Exception as e:
            logger.error(f"브라우저 상태 체크 실패: {e}")
    
    def aggressive_mode(self):
        """공격적 모드 (실전용)"""
        logger.info("⚡ 공격적 모드 시작!")
        
        # 극한 기법 적용
        lag_bypass = UltraLagBypass(self.driver)
        
        # 적응형 새로고침
        refresher = AdaptiveCalendarRefresher(self.driver, self.stealth_browser)
        
        # 동시 실행
        import asyncio
        
        async def combined_attack():
            # 모든 우회 기법 적용
            await lag_bypass.execute_all_methods()
            
            # 버스트 모드로 새로고침
            dates = refresher.burst_mode(60)  # 1분간 집중
            
            if dates:
                # 즉시 클릭
                self.stealth_browser.human_like_click(
                    self.driver, 
                    dates[0]['element']
                )
                return True
            
            return False
        
        # 실행
        success = asyncio.run(combined_attack())
        
        if success:
            logger.info("🎉 공격적 모드 성공!")
        else:
            logger.info("😅 공격적 모드 완료 - 날짜 없음")
    
    def run_test(self):
        """테스트 실행"""
        try:
            print("\n🧪 취소표 헌터 테스트 시작!")
            
            # 1. 환경 설정
            self.setup_test_environment()
            
            # 2. G4K 접속
            print("\n📱 G4K 사이트 접속 중...")
            self.stealth_browser.safe_page_load(
                self.driver, 
                "https://www.g4k.go.kr"
            )
            
            # 3. 수동 로그인 대기
            print("\n👤 수동 작업 필요:")
            print("   1. 로그인")
            print("   2. 방문예약 메뉴 이동")
            print("   3. 캘린더 페이지까지 진행")
            input("\n✅ 준비 완료 시 Enter...")
            
            # 4. 테스트 선택
            mode = self.select_test_mode()
            
            if mode == '1':
                self.safe_test_monitoring()
            elif mode == '2':
                self.test_mode = False
                self.aggressive_mode()
            else:
                print("❌ 잘못된 선택")
            
        except Exception as e:
            logger.error(f"테스트 실행 실패: {e}")
        finally:
            input("\n🔚 종료하려면 Enter...")
            if self.driver:
                self.driver.quit()
    
    def select_test_mode(self) -> str:
        """테스트 모드 선택"""
        print("\n🎯 테스트 모드를 선택하세요:")
        print("1. 🧪 안전 테스트 (추천) - 부드럽게 모니터링")
        print("2. ⚡ 실전 테스트 - 공격적 모드")
        
        while True:
            choice = input("\n선택 (1-2): ").strip()
            if choice in ['1', '2']:
                return choice
            print("❌ 잘못된 선택입니다.")


def main():
    """메인 실행"""
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cancellation_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🎯 취소표 헌터 테스트                    ║
║                                                              ║
║  📋 테스트 목적:                                            ║
║     • 시스템 안정성 확인                                    ║
║     • 감지 성능 측정                                        ║
║     • 실제 환경 적응성 테스트                               ║
║                                                              ║
║  ⚠️  주의사항:                                              ║
║     • 테스트 모드는 안전한 간격 사용                        ║
║     • 실제 예약은 신중하게 결정                             ║
║     • 과도한 사용 금지                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    hunter = CancellationHunter(test_mode=True)
    hunter.run_test()


if __name__ == "__main__":
    main()
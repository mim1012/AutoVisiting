#!/usr/bin/env python3
"""
G4K 방문예약 하이브리드 자동화 시스템
로그인은 사용자가 수동으로 처리하고, 나머지 예약 과정을 자동화
페이지 렉 및 서버 과부하 대응 메커니즘 포함
"""

import time
import logging
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import statistics

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    WebDriverException, StaleElementReferenceException
)
from profile_manager import ConfigManager
from auto_input_handler import AutoInputHandler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('g4k_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NetworkMonitor:
    """네트워크 상태 모니터링 클래스"""
    
    def __init__(self):
        self.response_times = []
        self.error_count = 0
        self.total_requests = 0
        self.last_check_time = time.time()
        
    def record_response_time(self, response_time: float):
        """응답 시간 기록"""
        self.response_times.append(response_time)
        self.total_requests += 1
        
        # 최근 100개 응답 시간만 유지
        if len(self.response_times) > 100:
            self.response_times.pop(0)
    
    def record_error(self):
        """오류 발생 기록"""
        self.error_count += 1
        self.total_requests += 1
    
    def get_average_response_time(self) -> float:
        """평균 응답 시간 계산"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    def get_error_rate(self) -> float:
        """오류율 계산"""
        if self.total_requests == 0:
            return 0.0
        return self.error_count / self.total_requests
    
    def is_server_overloaded(self) -> bool:
        """서버 과부하 상태 판단"""
        avg_response_time = self.get_average_response_time()
        error_rate = self.get_error_rate()
        
        # 평균 응답 시간이 10초 이상이거나 오류율이 30% 이상인 경우
        return avg_response_time > 10.0 or error_rate > 0.3


class AdaptiveTimeout:
    """적응형 타임아웃 관리 클래스"""
    
    def __init__(self, base_timeout: int = 30):
        self.base_timeout = base_timeout
        self.current_timeout = base_timeout
        self.response_times = []
        
    def update_timeout(self, response_time: float):
        """응답 시간을 바탕으로 타임아웃 업데이트"""
        self.response_times.append(response_time)
        
        # 최근 20개 응답 시간만 유지
        if len(self.response_times) > 20:
            self.response_times.pop(0)
        
        if len(self.response_times) >= 5:
            avg_time = statistics.mean(self.response_times)
            std_dev = statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0
            
            # 평균 + 2*표준편차 + 여유시간(10초)
            self.current_timeout = max(
                self.base_timeout,
                int(avg_time + 2 * std_dev + 10)
            )
    
    def get_timeout(self) -> int:
        """현재 타임아웃 값 반환"""
        return self.current_timeout


class RetryManager:
    """재시도 관리 클래스"""
    
    def __init__(self, max_retries: int = 5):
        self.max_retries = max_retries
        self.retry_delays = [1, 2, 5, 10, 20]  # 지수 백오프
    
    def execute_with_retry(self, func, *args, **kwargs):
        """재시도 로직을 적용하여 함수 실행"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                
                logger.info(f"작업 성공 (시도 {attempt + 1}/{self.max_retries}, 응답시간: {response_time:.2f}초)")
                return result, response_time
                
            except Exception as e:
                last_exception = e
                logger.warning(f"시도 {attempt + 1}/{self.max_retries} 실패: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    logger.info(f"{delay}초 후 재시도...")
                    time.sleep(delay)
        
        logger.error(f"모든 재시도 실패. 마지막 오류: {str(last_exception)}")
        raise last_exception


class LoginDetector:
    """로그인 완료 감지 클래스"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.check_interval = 2  # 2초마다 확인
        
    def wait_for_login_completion(self, timeout: int = 300) -> bool:
        """로그인 완료까지 대기 (최대 5분)"""
        start_time = time.time()
        
        logger.info("사용자 로그인 대기 중...")
        
        while time.time() - start_time < timeout:
            try:
                # 로그인 완료 확인 방법들
                if self._check_login_indicators():
                    logger.info("로그인 완료 감지됨")
                    return True
                    
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.warning(f"로그인 상태 확인 중 오류: {e}")
                time.sleep(self.check_interval)
        
        logger.error("로그인 타임아웃")
        return False
    
    def _check_login_indicators(self) -> bool:
        """로그인 완료 지표 확인"""
        try:
            # 1. URL 변화 확인
            current_url = self.driver.current_url
            if 'login' not in current_url.lower() and 'main' in current_url.lower():
                return True
            
            # 2. 로그아웃 버튼 존재 확인
            logout_elements = self.driver.find_elements(By.XPATH, "//a[contains(text(), '로그아웃')]")
            if logout_elements:
                return True
            
            # 3. 사용자 정보 표시 요소 확인
            user_info_elements = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'user-name')] | //div[contains(@class, 'user-info')]")
            if user_info_elements:
                return True
            
            # 4. 메인 메뉴 접근 가능 확인
            main_menu_elements = self.driver.find_elements(By.XPATH, "//a[contains(text(), '민원신청')] | //a[contains(text(), '방문예약')]")
            if main_menu_elements:
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"로그인 지표 확인 중 오류: {e}")
            return False


class ReservationAutomator:
    """예약 자동화 메인 클래스"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.driver = None
        self.wait = None
        self.network_monitor = NetworkMonitor()
        self.adaptive_timeout = AdaptiveTimeout()
        self.retry_manager = RetryManager()
        self.login_detector = None
        self.config_manager = ConfigManager()
        self.auto_input_handler = None
        
        self._setup_driver()
    
    def _setup_driver(self):
        """브라우저 드라이버 설정"""
        options = ChromeOptions()
        
        # 헤드리스 모드 설정 (사용자 로그인 시에는 GUI 필요)
        if self.config.get('headless', False):
            options.add_argument('--headless')
        
        # 성능 최적화 옵션
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-images')  # 이미지 로딩 차단
        options.add_argument('--disable-javascript')  # 필요시 JavaScript 차단
        options.add_argument('--window-size=1920,1080')
        
        # 메모리 사용량 최적화
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.adaptive_timeout.get_timeout())
        self.login_detector = LoginDetector(self.driver)
        self.auto_input_handler = AutoInputHandler(self.driver, self.config_manager)
    
    def start_automation(self, reservation_info: Dict) -> bool:
        """자동화 프로세스 시작"""
        try:
            logger.info("G4K 방문예약 자동화 시작")
            
            # 1. 사이트 접속
            if not self._navigate_to_site():
                return False
            
            # 2. 사용자 로그인 대기
            if not self._wait_for_user_login():
                return False
            
            # 3. 예약 프로세스 자동화
            return self._automate_reservation_process(reservation_info)
            
        except Exception as e:
            logger.error(f"자동화 프로세스 중 오류 발생: {e}")
            return False
        finally:
            self._cleanup()
    
    def _navigate_to_site(self) -> bool:
        """G4K 사이트 접속"""
        try:
            url = "https://www.g4k.go.kr/biz/main/main.do"
            logger.info(f"사이트 접속: {url}")
            
            def navigate():
                self.driver.get(url)
                return True
            
            result, response_time = self.retry_manager.execute_with_retry(navigate)
            self.network_monitor.record_response_time(response_time)
            self.adaptive_timeout.update_timeout(response_time)
            
            return result
            
        except Exception as e:
            logger.error(f"사이트 접속 실패: {e}")
            self.network_monitor.record_error()
            return False
    
    def _wait_for_user_login(self) -> bool:
        """사용자 로그인 완료 대기"""
        try:
            # 사용자에게 로그인 안내
            print("\n" + "="*50)
            print("사용자 로그인이 필요합니다.")
            print("브라우저에서 G4K 사이트에 로그인해 주세요.")
            print("로그인 완료 후 자동으로 다음 단계가 진행됩니다.")
            print("="*50 + "\n")
            
            # 로그인 완료 대기
            return self.login_detector.wait_for_login_completion()
            
        except Exception as e:
            logger.error(f"로그인 대기 중 오류: {e}")
            return False
    
    def _automate_reservation_process(self, reservation_info: Dict) -> bool:
        """예약 프로세스 자동화"""
        try:
            logger.info("예약 프로세스 자동화 시작")
            
            # 설정 검증
            validation = self.config_manager.validate_config()
            if validation['errors']:
                logger.error("설정 오류가 발견되었습니다:")
                for error in validation['errors']:
                    logger.error(f"  - {error}")
                return False
            
            if validation['warnings']:
                logger.warning("설정 경고:")
                for warning in validation['warnings']:
                    logger.warning(f"  - {warning}")
            
            # 서버 과부하 상태 확인
            if self.network_monitor.is_server_overloaded():
                logger.warning("서버 과부하 감지. 대기 시간을 늘립니다.")
                time.sleep(30)
            
            # 자동 입력 처리 실행
            if self.auto_input_handler:
                logger.info("자동 입력 처리 시작")
                return self.auto_input_handler.execute_full_auto_input()
            else:
                logger.warning("자동 입력 핸들러가 초기화되지 않았습니다. 기존 방식으로 진행합니다.")
                return self._legacy_reservation_process(reservation_info)
            
        except Exception as e:
            logger.error(f"예약 프로세스 자동화 중 오류: {e}")
            return False
    
    def _legacy_reservation_process(self, reservation_info: Dict) -> bool:
        """기존 예약 프로세스 (하위 호환성)"""
        try:
            logger.info("기존 예약 프로세스 시작")
            
            # 1단계: 방문예약 페이지로 이동
            if not self._navigate_to_reservation_page(reservation_info.get('center_type', 'gwanghwamun')):
                return False
            
            # 2단계: 주의사항 동의
            if not self._accept_terms():
                return False
            
            # 3단계: 센터 선택 (이미 선택됨)
            logger.info("센터 선택 완료")
            
            # 4단계: 서비스 및 날짜/시간 선택
            if not self._select_service_and_datetime(reservation_info):
                return False
            
            # 5단계: 신청자 정보 입력
            if not self._fill_applicant_info(reservation_info.get('applicant_info', {})):
                return False
            
            # 6단계: 최종 확인 및 제출
            if not self._submit_reservation():
                return False
            
            logger.info("기존 예약 프로세스 완료")
            return True
            
        except Exception as e:
            logger.error(f"기존 예약 프로세스 중 오류: {e}")
            return False
    
    def _navigate_to_reservation_page(self, center_type: str) -> bool:
        """방문예약 페이지로 이동"""
        try:
            if center_type == 'gwanghwamun':
                link_text = "광화문 센터방문예약"
            else:
                link_text = "재외공관방문예약"
            
            def click_reservation_link():
                link = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{link_text}')]"))
                )
                link.click()
                return True
            
            result, response_time = self.retry_manager.execute_with_retry(click_reservation_link)
            self.network_monitor.record_response_time(response_time)
            
            logger.info(f"{link_text} 페이지로 이동 완료")
            return result
            
        except Exception as e:
            logger.error(f"예약 페이지 이동 실패: {e}")
            self.network_monitor.record_error()
            return False
    
    def _accept_terms(self) -> bool:
        """주의사항 동의"""
        try:
            def accept_terms():
                # 주의사항 체크박스 클릭
                checkbox = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), '주의사항을 모두 확인')]"))
                )
                checkbox.click()
                
                # 신청하기 버튼 클릭
                submit_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '신청하기')]"))
                )
                submit_btn.click()
                
                return True
            
            result, response_time = self.retry_manager.execute_with_retry(accept_terms)
            self.network_monitor.record_response_time(response_time)
            
            logger.info("주의사항 동의 완료")
            return result
            
        except Exception as e:
            logger.error(f"주의사항 동의 실패: {e}")
            self.network_monitor.record_error()
            return False
    
    def _select_service_and_datetime(self, reservation_info: Dict) -> bool:
        """서비스 및 날짜/시간 선택"""
        try:
            # 서비스 선택
            service_type = reservation_info.get('service_type', 'drivers_license')
            if not self._select_service(service_type):
                return False
            
            # 날짜 선택
            preferred_dates = reservation_info.get('preferred_dates', [])
            if not self._select_date(preferred_dates):
                return False
            
            # 시간 선택
            preferred_times = reservation_info.get('preferred_times', [])
            if not self._select_time(preferred_times):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"서비스/날짜/시간 선택 실패: {e}")
            return False
    
    def _select_service(self, service_type: str) -> bool:
        """서비스 유형 선택"""
        try:
            def select_service():
                if service_type == 'drivers_license':
                    service_text = "운전면허"
                else:
                    service_text = service_type
                
                service_element = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{service_text}')]"))
                )
                service_element.click()
                return True
            
            result, response_time = self.retry_manager.execute_with_retry(select_service)
            self.network_monitor.record_response_time(response_time)
            
            logger.info(f"서비스 선택 완료: {service_type}")
            return result
            
        except Exception as e:
            logger.error(f"서비스 선택 실패: {e}")
            self.network_monitor.record_error()
            return False
    
    def _select_date(self, preferred_dates: List[str]) -> bool:
        """날짜 선택"""
        try:
            for date in preferred_dates:
                try:
                    def select_date():
                        # 달력에서 날짜 클릭
                        date_element = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, f"//td[@data-date='{date}' and not(contains(@class, 'disabled'))]"))
                        )
                        date_element.click()
                        return True
                    
                    result, response_time = self.retry_manager.execute_with_retry(select_date)
                    self.network_monitor.record_response_time(response_time)
                    
                    logger.info(f"날짜 선택 완료: {date}")
                    return result
                    
                except Exception as e:
                    logger.warning(f"날짜 {date} 선택 실패, 다음 날짜 시도: {e}")
                    continue
            
            logger.error("모든 희망 날짜 선택 실패")
            return False
            
        except Exception as e:
            logger.error(f"날짜 선택 중 오류: {e}")
            return False
    
    def _select_time(self, preferred_times: List[str]) -> bool:
        """시간 선택"""
        try:
            # 시간 슬롯 로딩 대기
            time.sleep(3)
            
            for time_slot in preferred_times:
                try:
                    def select_time():
                        time_element = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, f"//div[@data-time='{time_slot}' and not(contains(@class, 'disabled'))]"))
                        )
                        time_element.click()
                        return True
                    
                    result, response_time = self.retry_manager.execute_with_retry(select_time)
                    self.network_monitor.record_response_time(response_time)
                    
                    logger.info(f"시간 선택 완료: {time_slot}")
                    return result
                    
                except Exception as e:
                    logger.warning(f"시간 {time_slot} 선택 실패, 다음 시간 시도: {e}")
                    continue
            
            logger.error("모든 희망 시간 선택 실패")
            return False
            
        except Exception as e:
            logger.error(f"시간 선택 중 오류: {e}")
            return False
    
    def _fill_applicant_info(self, applicant_info: Dict) -> bool:
        """신청자 정보 입력"""
        try:
            def fill_info():
                # 이름 입력
                if 'name' in applicant_info:
                    name_input = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='성명' or @name='name']"))
                    )
                    name_input.clear()
                    name_input.send_keys(applicant_info['name'])
                
                # 연락처 입력
                if 'phone' in applicant_info:
                    phone_input = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='연락처' or @name='phone']"))
                    )
                    phone_input.clear()
                    phone_input.send_keys(applicant_info['phone'])
                
                return True
            
            result, response_time = self.retry_manager.execute_with_retry(fill_info)
            self.network_monitor.record_response_time(response_time)
            
            logger.info("신청자 정보 입력 완료")
            return result
            
        except Exception as e:
            logger.error(f"신청자 정보 입력 실패: {e}")
            self.network_monitor.record_error()
            return False
    
    def _submit_reservation(self) -> bool:
        """예약 신청 제출"""
        try:
            def submit():
                submit_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '신청') or contains(text(), '제출') or contains(text(), '완료')]"))
                )
                submit_btn.click()
                
                # 제출 완료 확인
                time.sleep(5)
                success_elements = self.driver.find_elements(By.XPATH, "//div[contains(text(), '완료') or contains(text(), '성공')]")
                if success_elements:
                    return True
                else:
                    raise Exception("제출 완료 확인 실패")
            
            result, response_time = self.retry_manager.execute_with_retry(submit)
            self.network_monitor.record_response_time(response_time)
            
            logger.info("예약 신청 제출 완료")
            return result
            
        except Exception as e:
            logger.error(f"예약 신청 제출 실패: {e}")
            self.network_monitor.record_error()
            return False
    
    def _cleanup(self):
        """리소스 정리"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("브라우저 종료 완료")
        except Exception as e:
            logger.error(f"리소스 정리 중 오류: {e}")


def main():
    """메인 함수"""
    # 설정 정보
    config = {
        'headless': False,  # 사용자 로그인을 위해 GUI 모드 사용
        'timeout': 30
    }
    
    # 예약 정보
    reservation_info = {
        'center_type': 'gwanghwamun',
        'service_type': 'drivers_license',
        'preferred_dates': ['2024-01-15', '2024-01-16', '2024-01-17'],
        'preferred_times': ['09:00', '10:00', '14:00'],
        'applicant_info': {
            'name': '홍길동',
            'phone': '010-1234-5678'
        }
    }
    
    # 자동화 실행
    automator = ReservationAutomator(config)
    success = automator.start_automation(reservation_info)
    
    if success:
        print("\n✅ 예약 신청이 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 예약 신청 중 오류가 발생했습니다. 로그를 확인해 주세요.")


if __name__ == "__main__":
    main()


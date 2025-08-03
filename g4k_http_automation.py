#!/usr/bin/env python3
"""
G4K 방문예약 HTTP 직접 요청 자동화 시스템
세션 쿠키를 활용하여 브라우저 없이 순수 HTTP 요청으로 예약 처리
"""

import requests
import json
import time
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import hashlib
import base64

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('g4k_http_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SessionManager:
    """세션 쿠키 관리 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.g4k.go.kr"
        self.csrf_token = None
        self.session_id = None
        self.user_info = {}
        
        # 기본 헤더 설정
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
    
    def import_session_from_browser(self, cookies_dict: Dict[str, str]) -> bool:
        """브라우저에서 추출한 쿠키로 세션 설정"""
        try:
            logger.info("브라우저 세션 정보 가져오기 시작")
            
            # 쿠키 설정
            for name, value in cookies_dict.items():
                self.session.cookies.set(name, value, domain='.g4k.go.kr')
            
            # 세션 유효성 검증
            if self._validate_session():
                logger.info("세션 가져오기 성공")
                return True
            else:
                logger.error("세션 유효성 검증 실패")
                return False
                
        except Exception as e:
            logger.error(f"세션 가져오기 실패: {e}")
            return False
    
    def import_session_from_selenium(self, driver) -> bool:
        """Selenium WebDriver에서 세션 추출"""
        try:
            logger.info("Selenium에서 세션 추출 시작")
            
            # 현재 URL이 G4K 사이트인지 확인
            current_url = driver.current_url
            if 'g4k.go.kr' not in current_url:
                logger.error("G4K 사이트가 아닙니다")
                return False
            
            # 쿠키 추출
            cookies = driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(
                    cookie['name'], 
                    cookie['value'], 
                    domain=cookie.get('domain', '.g4k.go.kr'),
                    path=cookie.get('path', '/'),
                    secure=cookie.get('secure', False)
                )
            
            # 현재 페이지에서 CSRF 토큰 추출
            page_source = driver.page_source
            self._extract_csrf_token(page_source)
            
            # 세션 유효성 검증
            if self._validate_session():
                logger.info("Selenium 세션 추출 성공")
                return True
            else:
                logger.error("세션 유효성 검증 실패")
                return False
                
        except Exception as e:
            logger.error(f"Selenium 세션 추출 실패: {e}")
            return False
    
    def _validate_session(self) -> bool:
        """세션 유효성 검증"""
        try:
            # 인증이 필요한 페이지에 요청
            response = self.session.get(f"{self.base_url}/biz/main/main.do")
            
            if response.status_code == 200:
                # 로그인 상태 확인
                if '로그아웃' in response.text or 'logout' in response.text.lower():
                    logger.info("세션 유효성 확인됨")
                    return True
                elif '로그인' in response.text or 'login' in response.text.lower():
                    logger.warning("로그인이 필요한 상태")
                    return False
            
            logger.warning(f"예상치 못한 응답: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"세션 검증 중 오류: {e}")
            return False
    
    def _extract_csrf_token(self, html_content: str) -> bool:
        """HTML에서 CSRF 토큰 추출"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 메타 태그에서 CSRF 토큰 찾기
            csrf_meta = soup.find('meta', {'name': 'csrf-token'}) or \
                       soup.find('meta', {'name': '_csrf'}) or \
                       soup.find('meta', {'name': 'csrf_token'})
            
            if csrf_meta:
                self.csrf_token = csrf_meta.get('content')
                logger.info("CSRF 토큰 추출 성공")
                return True
            
            # 숨겨진 입력 필드에서 CSRF 토큰 찾기
            csrf_input = soup.find('input', {'name': '_token'}) or \
                        soup.find('input', {'name': 'csrf_token'}) or \
                        soup.find('input', {'name': '_csrf'})
            
            if csrf_input:
                self.csrf_token = csrf_input.get('value')
                logger.info("CSRF 토큰 추출 성공 (input)")
                return True
            
            logger.warning("CSRF 토큰을 찾을 수 없음")
            return False
            
        except Exception as e:
            logger.error(f"CSRF 토큰 추출 실패: {e}")
            return False


class G4KHttpAutomator:
    """G4K HTTP 직접 요청 자동화 클래스"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.session = session_manager.session
        self.base_url = session_manager.base_url
        
        # 예약 관련 정보 저장
        self.reservation_data = {}
        self.available_dates = []
        self.available_times = []
        
    def start_reservation_process(self, reservation_info: Dict) -> bool:
        """예약 프로세스 시작"""
        try:
            logger.info("HTTP 기반 예약 프로세스 시작")
            
            # 1단계: 방문예약 페이지 접근
            if not self._access_reservation_page(reservation_info.get('center_type', 'gwanghwamun')):
                return False
            
            # 2단계: 주의사항 동의
            if not self._accept_terms():
                return False
            
            # 3단계: 서비스 선택
            if not self._select_service(reservation_info.get('service_type', 'drivers_license')):
                return False
            
            # 4단계: 날짜 및 시간 선택
            if not self._select_datetime(reservation_info):
                return False
            
            # 5단계: 신청자 정보 입력
            if not self._fill_applicant_info(reservation_info.get('applicant_info', {})):
                return False
            
            # 6단계: 최종 제출
            if not self._submit_reservation():
                return False
            
            logger.info("예약 프로세스 완료!")
            return True
            
        except Exception as e:
            logger.error(f"예약 프로세스 중 오류: {e}")
            return False
    
    def _access_reservation_page(self, center_type: str) -> bool:
        """방문예약 페이지 접근"""
        try:
            if center_type == 'gwanghwamun':
                url = f"{self.base_url}/biz/visit/gwanghwamun/main.do"
            else:
                url = f"{self.base_url}/biz/visit/embassy/main.do"
            
            logger.info(f"예약 페이지 접근: {url}")
            
            response = self.session.get(url)
            if response.status_code == 200:
                # 페이지에서 필요한 정보 추출
                self.session_manager._extract_csrf_token(response.text)
                logger.info("예약 페이지 접근 성공")
                return True
            else:
                logger.error(f"예약 페이지 접근 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"예약 페이지 접근 중 오류: {e}")
            return False
    
    def _accept_terms(self) -> bool:
        """주의사항 동의 처리"""
        try:
            logger.info("주의사항 동의 처리")
            
            # 주의사항 동의 요청 구성
            data = {
                'agree': 'Y',
                'terms_check': 'on'
            }
            
            if self.session_manager.csrf_token:
                data['_token'] = self.session_manager.csrf_token
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': self.session.get(f"{self.base_url}/biz/visit/gwanghwamun/main.do").url
            }
            
            response = self.session.post(
                f"{self.base_url}/biz/visit/gwanghwamun/terms.do",
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info("주의사항 동의 완료")
                return True
            else:
                logger.error(f"주의사항 동의 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"주의사항 동의 중 오류: {e}")
            return False
    
    def _select_service(self, service_type: str) -> bool:
        """서비스 선택"""
        try:
            logger.info(f"서비스 선택: {service_type}")
            
            # 서비스 코드 매핑
            service_codes = {
                'drivers_license': 'DL001',
                'passport': 'PP001',
                'id_card': 'ID001',
                'certificate': 'CT001'
            }
            
            service_code = service_codes.get(service_type, 'DL001')
            
            data = {
                'service_code': service_code,
                'service_type': service_type
            }
            
            if self.session_manager.csrf_token:
                data['_token'] = self.session_manager.csrf_token
            
            response = self.session.post(
                f"{self.base_url}/biz/visit/gwanghwamun/selectService.do",
                data=data
            )
            
            if response.status_code == 200:
                logger.info("서비스 선택 완료")
                return True
            else:
                logger.error(f"서비스 선택 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"서비스 선택 중 오류: {e}")
            return False
    
    def _get_available_dates(self, service_code: str) -> List[str]:
        """가용 날짜 조회"""
        try:
            logger.info("가용 날짜 조회")
            
            # AJAX 요청으로 가용 날짜 조회
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            params = {
                'service_code': service_code,
                'year': datetime.now().year,
                'month': datetime.now().month
            }
            
            response = self.session.get(
                f"{self.base_url}/api/visit/available-dates",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                available_dates = data.get('available_dates', [])
                logger.info(f"가용 날짜 {len(available_dates)}개 조회됨")
                return available_dates
            else:
                logger.error(f"가용 날짜 조회 실패: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"가용 날짜 조회 중 오류: {e}")
            return []
    
    def _get_available_times(self, date: str, service_code: str) -> List[str]:
        """특정 날짜의 가용 시간 조회"""
        try:
            logger.info(f"가용 시간 조회: {date}")
            
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            params = {
                'date': date,
                'service_code': service_code
            }
            
            response = self.session.get(
                f"{self.base_url}/api/visit/available-times",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                available_times = data.get('available_times', [])
                logger.info(f"가용 시간 {len(available_times)}개 조회됨")
                return available_times
            else:
                logger.error(f"가용 시간 조회 실패: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"가용 시간 조회 중 오류: {e}")
            return []
    
    def _select_datetime(self, reservation_info: Dict) -> bool:
        """날짜 및 시간 선택"""
        try:
            logger.info("날짜 및 시간 선택")
            
            service_code = 'DL001'  # 임시 코드
            preferred_dates = reservation_info.get('preferred_dates', [])
            preferred_times = reservation_info.get('preferred_times', [])
            
            # 가용 날짜 조회
            available_dates = self._get_available_dates(service_code)
            
            selected_date = None
            selected_time = None
            
            # 희망 날짜 중 가용한 날짜 찾기
            for date in preferred_dates:
                if date in available_dates:
                    # 해당 날짜의 가용 시간 조회
                    available_times = self._get_available_times(date, service_code)
                    
                    # 희망 시간 중 가용한 시간 찾기
                    for time_slot in preferred_times:
                        if time_slot in available_times:
                            selected_date = date
                            selected_time = time_slot
                            break
                    
                    if selected_date and selected_time:
                        break
            
            if not selected_date or not selected_time:
                logger.error("가용한 날짜/시간을 찾을 수 없음")
                return False
            
            # 날짜/시간 선택 요청
            data = {
                'selected_date': selected_date,
                'selected_time': selected_time,
                'service_code': service_code
            }
            
            if self.session_manager.csrf_token:
                data['_token'] = self.session_manager.csrf_token
            
            response = self.session.post(
                f"{self.base_url}/biz/visit/gwanghwamun/selectDateTime.do",
                data=data
            )
            
            if response.status_code == 200:
                self.reservation_data.update({
                    'selected_date': selected_date,
                    'selected_time': selected_time
                })
                logger.info(f"날짜/시간 선택 완료: {selected_date} {selected_time}")
                return True
            else:
                logger.error(f"날짜/시간 선택 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"날짜/시간 선택 중 오류: {e}")
            return False
    
    def _fill_applicant_info(self, applicant_info: Dict) -> bool:
        """신청자 정보 입력"""
        try:
            logger.info("신청자 정보 입력")
            
            data = {
                'name': applicant_info.get('name', ''),
                'name_english': applicant_info.get('name_english', ''),
                'phone': applicant_info.get('phone', ''),
                'email': applicant_info.get('email', ''),
                'id_type': applicant_info.get('id_type', 'passport'),
                'id_number': applicant_info.get('id_number', ''),
                'birth_date': applicant_info.get('birth_date', ''),
                'nationality': applicant_info.get('nationality', 'KR')
            }
            
            # 이전 단계 정보 포함
            data.update(self.reservation_data)
            
            if self.session_manager.csrf_token:
                data['_token'] = self.session_manager.csrf_token
            
            response = self.session.post(
                f"{self.base_url}/biz/visit/gwanghwamun/applicantInfo.do",
                data=data
            )
            
            if response.status_code == 200:
                logger.info("신청자 정보 입력 완료")
                return True
            else:
                logger.error(f"신청자 정보 입력 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"신청자 정보 입력 중 오류: {e}")
            return False
    
    def _submit_reservation(self) -> bool:
        """최종 예약 제출"""
        try:
            logger.info("최종 예약 제출")
            
            data = self.reservation_data.copy()
            data['final_submit'] = 'Y'
            
            if self.session_manager.csrf_token:
                data['_token'] = self.session_manager.csrf_token
            
            response = self.session.post(
                f"{self.base_url}/biz/visit/gwanghwamun/submit.do",
                data=data
            )
            
            if response.status_code == 200:
                # 성공 응답 확인
                if '예약이 완료' in response.text or '신청이 완료' in response.text:
                    # 예약 번호 추출
                    reservation_number = self._extract_reservation_number(response.text)
                    if reservation_number:
                        logger.info(f"예약 완료! 예약번호: {reservation_number}")
                    else:
                        logger.info("예약 완료!")
                    return True
                else:
                    logger.error("예약 제출 후 성공 확인 실패")
                    return False
            else:
                logger.error(f"예약 제출 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"예약 제출 중 오류: {e}")
            return False
    
    def _extract_reservation_number(self, html_content: str) -> Optional[str]:
        """HTML에서 예약 번호 추출"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 예약 번호 패턴 찾기
            patterns = [
                r'예약번호[:\s]*([A-Z0-9\-]+)',
                r'신청번호[:\s]*([A-Z0-9\-]+)',
                r'접수번호[:\s]*([A-Z0-9\-]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html_content)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"예약 번호 추출 중 오류: {e}")
            return None


class CookieExtractor:
    """브라우저에서 쿠키 추출을 위한 유틸리티 클래스"""
    
    @staticmethod
    def extract_from_selenium(driver) -> Dict[str, str]:
        """Selenium WebDriver에서 쿠키 추출"""
        cookies_dict = {}
        try:
            cookies = driver.get_cookies()
            for cookie in cookies:
                cookies_dict[cookie['name']] = cookie['value']
            return cookies_dict
        except Exception as e:
            logger.error(f"Selenium 쿠키 추출 실패: {e}")
            return {}
    
    @staticmethod
    def extract_from_browser_export(cookie_string: str) -> Dict[str, str]:
        """브라우저에서 내보낸 쿠키 문자열 파싱"""
        cookies_dict = {}
        try:
            # 쿠키 문자열 파싱 (name=value; name2=value2 형식)
            cookie_pairs = cookie_string.split(';')
            for pair in cookie_pairs:
                if '=' in pair:
                    name, value = pair.strip().split('=', 1)
                    cookies_dict[name] = value
            return cookies_dict
        except Exception as e:
            logger.error(f"쿠키 문자열 파싱 실패: {e}")
            return {}
    
    @staticmethod
    def save_cookies_to_file(cookies_dict: Dict[str, str], filename: str):
        """쿠키를 파일에 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(cookies_dict, f, indent=2, ensure_ascii=False)
            logger.info(f"쿠키 저장 완료: {filename}")
        except Exception as e:
            logger.error(f"쿠키 저장 실패: {e}")
    
    @staticmethod
    def load_cookies_from_file(filename: str) -> Dict[str, str]:
        """파일에서 쿠키 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                cookies_dict = json.load(f)
            logger.info(f"쿠키 로드 완료: {filename}")
            return cookies_dict
        except Exception as e:
            logger.error(f"쿠키 로드 실패: {e}")
            return {}


def main():
    """메인 함수 - 사용 예시"""
    
    # 1. 세션 매니저 초기화
    session_manager = SessionManager()
    
    # 2. 쿠키 방식 선택 (여러 방법 중 하나 선택)
    
    # 방법 1: Selenium에서 직접 추출 (권장)
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    
    try:
        # 사용자가 수동으로 로그인할 수 있도록 브라우저 열기
        driver.get("https://www.g4k.go.kr/biz/main/main.do")
        
        print("\n" + "="*60)
        print("브라우저에서 G4K 사이트에 로그인해 주세요.")
        print("로그인 완료 후 Enter 키를 눌러주세요.")
        print("="*60)
        input("로그인 완료 후 Enter 키를 눌러주세요...")
        
        # 세션 추출
        if session_manager.import_session_from_selenium(driver):
            print("✅ 세션 추출 성공!")
        else:
            print("❌ 세션 추출 실패!")
            return
            
    finally:
        driver.quit()
    
    # 방법 2: 저장된 쿠키 파일 사용
    # cookies_dict = CookieExtractor.load_cookies_from_file('g4k_cookies.json')
    # session_manager.import_session_from_browser(cookies_dict)
    
    # 방법 3: 수동으로 쿠키 입력
    # cookie_string = input("브라우저에서 복사한 쿠키 문자열을 입력하세요: ")
    # cookies_dict = CookieExtractor.extract_from_browser_export(cookie_string)
    # session_manager.import_session_from_browser(cookies_dict)
    
    # 3. 자동화 시스템 초기화
    automator = G4KHttpAutomator(session_manager)
    
    # 4. 예약 정보 설정
    reservation_info = {
        'center_type': 'gwanghwamun',
        'service_type': 'drivers_license',
        'preferred_dates': ['2024-01-15', '2024-01-16', '2024-01-17'],
        'preferred_times': ['09:00', '10:00', '14:00'],
        'applicant_info': {
            'name': '홍길동',
            'name_english': 'Hong Gildong',
            'phone': '010-1234-5678',
            'email': 'hong@example.com',
            'id_type': 'passport',
            'id_number': 'M12345678',
            'birth_date': '1990-01-01',
            'nationality': 'KR'
        }
    }
    
    # 5. 예약 프로세스 실행
    print("\n🚀 HTTP 기반 예약 자동화 시작...")
    success = automator.start_reservation_process(reservation_info)
    
    if success:
        print("\n✅ 예약이 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 예약 중 오류가 발생했습니다. 로그를 확인해 주세요.")


if __name__ == "__main__":
    main()


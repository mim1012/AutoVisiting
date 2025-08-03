#!/usr/bin/env python3
"""
G4K 스텔스 브라우저 모듈
404 에러 및 봇 탐지 우회 기능
"""

import os
import time
import random
import subprocess
import logging
from typing import Optional, Dict, Any

try:
    import undetected_chromedriver as uc
    UNDETECTED_AVAILABLE = True
except ImportError:
    UNDETECTED_AVAILABLE = False
    import warnings
    warnings.warn("undetected-chromedriver not installed. Using standard selenium.")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException

logger = logging.getLogger(__name__)


class StealthBrowser:
    """봇 탐지 우회 브라우저 클래스"""
    
    def __init__(self, use_debug_port: bool = True):
        self.driver = None
        self.use_debug_port = use_debug_port
        self.debug_port = 9222
        self.chrome_process = None
        
    def create_driver(self) -> webdriver.Chrome:
        """스텔스 드라이버 생성"""
        try:
            if self.use_debug_port:
                return self._create_debug_driver()
            elif UNDETECTED_AVAILABLE:
                return self._create_undetected_driver()
            else:
                return self._create_standard_driver()
        except Exception as e:
            logger.error(f"드라이버 생성 실패: {e}")
            raise
    
    def _create_debug_driver(self) -> webdriver.Chrome:
        """디버깅 포트를 사용한 드라이버 생성"""
        # Chrome 프로세스 실행
        chrome_path = self._find_chrome_path()
        user_data_dir = os.path.join(os.environ['TEMP'], 'chrome_debug_profile')
        
        cmd = [
            chrome_path,
            f'--remote-debugging-port={self.debug_port}',
            f'--user-data-dir={user_data_dir}',
            '--no-first-run',
            '--no-default-browser-check'
        ]
        
        self.chrome_process = subprocess.Popen(cmd)
        time.sleep(3)  # Chrome 시작 대기
        
        # 디버깅 포트에 연결
        if UNDETECTED_AVAILABLE:
            options = uc.ChromeOptions()
        else:
            options = webdriver.ChromeOptions()
            
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
        
        if UNDETECTED_AVAILABLE:
            driver = uc.Chrome(options=options)
        else:
            driver = webdriver.Chrome(options=options)
            
        # 탐지 우회 스크립트 주입
        self._inject_stealth_scripts(driver)
        
        return driver
    
    def _create_undetected_driver(self) -> uc.Chrome:
        """Undetected ChromeDriver 생성"""
        options = uc.ChromeOptions()
        
        # 필수 옵션
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 사용자 에이전트
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = uc.Chrome(options=options, version_main=120)
        self._inject_stealth_scripts(driver)
        
        return driver
    
    def _create_standard_driver(self) -> webdriver.Chrome:
        """표준 Chrome 드라이버 (폴백)"""
        options = webdriver.ChromeOptions()
        
        # 자동화 플래그 제거 시도
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        driver = webdriver.Chrome(options=options)
        self._inject_stealth_scripts(driver)
        
        return driver
    
    def _inject_stealth_scripts(self, driver):
        """탐지 우회 스크립트 주입"""
        stealth_js = """
        // navigator.webdriver 제거
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Chrome 자동화 플래그 제거
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // 언어 설정
        Object.defineProperty(navigator, 'languages', {
            get: () => ['ko-KR', 'ko', 'en']
        });
        
        // 플랫폼 설정
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });
        
        // WebGL 벤더
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter(parameter);
        };
        
        // 개발자 도구 감지 무력화
        let devtools = {open: false, orientation: null};
        const threshold = 160;
        const emitEvent = (state, orientation) => {};
        
        // 우클릭 활성화
        document.addEventListener('contextmenu', e => e.stopPropagation(), true);
        
        // F12 활성화
        document.addEventListener('keydown', e => {
            if(e.keyCode === 123) e.stopPropagation();
        }, true);
        """
        
        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': stealth_js
            })
        except:
            # CDP가 지원되지 않는 경우 일반 스크립트 실행
            driver.execute_script(stealth_js)
    
    def _find_chrome_path(self) -> str:
        """Chrome 실행 파일 경로 찾기"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        raise FileNotFoundError("Chrome 실행 파일을 찾을 수 없습니다")
    
    def human_like_delay(self, min_sec: float = 0.5, max_sec: float = 2.0):
        """인간같은 지연 시간"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
    
    def human_like_click(self, driver, element):
        """인간같은 클릭 동작"""
        # 요소가 보일 때까지 스크롤
        driver.execute_script("""
            arguments[0].scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        """, element)
        
        self.human_like_delay(0.3, 0.8)
        
        # 마우스 움직임 시뮬레이션
        action = ActionChains(driver)
        
        # 랜덤 위치에서 시작
        action.move_by_offset(random.randint(0, 100), random.randint(0, 100))
        
        # 베지어 곡선 움직임 (여러 포인트를 거쳐 이동)
        for _ in range(random.randint(3, 5)):
            action.move_by_offset(
                random.randint(-50, 50),
                random.randint(-50, 50)
            )
        
        # 요소로 이동 (약간의 오프셋 포함)
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        action.move_to_element_with_offset(element, offset_x, offset_y)
        
        # 클릭 전 짧은 대기
        action.pause(random.uniform(0.1, 0.3))
        
        # 클릭
        action.click()
        
        action.perform()
    
    def human_like_type(self, element, text: str):
        """인간같은 타이핑"""
        element.clear()
        
        for char in text:
            element.send_keys(char)
            # 타이핑 속도 변화
            delay = random.uniform(0.05, 0.3)
            
            # 가끔 더 긴 멈춤 (생각하는 것처럼)
            if random.random() < 0.1:
                delay = random.uniform(0.5, 1.0)
                
            time.sleep(delay)
    
    def safe_page_load(self, driver, url: str) -> bool:
        """안전한 페이지 로드"""
        try:
            # 메인 페이지 먼저 방문
            logger.info("메인 페이지 방문")
            driver.get("https://www.g4k.go.kr")
            self.human_like_delay(2, 4)
            
            # 페이지 완전 로드 대기
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 쿠키 확인
            cookies = driver.get_cookies()
            logger.info(f"쿠키 수: {len(cookies)}")
            
            # 목표 페이지로 이동
            logger.info(f"목표 페이지 이동: {url}")
            driver.get(url)
            
            # 다시 완전 로드 대기
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 404 체크
            if "404" in driver.title or "오류" in driver.title:
                logger.error("404 에러 감지")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"페이지 로드 실패: {e}")
            return False
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            
        if self.chrome_process:
            self.chrome_process.terminate()
            time.sleep(1)
            if self.chrome_process.poll() is None:
                self.chrome_process.kill()


class G4KStealthAutomation:
    """G4K 스텔스 자동화 메인 클래스"""
    
    def __init__(self):
        self.browser = StealthBrowser(use_debug_port=True)
        self.driver = None
        
    def initialize(self) -> bool:
        """초기화"""
        try:
            logger.info("스텔스 브라우저 초기화 시작")
            self.driver = self.browser.create_driver()
            logger.info("스텔스 브라우저 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"초기화 실패: {e}")
            return False
    
    def login_wait(self) -> bool:
        """사용자 로그인 대기"""
        print("\n" + "="*50)
        print("G4K 사이트에서 수동으로 로그인해주세요.")
        print("로그인 완료 후 Enter 키를 눌러주세요...")
        print("="*50)
        
        input()
        
        # 로그인 확인
        try:
            # 로그아웃 버튼이나 마이페이지 요소 확인
            logout_elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "로그아웃")
            if logout_elements:
                logger.info("로그인 확인됨")
                return True
            else:
                logger.warning("로그인 상태를 확인할 수 없습니다")
                return False
        except Exception as e:
            logger.error(f"로그인 확인 실패: {e}")
            return False
    
    def navigate_to_reservation(self) -> bool:
        """예약 페이지로 안전하게 이동"""
        try:
            # 여러 경로 시도
            reservation_urls = [
                "https://www.g4k.go.kr/reservation/main",
                "https://www.g4k.go.kr/biz/visit/gwanghwamun/main.do",
                "https://www.g4k.go.kr/visit/reservation"
            ]
            
            for url in reservation_urls:
                logger.info(f"예약 페이지 시도: {url}")
                if self.browser.safe_page_load(self.driver, url):
                    return True
                    
                self.browser.human_like_delay(2, 3)
            
            return False
            
        except Exception as e:
            logger.error(f"예약 페이지 이동 실패: {e}")
            return False
    
    def run(self):
        """메인 실행"""
        try:
            # 1. 초기화
            if not self.initialize():
                return
            
            # 2. 메인 페이지 로드
            if not self.browser.safe_page_load(self.driver, "https://www.g4k.go.kr"):
                logger.error("메인 페이지 로드 실패")
                return
            
            # 3. 로그인 대기
            if not self.login_wait():
                return
            
            # 4. 예약 페이지 이동
            if not self.navigate_to_reservation():
                logger.error("예약 페이지 이동 실패")
                return
            
            logger.info("준비 완료! 자동화를 시작할 수 있습니다.")
            
            # 여기서부터 실제 자동화 로직
            # ...
            
        except Exception as e:
            logger.error(f"실행 중 오류: {e}")
        finally:
            input("\n종료하려면 Enter 키를 누르세요...")
            self.browser.close()


if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 실행
    automation = G4KStealthAutomation()
    automation.run()
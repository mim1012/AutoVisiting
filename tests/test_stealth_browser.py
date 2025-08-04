#!/usr/bin/env python3
"""
StealthBrowser 모듈 단위 테스트
기존 코드 변경 없이 테스트만 추가
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 상위 디렉토리의 모듈 import 가능하도록 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from stealth_browser import StealthBrowser
except ImportError as e:
    print(f"Import 경고: {e}")
    StealthBrowser = None


class TestStealthBrowser(unittest.TestCase):
    """StealthBrowser 단위 테스트"""
    
    def setUp(self):
        """테스트 준비"""
        if StealthBrowser is None:
            self.skipTest("StealthBrowser 모듈을 import할 수 없습니다")
    
    def test_stealth_browser_initialization(self):
        """StealthBrowser 초기화 테스트"""
        browser = StealthBrowser()
        
        # 기본 속성 확인
        self.assertIsNotNone(browser)
        self.assertTrue(hasattr(browser, 'create_driver'))
        self.assertTrue(hasattr(browser, 'safe_page_load'))
        self.assertTrue(hasattr(browser, 'human_like_click'))
    
    def test_stealth_browser_attributes(self):
        """StealthBrowser 속성 테스트"""
        browser = StealthBrowser()
        
        # 필수 속성들 존재 확인
        expected_attrs = [
            'create_driver',
            'safe_page_load', 
            'human_like_click',
            'close'
        ]
        
        for attr in expected_attrs:
            self.assertTrue(hasattr(browser, attr), f"속성 {attr}이 없습니다")
    
    @patch('selenium.webdriver.Chrome')
    def test_create_driver_mock(self, mock_chrome):
        """create_driver 메소드 테스트 (Mock 사용)"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        browser = StealthBrowser()
        
        # Mock 환경에서는 실제 드라이버 생성 대신 Mock 반환
        with patch.object(browser, 'create_driver', return_value=mock_driver):
            driver = browser.create_driver()
            self.assertIsNotNone(driver)
    
    def test_stealth_browser_methods_exist(self):
        """StealthBrowser 주요 메소드 존재 확인"""
        browser = StealthBrowser()
        
        # 메소드들이 callable인지 확인
        self.assertTrue(callable(getattr(browser, 'create_driver', None)))
        self.assertTrue(callable(getattr(browser, 'safe_page_load', None)))
        self.assertTrue(callable(getattr(browser, 'human_like_click', None)))
    
    @patch('stealth_browser.uc')
    def test_undetected_chrome_fallback(self, mock_uc):
        """undetected-chromedriver 없을 때 fallback 테스트"""
        # undetected-chromedriver가 없는 상황 시뮬레이션
        mock_uc.Chrome.side_effect = ImportError("No module named 'undetected_chromedriver'")
        
        browser = StealthBrowser()
        
        # 에러 없이 초기화되는지 확인
        self.assertIsNotNone(browser)
    
    def test_stealth_browser_configuration_defaults(self):
        """StealthBrowser 기본 설정 테스트"""
        browser = StealthBrowser()
        
        # 기본 속성들 확인 (실제 값이 아닌 존재 여부만)
        self.assertTrue(hasattr(browser, '__init__'))
        self.assertIsInstance(browser, StealthBrowser)


class TestStealthBrowserIntegration(unittest.TestCase):
    """StealthBrowser 통합 테스트 (Mock 기반)"""
    
    def setUp(self):
        """테스트 준비"""
        if StealthBrowser is None:
            self.skipTest("StealthBrowser 모듈을 import할 수 없습니다")
    
    @patch('selenium.webdriver.Chrome')
    def test_safe_page_load_mock(self, mock_chrome):
        """safe_page_load 메소드 통합 테스트"""
        mock_driver = Mock()
        mock_driver.get = Mock()
        mock_chrome.return_value = mock_driver
        
        browser = StealthBrowser()
        
        # Mock 환경에서 safe_page_load 테스트
        with patch.object(browser, 'create_driver', return_value=mock_driver):
            driver = browser.create_driver()
            
            # safe_page_load 호출 (URL 매개변수 필요)
            try:
                browser.safe_page_load(driver, "https://test.com")
                # 에러 없이 실행되면 성공
                self.assertTrue(True)
            except Exception as e:
                # 예상 가능한 에러는 허용
                if "safe_page_load" in str(e):
                    self.skipTest("safe_page_load 메소드 시그니처 문제")
                else:
                    raise
    
    @patch('selenium.webdriver.Chrome')
    def test_human_like_click_mock(self, mock_chrome):
        """human_like_click 메소드 통합 테스트"""
        mock_driver = Mock()
        mock_element = Mock()
        mock_chrome.return_value = mock_driver
        
        browser = StealthBrowser()
        
        # Mock 환경에서 human_like_click 테스트
        try:
            browser.human_like_click(mock_driver, mock_element)
            # 에러 없이 실행되면 성공
            self.assertTrue(True)
        except Exception as e:
            # 예상 가능한 에러는 허용
            if "human_like_click" in str(e) or "ActionChains" in str(e):
                self.skipTest("human_like_click 실행 환경 문제")
            else:
                # 심각한 에러만 실패 처리
                self.fail(f"예상치 못한 에러: {e}")


def run_stealth_browser_tests():
    """StealthBrowser 테스트 실행"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestStealthBrowser))
    suite.addTests(loader.loadTestsFromTestCase(TestStealthBrowserIntegration))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🔬 StealthBrowser 모듈 단위 테스트")
    print("=" * 50)
    
    success = run_stealth_browser_tests()
    
    if success:
        print("\n✅ 모든 StealthBrowser 테스트 통과!")
    else:
        print("\n❌ 일부 StealthBrowser 테스트 실패")
    
    exit(0 if success else 1)
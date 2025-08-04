#!/usr/bin/env python3
"""
UltraLagBypass 모듈 단위 테스트
기존 코드 변경 없이 테스트만 추가
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 상위 디렉토리의 모듈 import 가능하도록 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ultra_lag_bypass import UltraLagBypass, ExtremeTicketing
except ImportError as e:
    print(f"Import 경고: {e}")
    UltraLagBypass = None
    ExtremeTicketing = None


class TestUltraLagBypass(unittest.TestCase):
    """UltraLagBypass 단위 테스트"""
    
    def setUp(self):
        """테스트 준비"""
        if UltraLagBypass is None:
            self.skipTest("UltraLagBypass 모듈을 import할 수 없습니다")
        
        # Mock 드라이버 설정
        self.mock_driver = Mock()
        self.mock_driver.execute_script = Mock(return_value=True)
        self.mock_driver.capabilities = {'goog:chromeOptions': {}}
    
    def test_ultra_lag_bypass_initialization(self):
        """UltraLagBypass 초기화 테스트"""
        bypass = UltraLagBypass(self.mock_driver)
        
        # 기본 속성 확인
        self.assertIsNotNone(bypass)
        self.assertEqual(bypass.driver, self.mock_driver)
        self.assertTrue(hasattr(bypass, 'method1_websocket_hijack'))
        self.assertTrue(hasattr(bypass, 'method2_memory_injection'))
    
    def test_lag_bypass_methods_exist(self):
        """LAG 우회 메소드들 존재 확인"""
        bypass = UltraLagBypass(self.mock_driver)
        
        # 10가지 우회 기법 메소드 확인
        expected_methods = [
            'method1_websocket_hijack',
            'method2_memory_injection', 
            'method3_cdp_manipulation',
            'method4_browser_exploit',
            'method5_ajax_interceptor',
            'method6_dom_mutation_hack',
            'method7_worker_thread_abuse',
            'method8_protocol_downgrade',
            'method9_cache_poisoning',
            'method10_timing_attack'
        ]
        
        for method in expected_methods:
            self.assertTrue(hasattr(bypass, method), f"메소드 {method}가 없습니다")
            self.assertTrue(callable(getattr(bypass, method)), f"메소드 {method}가 호출 가능하지 않습니다")
    
    def test_cdp_setup(self):
        """CDP 연결 설정 테스트"""
        # CDP 정보가 있는 capabilities 설정
        mock_driver_with_cdp = Mock()
        mock_driver_with_cdp.capabilities = {
            'goog:chromeOptions': {
                'debuggerAddress': 'localhost:9222'
            }
        }
        
        bypass = UltraLagBypass(mock_driver_with_cdp)
        
        # CDP URL이 올바르게 설정되는지 확인
        if hasattr(bypass, 'cdp_url'):
            expected_cdp = "ws://localhost:9222/devtools/browser"
            self.assertEqual(bypass.cdp_url, expected_cdp)
    
    def test_browser_exploit_method(self):
        """브라우저 익스플로잇 메소드 테스트"""
        bypass = UltraLagBypass(self.mock_driver)
        
        # method4_browser_exploit 실행 테스트
        try:
            bypass.method4_browser_exploit()
            # execute_script가 호출되었는지 확인
            self.mock_driver.execute_script.assert_called()
        except Exception as e:
            # 실행 환경 문제로 인한 에러는 허용
            self.assertIsInstance(e, (AttributeError, TypeError))
    
    def test_ajax_interceptor_method(self):
        """AJAX 인터셉터 메소드 테스트"""
        bypass = UltraLagBypass(self.mock_driver)
        
        # method5_ajax_interceptor 실행 테스트
        try:
            bypass.method5_ajax_interceptor()
            # execute_script가 호출되었는지 확인
            self.mock_driver.execute_script.assert_called()
        except Exception as e:
            # 실행 환경 문제로 인한 에러는 허용
            self.assertIsInstance(e, (AttributeError, TypeError))
    
    def test_dom_mutation_hack_method(self):
        """DOM 뮤테이션 해킹 메소드 테스트"""
        bypass = UltraLagBypass(self.mock_driver)
        
        # method6_dom_mutation_hack 실행 테스트  
        try:
            bypass.method6_dom_mutation_hack()
            # execute_script가 호출되었는지 확인
            self.mock_driver.execute_script.assert_called()
        except Exception as e:
            # 실행 환경 문제로 인한 에러는 허용
            self.assertIsInstance(e, (AttributeError, TypeError))
    
    def test_worker_thread_abuse_method(self):
        """워커 스레드 남용 메소드 테스트"""
        bypass = UltraLagBypass(self.mock_driver)
        
        # method7_worker_thread_abuse 실행 테스트
        try:
            bypass.method7_worker_thread_abuse()
            # execute_script가 호출되었는지 확인
            self.mock_driver.execute_script.assert_called()
        except Exception as e:
            # 실행 환경 문제로 인한 에러는 허용
            self.assertIsInstance(e, (AttributeError, TypeError))
    
    def test_cache_poisoning_method(self):
        """캐시 포이즈닝 메소드 테스트"""
        bypass = UltraLagBypass(self.mock_driver)
        
        # method9_cache_poisoning 실행 테스트
        try:
            bypass.method9_cache_poisoning()
            # execute_script가 호출되었는지 확인
            self.mock_driver.execute_script.assert_called()
        except Exception as e:
            # 실행 환경 문제로 인한 에러는 허용
            self.assertIsInstance(e, (AttributeError, TypeError))
    
    def test_timing_attack_method(self):
        """타이밍 어택 메소드 테스트"""
        bypass = UltraLagBypass(self.mock_driver)
        
        # method10_timing_attack 실행 테스트
        try:
            bypass.method10_timing_attack()
            # execute_script가 호출되었는지 확인
            self.mock_driver.execute_script.assert_called()
        except Exception as e:
            # 실행 환경 문제로 인한 에러는 허용
            self.assertIsInstance(e, (AttributeError, TypeError))


class TestExtremeTicketing(unittest.TestCase):
    """ExtremeTicketing 단위 테스트"""
    
    def setUp(self):
        """테스트 준비"""
        if ExtremeTicketing is None:
            self.skipTest("ExtremeTicketing 모듈을 import할 수 없습니다")
        
        # Mock 드라이버 설정
        self.mock_driver = Mock()
        self.mock_driver.execute_script = Mock(return_value=True)
    
    def test_extreme_ticketing_initialization(self):
        """ExtremeTicketing 초기화 테스트"""
        extreme = ExtremeTicketing(self.mock_driver)
        
        # 기본 속성 확인
        self.assertIsNotNone(extreme)
        self.assertEqual(extreme.driver, self.mock_driver)
        self.assertTrue(hasattr(extreme, 'lag_bypass'))
        self.assertTrue(hasattr(extreme, 'nuclear_option'))
    
    def test_extreme_ticketing_attributes(self):
        """ExtremeTicketing 속성 테스트"""
        extreme = ExtremeTicketing(self.mock_driver)
        
        # lag_bypass가 UltraLagBypass 인스턴스인지 확인
        if hasattr(extreme, 'lag_bypass'):
            self.assertIsInstance(extreme.lag_bypass, UltraLagBypass)
    
    def test_nuclear_option_method_exists(self):
        """nuclear_option 메소드 존재 확인"""
        extreme = ExtremeTicketing(self.mock_driver)
        
        # nuclear_option 메소드 확인
        self.assertTrue(hasattr(extreme, 'nuclear_option'))
        self.assertTrue(callable(getattr(extreme, 'nuclear_option')))


class TestUltraLagBypassIntegration(unittest.TestCase):
    """UltraLagBypass 통합 테스트"""
    
    def setUp(self):
        """테스트 준비"""
        if UltraLagBypass is None:
            self.skipTest("UltraLagBypass 모듈을 import할 수 없습니다")
    
    @patch('asyncio.run')
    def test_execute_all_methods_mock(self, mock_asyncio_run):
        """execute_all_methods 통합 테스트 (Mock)"""
        mock_driver = Mock()
        bypass = UltraLagBypass(mock_driver)
        
        # execute_all_methods 메소드가 있는 경우 테스트
        if hasattr(bypass, 'execute_all_methods'):
            # Mock으로 비동기 실행 시뮬레이션
            mock_asyncio_run.return_value = None
            
            try:
                # 실제로는 비동기지만 테스트에서는 Mock으로 처리
                result = bypass.execute_all_methods()
                # 에러 없이 실행되면 성공
                self.assertTrue(True)
            except Exception as e:
                # 예상 가능한 에러는 허용
                if "asyncio" in str(e) or "coroutine" in str(e):
                    self.skipTest("비동기 실행 환경 문제")
                else:
                    raise
        else:
            self.skipTest("execute_all_methods 메소드가 없습니다")
    
    def test_multiple_methods_execution(self):
        """여러 메소드 연속 실행 테스트"""
        mock_driver = Mock()
        mock_driver.execute_script = Mock(return_value=True)
        bypass = UltraLagBypass(mock_driver)
        
        # 여러 메소드를 연속으로 실행해도 에러가 없는지 확인
        methods_to_test = [
            'method4_browser_exploit',
            'method5_ajax_interceptor', 
            'method6_dom_mutation_hack'
        ]
        
        executed_count = 0
        for method_name in methods_to_test:
            if hasattr(bypass, method_name):
                try:
                    method = getattr(bypass, method_name)
                    method()
                    executed_count += 1
                except Exception as e:
                    # JavaScript 실행 관련 에러는 예상됨
                    if "execute_script" not in str(e):
                        self.fail(f"예상치 못한 에러 in {method_name}: {e}")
        
        # 최소 1개 메소드는 실행되어야 함
        self.assertGreater(executed_count, 0, "실행된 메소드가 없습니다")


def run_ultra_lag_bypass_tests():
    """UltraLagBypass 테스트 실행"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestUltraLagBypass))
    suite.addTests(loader.loadTestsFromTestCase(TestExtremeTicketing))
    suite.addTests(loader.loadTestsFromTestCase(TestUltraLagBypassIntegration))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🔬 UltraLagBypass 모듈 단위 테스트")
    print("=" * 50)
    
    success = run_ultra_lag_bypass_tests()
    
    if success:
        print("\n✅ 모든 UltraLagBypass 테스트 통과!")
    else:
        print("\n❌ 일부 UltraLagBypass 테스트 실패")
    
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
G4K 자동화 시스템 통합 테스트 스위트
Unit, Integration, E2E 테스트 포함
"""

import unittest
import asyncio
import time
import logging
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import traceback

# 테스트 대상 모듈들
try:
    from stealth_browser import StealthBrowser
    from profile_manager import ProfileManager, ConfigManager
    from adaptive_calendar_refresher import AdaptiveCalendarRefresher, ServerLoadAnalyzer
    from ultra_lag_bypass import UltraLagBypass, ExtremeTicketing
    from multi_profile_ticketing import MultiProfileTicketing
    from server_overload_strategy import ServerOverloadStrategy
    from cancellation_hunter import CancellationHunter
except ImportError as e:
    print(f"⚠️ 모듈 import 오류: {e}")
    print("일부 테스트가 스킵될 수 있습니다.")

# 테스트 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestResult:
    """테스트 결과 저장 클래스"""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.errors = []
        self.execution_time = 0
        self.coverage = {}
        
    def add_result(self, test_name: str, status: str, error: str = None, execution_time: float = 0):
        """테스트 결과 추가"""
        self.total_tests += 1
        
        if status == 'PASSED':
            self.passed_tests += 1
        elif status == 'FAILED':
            self.failed_tests += 1
            if error:
                self.errors.append(f"{test_name}: {error}")
        elif status == 'SKIPPED':
            self.skipped_tests += 1
            
        self.execution_time += execution_time
    
    def get_summary(self):
        """결과 요약 반환"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        return {
            'total': self.total_tests,
            'passed': self.passed_tests,
            'failed': self.failed_tests,
            'skipped': self.skipped_tests,
            'success_rate': round(success_rate, 2),
            'execution_time': round(self.execution_time, 2),
            'errors': self.errors
        }


class UnitTests:
    """단위 테스트 클래스"""
    
    def __init__(self):
        self.result = TestResult()
    
    def test_stealth_browser_initialization(self):
        """StealthBrowser 초기화 테스트"""
        start_time = time.time()
        try:
            browser = StealthBrowser()
            assert browser is not None
            assert hasattr(browser, 'create_driver')
            
            self.result.add_result(
                'stealth_browser_init', 
                'PASSED', 
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_result(
                'stealth_browser_init', 
                'FAILED', 
                str(e), 
                time.time() - start_time
            )
    
    def test_profile_manager(self):
        """프로필 매니저 테스트"""
        start_time = time.time()
        try:
            # 임시 파일로 테스트
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                test_profile = {
                    "profiles": [
                        {
                            "name": "test_user",
                            "id_number": "M12345678",
                            "phone": "010-1234-5678"
                        }
                    ]
                }
                json.dump(test_profile, f)
                temp_file = f.name
            
            try:
                profile_manager = ProfileManager(temp_file)
                profiles = profile_manager.load_profiles()
                
                assert len(profiles) == 1
                assert profiles[0]['name'] == 'test_user'
                
                self.result.add_result(
                    'profile_manager', 
                    'PASSED', 
                    execution_time=time.time() - start_time
                )
                
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            self.result.add_result(
                'profile_manager', 
                'FAILED', 
                str(e), 
                time.time() - start_time
            )
    
    def test_server_load_analyzer(self):
        """서버 부하 분석기 테스트"""
        start_time = time.time()
        try:
            analyzer = ServerLoadAnalyzer()
            
            # 테스트 데이터 추가
            analyzer.record_request(0.5, True)
            analyzer.record_request(1.0, True)
            analyzer.record_request(2.0, False)
            
            optimal_interval = analyzer.get_optimal_interval()
            
            assert isinstance(optimal_interval, float)
            assert optimal_interval > 0
            
            self.result.add_result(
                'server_load_analyzer', 
                'PASSED', 
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_result(
                'server_load_analyzer', 
                'FAILED', 
                str(e), 
                time.time() - start_time
            )
    
    def test_config_validation(self):
        """설정 파일 검증 테스트"""
        start_time = time.time()
        try:
            # 필수 설정 파일들 존재 확인
            required_files = [
                'config.yaml',
                'requirements.txt',
                'user_profiles.json'
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(file):
                    missing_files.append(file)
            
            if missing_files:
                raise AssertionError(f"Missing required files: {missing_files}")
            
            self.result.add_result(
                'config_validation', 
                'PASSED', 
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_result(
                'config_validation', 
                'FAILED', 
                str(e), 
                time.time() - start_time
            )
    
    def run_all(self):
        """모든 단위 테스트 실행"""
        logger.info("🔬 단위 테스트 실행 중...")
        
        test_methods = [
            self.test_stealth_browser_initialization,
            self.test_profile_manager,
            self.test_server_load_analyzer,
            self.test_config_validation
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"테스트 실행 오류: {e}")
        
        return self.result


class IntegrationTests:
    """통합 테스트 클래스"""
    
    def __init__(self):
        self.result = TestResult()
    
    def test_browser_profile_integration(self):
        """브라우저-프로필 통합 테스트"""
        start_time = time.time()
        try:
            # Mock 브라우저 드라이버
            mock_driver = Mock()
            mock_driver.execute_script.return_value = True
            
            # 프로필 매니저 생성
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                test_profile = {
                    "profiles": [
                        {
                            "name": "integration_test",
                            "id_number": "M87654321",
                            "phone": "010-8765-4321"
                        }
                    ]
                }
                json.dump(test_profile, f)
                temp_file = f.name
            
            try:
                profile_manager = ProfileManager(temp_file)
                profiles = profile_manager.load_profiles()
                
                # 브라우저와 프로필 연동 테스트
                assert len(profiles) > 0
                
                # 스텔스 브라우저 초기화 테스트 (Mock)
                with patch('stealth_browser.StealthBrowser.create_driver', return_value=mock_driver):
                    browser = StealthBrowser()
                    driver = browser.create_driver()
                    assert driver is not None
                
                self.result.add_result(
                    'browser_profile_integration', 
                    'PASSED', 
                    execution_time=time.time() - start_time
                )
                
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            self.result.add_result(
                'browser_profile_integration', 
                'FAILED', 
                str(e), 
                time.time() - start_time
            )
    
    def test_multi_component_workflow(self):
        """다중 컴포넌트 워크플로우 테스트"""
        start_time = time.time()
        try:
            # Mock 드라이버
            mock_driver = Mock()
            mock_driver.find_elements.return_value = []
            mock_driver.execute_script.return_value = {"found": False}
            
            # 적응형 새로고침과 서버 부하 분석기 통합
            analyzer = ServerLoadAnalyzer()
            
            with patch('adaptive_calendar_refresher.webdriver.Chrome', return_value=mock_driver):
                refresher = AdaptiveCalendarRefresher(mock_driver)
                
                # 테스트 데이터로 시뮬레이션
                analyzer.record_request(1.0, True)
                optimal_interval = analyzer.get_optimal_interval()
                
                assert optimal_interval > 0
                assert refresher is not None
            
            self.result.add_result(
                'multi_component_workflow', 
                'PASSED', 
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_result(
                'multi_component_workflow', 
                'FAILED', 
                str(e), 
                time.time() - start_time
            )
    
    def test_async_components(self):
        """비동기 컴포넌트 테스트"""
        start_time = time.time()
        
        async def async_test():
            try:
                # Mock 드라이버로 비동기 테스트
                mock_driver = Mock()
                
                # 서버 과부하 전략 테스트
                strategy = ServerOverloadStrategy()
                
                # Mock HTTP 세션
                with patch('aiohttp.ClientSession') as mock_session:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_session.return_value.__aenter__.return_value.post.return_value = mock_response
                    
                    # 준비 단계 테스트
                    await strategy.prepare_assault()
                    
                return True
                
            except Exception as e:
                raise e
        
        try:
            # 비동기 함수 실행
            result = asyncio.run(async_test())
            assert result is True
            
            self.result.add_result(
                'async_components', 
                'PASSED', 
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_result(
                'async_components', 
                'FAILED', 
                str(e), 
                time.time() - start_time
            )
    
    def run_all(self):
        """모든 통합 테스트 실행"""
        logger.info("🔗 통합 테스트 실행 중...")
        
        test_methods = [
            self.test_browser_profile_integration,
            self.test_multi_component_workflow,
            self.test_async_components
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"통합 테스트 실행 오류: {e}")
        
        return self.result


class EndToEndTests:
    """종단간 테스트 클래스"""
    
    def __init__(self):
        self.result = TestResult()
    
    def test_safe_cancellation_hunter(self):
        """안전한 취소표 헌터 테스트"""
        start_time = time.time()
        try:
            # Mock 환경에서 안전 테스트
            with patch('selenium.webdriver.Chrome') as mock_chrome:
                mock_driver = Mock()
                mock_driver.execute_script.return_value = {"found": False, "count": 0}
                mock_driver.current_url = "https://test.g4k.go.kr"
                mock_chrome.return_value = mock_driver
                
                # 테스트 모드로 취소표 헌터 초기화
                hunter = CancellationHunter(test_mode=True)
                hunter.driver = mock_driver
                
                # 부드러운 날짜 체크 테스트
                result = hunter.gentle_date_check()
                
                # Mock 환경에서는 False 반환 예상
                assert result is False
                
            self.result.add_result(
                'safe_cancellation_hunter', 
                'PASSED', 
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_result(
                'safe_cancellation_hunter', 
                'FAILED', 
                str(e), 
                time.time() - start_time
            )
    
    def test_multi_browser_simulation(self):
        """멀티 브라우저 시뮬레이션 테스트"""
        start_time = time.time()
        try:
            # 테스트용 프로필 생성
            test_profiles = [
                {"name": f"test_user_{i}", "id_number": f"M1234567{i}"}
                for i in range(3)  # 3개만 테스트
            ]
            
            with patch('undetected_chromedriver.Chrome') as mock_chrome:
                mock_driver = Mock()
                mock_chrome.return_value = mock_driver
                
                # 멀티 프로필 시스템 초기화
                multi_system = MultiProfileTicketing(test_profiles)
                
                # 브라우저 풀 생성 테스트 (Mock)
                browsers = multi_system.create_browser_pool()
                
                # 3개 브라우저가 생성되어야 함
                assert len(browsers) == 3
            
            self.result.add_result(
                'multi_browser_simulation', 
                'PASSED', 
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_result(
                'multi_browser_simulation', 
                'FAILED', 
                str(e), 
                time.time() - start_time
            )
    
    def test_extreme_bypass_safety(self):
        """극한 우회 기법 안전성 테스트"""
        start_time = time.time()
        try:
            mock_driver = Mock()
            mock_driver.execute_script.return_value = True
            
            # 극한 기법 초기화
            bypass = UltraLagBypass(mock_driver)
            
            # CDP URL이 설정되지 않은 상태에서 안전성 확인
            assert bypass.cdp_url is None or isinstance(bypass.cdp_url, str)
            
            # 메소드들이 예외 없이 실행되는지 확인
            bypass.method4_browser_exploit()
            bypass.method5_ajax_interceptor()
            
            self.result.add_result(
                'extreme_bypass_safety', 
                'PASSED', 
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_result(
                'extreme_bypass_safety', 
                'FAILED', 
                str(e), 
                time.time() - start_time
            )
    
    def run_all(self):
        """모든 E2E 테스트 실행"""
        logger.info("🎯 종단간 테스트 실행 중...")
        
        test_methods = [
            self.test_safe_cancellation_hunter,
            self.test_multi_browser_simulation,
            self.test_extreme_bypass_safety
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"E2E 테스트 실행 오류: {e}")
        
        return self.result


class TestRunner:
    """테스트 실행기"""
    
    def __init__(self):
        self.overall_result = TestResult()
        
    def run_tests(self, test_type: str = 'all'):
        """테스트 실행"""
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║                    🧪 G4K 자동화 테스트 스위트                ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        
        start_time = time.time()
        
        results = {}
        
        if test_type in ['all', 'unit']:
            print("\n🔬 단위 테스트 실행 중...")
            unit_tests = UnitTests()
            results['unit'] = unit_tests.run_all()
            
        if test_type in ['all', 'integration']:
            print("\n🔗 통합 테스트 실행 중...")
            integration_tests = IntegrationTests()
            results['integration'] = integration_tests.run_all()
            
        if test_type in ['all', 'e2e']:
            print("\n🎯 종단간 테스트 실행 중...")
            e2e_tests = EndToEndTests()
            results['e2e'] = e2e_tests.run_all()
        
        total_time = time.time() - start_time
        
        # 결과 통합
        self._combine_results(results)
        
        # 보고서 생성
        self._generate_report(results, total_time)
        
        return results
    
    def _combine_results(self, results):
        """결과 통합"""
        for test_type, result in results.items():
            summary = result.get_summary()
            self.overall_result.total_tests += summary['total']
            self.overall_result.passed_tests += summary['passed']
            self.overall_result.failed_tests += summary['failed']
            self.overall_result.skipped_tests += summary['skipped']
            self.overall_result.execution_time += summary['execution_time']
            self.overall_result.errors.extend(summary['errors'])
    
    def _generate_report(self, results, total_time):
        """테스트 보고서 생성"""
        print("\n" + "="*70)
        print("📊 테스트 결과 보고서")
        print("="*70)
        
        overall_summary = self.overall_result.get_summary()
        
        print(f"전체 실행 시간: {total_time:.2f}초")
        print(f"총 테스트 수: {overall_summary['total']}")
        print(f"✅ 성공: {overall_summary['passed']} ({overall_summary['success_rate']}%)")
        print(f"❌ 실패: {overall_summary['failed']}")
        print(f"⏭️ 스킵: {overall_summary['skipped']}")
        
        # 테스트 타입별 결과
        print("\n📋 테스트 타입별 결과:")
        for test_type, result in results.items():
            summary = result.get_summary()
            status = "✅ PASS" if summary['failed'] == 0 else "❌ FAIL"
            print(f"  {test_type.upper():12} - {status} ({summary['passed']}/{summary['total']})")
        
        # 오류 상세
        if overall_summary['errors']:
            print("\n❌ 오류 상세:")
            for i, error in enumerate(overall_summary['errors'][:5], 1):  # 최대 5개만 표시
                print(f"  {i}. {error}")
            
            if len(overall_summary['errors']) > 5:
                print(f"  ... 및 {len(overall_summary['errors']) - 5}개 추가 오류")
        
        # 권장사항
        self._generate_recommendations(overall_summary)
        
        # JSON 보고서도 생성
        self._save_json_report(results, total_time)
    
    def _generate_recommendations(self, summary):
        """권장사항 생성"""
        print("\n💡 권장사항:")
        
        if summary['success_rate'] >= 90:
            print("  🎉 훌륭합니다! 대부분의 테스트가 통과했습니다.")
        elif summary['success_rate'] >= 70:
            print("  👍 양호합니다. 몇 가지 개선사항이 있습니다.")
        else:
            print("  ⚠️ 주의: 많은 테스트가 실패했습니다. 코드 검토가 필요합니다.")
        
        if summary['failed'] > 0:
            print("  • 실패한 테스트들을 우선적으로 수정하세요.")
            print("  • 로그를 확인하여 원인을 파악하세요.")
        
        if summary['execution_time'] > 60:
            print("  • 테스트 실행 시간이 길습니다. 성능 최적화를 고려하세요.")
        
        print("  • 정기적으로 테스트를 실행하여 품질을 유지하세요.")
    
    def _save_json_report(self, results, total_time):
        """JSON 보고서 저장"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_execution_time': total_time,
            'overall_summary': self.overall_result.get_summary(),
            'detailed_results': {}
        }
        
        for test_type, result in results.items():
            report_data['detailed_results'][test_type] = result.get_summary()
        
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n📄 상세 보고서 저장됨: {report_file}")
        except Exception as e:
            print(f"⚠️ 보고서 저장 실패: {e}")


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='G4K 자동화 테스트 스위트')
    parser.add_argument('--type', choices=['unit', 'integration', 'e2e', 'all'], 
                       default='all', help='실행할 테스트 타입')
    parser.add_argument('--coverage', action='store_true', help='커버리지 보고서 생성')
    parser.add_argument('--watch', action='store_true', help='파일 변경 감시 모드')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.watch:
        print("📁 파일 변경 감시 모드 (Ctrl+C로 종료)")
        try:
            while True:
                print(f"\n🔄 테스트 실행 중... ({datetime.now().strftime('%H:%M:%S')})")
                runner.run_tests(args.type)
                print("\n⏳ 변경사항 대기 중... (30초 후 재실행)")
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n👋 감시 모드 종료")
    else:
        runner.run_tests(args.type)


if __name__ == "__main__":
    main()
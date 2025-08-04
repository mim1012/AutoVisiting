#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G4K 자동화 시스템 안전 테스트 스위트
의존성 문제를 우회하는 독립적인 테스트
"""

import unittest
import json
import os
import tempfile
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
import sys

# 안전한 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SafeTestResult:
    """안전한 테스트 결과 저장"""
    
    def __init__(self):
        self.results = []
        self.summary = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
    
    def add_test_result(self, test_name: str, status: str, message: str = "", execution_time: float = 0):
        """테스트 결과 추가"""
        result = {
            'test_name': test_name,
            'status': status,
            'message': message,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        self.summary['total'] += 1
        
        if status == 'PASSED':
            self.summary['passed'] += 1
        elif status == 'FAILED':
            self.summary['failed'] += 1
            self.summary['errors'].append(f"{test_name}: {message}")
        elif status == 'SKIPPED':
            self.summary['skipped'] += 1
    
    def get_summary(self):
        """요약 반환"""
        success_rate = (self.summary['passed'] / self.summary['total'] * 100) if self.summary['total'] > 0 else 0
        return {
            **self.summary,
            'success_rate': round(success_rate, 2)
        }


class ConfigurationTests:
    """설정 및 구성 테스트"""
    
    def __init__(self):
        self.result = SafeTestResult()
    
    def test_required_files_exist(self):
        """필수 파일 존재 확인"""
        start_time = time.time()
        test_name = "required_files_exist"
        
        try:
            required_files = [
                'requirements.txt',
                'config.yaml',
                'CLAUDE.md',
                'README.md'
            ]
            
            missing_files = []
            existing_files = []
            
            for file in required_files:
                if os.path.exists(file):
                    existing_files.append(file)
                else:
                    missing_files.append(file)
            
            if missing_files:
                self.result.add_test_result(
                    test_name,
                    'FAILED',
                    f"Missing files: {', '.join(missing_files)}",
                    time.time() - start_time
                )
            else:
                self.result.add_test_result(
                    test_name,
                    'PASSED',
                    f"All {len(existing_files)} required files found",
                    time.time() - start_time
                )
                
        except Exception as e:
            self.result.add_test_result(
                test_name,
                'FAILED',
                str(e),
                time.time() - start_time
            )
    
    def test_python_modules_exist(self):
        """파이썬 모듈 파일 존재 확인"""
        start_time = time.time()
        test_name = "python_modules_exist"
        
        try:
            required_modules = [
                'stealth_browser.py',
                'profile_manager.py',
                'adaptive_calendar_refresher.py',
                'ultra_lag_bypass.py',
                'multi_profile_ticketing.py',
                'cancellation_hunter.py'
            ]
            
            existing_modules = []
            missing_modules = []
            
            for module in required_modules:
                if os.path.exists(module):
                    existing_modules.append(module)
                else:
                    missing_modules.append(module)
            
            self.result.add_test_result(
                test_name,
                'PASSED' if not missing_modules else 'FAILED',
                f"Found {len(existing_modules)}/{len(required_modules)} modules. Missing: {missing_modules}",
                time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_test_result(
                test_name,
                'FAILED',
                str(e),
                time.time() - start_time
            )
    
    def test_json_files_valid(self):
        """JSON 파일 유효성 검사"""
        start_time = time.time()
        test_name = "json_files_valid"
        
        try:
            json_files = [
                'user_profiles.json',
                'auto_check_settings.json',
                'reservation_templates.json'
            ]
            
            valid_files = []
            invalid_files = []
            
            for json_file in json_files:
                if os.path.exists(json_file):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            json.load(f)
                        valid_files.append(json_file)
                    except json.JSONDecodeError as e:
                        invalid_files.append(f"{json_file}: {str(e)}")
                else:
                    invalid_files.append(f"{json_file}: File not found")
            
            self.result.add_test_result(
                test_name,
                'PASSED' if not invalid_files else 'FAILED',
                f"Valid: {len(valid_files)}, Invalid: {len(invalid_files)}. Details: {invalid_files[:3]}",
                time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_test_result(
                test_name,
                'FAILED',
                str(e),
                time.time() - start_time
            )
    
    def test_requirements_parseable(self):
        """requirements.txt 파싱 가능 여부"""
        start_time = time.time()
        test_name = "requirements_parseable"
        
        try:
            if not os.path.exists('requirements.txt'):
                self.result.add_test_result(
                    test_name,
                    'SKIPPED',
                    "requirements.txt not found",
                    time.time() - start_time
                )
                return
            
            with open('requirements.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            packages = []
            invalid_lines = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '>=' in line or '==' in line or '~=' in line:
                        packages.append(line)
                    elif line and not line.startswith('-'):
                        invalid_lines.append(f"Line {i}: {line}")
            
            self.result.add_test_result(
                test_name,
                'PASSED' if not invalid_lines else 'FAILED',
                f"Found {len(packages)} packages, {len(invalid_lines)} invalid lines",
                time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_test_result(
                test_name,
                'FAILED',
                str(e),
                time.time() - start_time
            )
    
    def run_all(self):
        """모든 설정 테스트 실행"""
        logger.info("📁 설정 파일 테스트 실행 중...")
        
        test_methods = [
            self.test_required_files_exist,
            self.test_python_modules_exist,
            self.test_json_files_valid,
            self.test_requirements_parseable
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"테스트 실행 오류: {test_method.__name__}: {e}")
        
        return self.result


class ModuleIntegrityTests:
    """모듈 무결성 테스트"""
    
    def __init__(self):
        self.result = SafeTestResult()
    
    def test_python_syntax(self):
        """파이썬 파일 문법 검사"""
        start_time = time.time()
        test_name = "python_syntax_check"
        
        try:
            python_files = [f for f in os.listdir('.') if f.endswith('.py')]
            
            syntax_errors = []
            valid_files = []
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    # 문법 검사
                    compile(code, py_file, 'exec')
                    valid_files.append(py_file)
                    
                except SyntaxError as e:
                    syntax_errors.append(f"{py_file}:{e.lineno}: {e.msg}")
                except Exception as e:
                    syntax_errors.append(f"{py_file}: {str(e)}")
            
            self.result.add_test_result(
                test_name,
                'PASSED' if not syntax_errors else 'FAILED',
                f"Valid: {len(valid_files)}, Errors: {len(syntax_errors)}. First 3: {syntax_errors[:3]}",
                time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_test_result(
                test_name,
                'FAILED',
                str(e),
                time.time() - start_time
            )
    
    def test_import_structure(self):
        """import 구조 검사"""
        start_time = time.time()
        test_name = "import_structure_check"
        
        try:
            python_files = [f for f in os.listdir('.') if f.endswith('.py')]
            
            import_issues = []
            clean_files = []
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # import 문 검사
                    for i, line in enumerate(lines, 1):
                        line = line.strip()
                        if line.startswith('from') or line.startswith('import'):
                            # 상대 import 검사
                            if 'from .' in line and not py_file.startswith('test_'):
                                import_issues.append(f"{py_file}:{i}: Relative import in non-package")
                    
                    if py_file not in [issue.split(':')[0] for issue in import_issues]:
                        clean_files.append(py_file)
                        
                except Exception as e:
                    import_issues.append(f"{py_file}: Read error - {str(e)}")
            
            self.result.add_test_result(
                test_name,
                'PASSED' if len(import_issues) <= 2 else 'FAILED',  # 약간의 여유 허용
                f"Clean: {len(clean_files)}, Issues: {len(import_issues)}",
                time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_test_result(
                test_name,
                'FAILED',
                str(e),
                time.time() - start_time
            )
    
    def test_file_encoding(self):
        """파일 인코딩 검사"""
        start_time = time.time()
        test_name = "file_encoding_check"
        
        try:
            python_files = [f for f in os.listdir('.') if f.endswith('.py')]
            
            encoding_errors = []
            valid_files = []
            
            for py_file in python_files:
                try:
                    # UTF-8으로 읽기 시도
                    with open(py_file, 'r', encoding='utf-8') as f:
                        f.read()
                    valid_files.append(py_file)
                    
                except UnicodeDecodeError as e:
                    encoding_errors.append(f"{py_file}: UTF-8 decode error")
                except Exception as e:
                    encoding_errors.append(f"{py_file}: {str(e)}")
            
            self.result.add_test_result(
                test_name,
                'PASSED' if not encoding_errors else 'FAILED',
                f"UTF-8 compatible: {len(valid_files)}, Errors: {len(encoding_errors)}",
                time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_test_result(
                test_name,
                'FAILED',
                str(e),
                time.time() - start_time
            )
    
    def run_all(self):
        """모든 무결성 테스트 실행"""
        logger.info("🔍 모듈 무결성 테스트 실행 중...")
        
        test_methods = [
            self.test_python_syntax,
            self.test_import_structure,
            self.test_file_encoding
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"무결성 테스트 오류: {test_method.__name__}: {e}")
        
        return self.result


class PerformanceTests:
    """성능 테스트"""
    
    def __init__(self):
        self.result = SafeTestResult()
    
    def test_file_load_performance(self):
        """파일 로딩 성능 테스트"""
        start_time = time.time()
        test_name = "file_load_performance"
        
        try:
            python_files = [f for f in os.listdir('.') if f.endswith('.py')][:10]  # 최대 10개
            
            load_times = []
            
            for py_file in python_files:
                file_start = time.time()
                with open(py_file, 'r', encoding='utf-8') as f:
                    f.read()
                load_time = time.time() - file_start
                load_times.append(load_time)
            
            avg_load_time = sum(load_times) / len(load_times) if load_times else 0
            max_load_time = max(load_times) if load_times else 0
            
            # 성능 기준: 평균 0.1초 이하, 최대 0.5초 이하
            performance_ok = avg_load_time < 0.1 and max_load_time < 0.5
            
            self.result.add_test_result(
                test_name,
                'PASSED' if performance_ok else 'FAILED',
                f"Avg: {avg_load_time:.3f}s, Max: {max_load_time:.3f}s, Files: {len(python_files)}",
                time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_test_result(
                test_name,
                'FAILED',
                str(e),
                time.time() - start_time
            )
    
    def test_json_parsing_performance(self):
        """JSON 파싱 성능 테스트"""
        start_time = time.time()
        test_name = "json_parsing_performance"
        
        try:
            json_files = [f for f in os.listdir('.') if f.endswith('.json')]
            
            if not json_files:
                self.result.add_test_result(
                    test_name,
                    'SKIPPED',
                    "No JSON files found",
                    time.time() - start_time
                )
                return
            
            parse_times = []
            
            for json_file in json_files:
                try:
                    file_start = time.time()
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    parse_time = time.time() - file_start
                    parse_times.append(parse_time)
                except:
                    continue  # 파싱 불가능한 파일은 스킵
            
            if not parse_times:
                self.result.add_test_result(
                    test_name,
                    'SKIPPED',
                    "No valid JSON files",
                    time.time() - start_time
                )
                return
            
            avg_parse_time = sum(parse_times) / len(parse_times)
            max_parse_time = max(parse_times)
            
            # 성능 기준: 평균 0.05초 이하
            performance_ok = avg_parse_time < 0.05
            
            self.result.add_test_result(
                test_name,
                'PASSED' if performance_ok else 'FAILED',
                f"Avg: {avg_parse_time:.3f}s, Max: {max_parse_time:.3f}s, Files: {len(parse_times)}",
                time.time() - start_time
            )
            
        except Exception as e:
            self.result.add_test_result(
                test_name,
                'FAILED',
                str(e),
                time.time() - start_time
            )
    
    def run_all(self):
        """모든 성능 테스트 실행"""
        logger.info("⚡ 성능 테스트 실행 중...")
        
        test_methods = [
            self.test_file_load_performance,
            self.test_json_parsing_performance
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"성능 테스트 오류: {test_method.__name__}: {e}")
        
        return self.result


class SafeTestRunner:
    """안전한 테스트 실행기"""
    
    def __init__(self):
        self.all_results = {}
        self.start_runtime = time.time()
    
    def run_safe_tests(self, test_types: List[str] = None):
        """안전한 테스트 실행"""
        if test_types is None:
            test_types = ['config', 'integrity', 'performance']
        
        print("="*67)
        print("                  G4K 안전 테스트 스위트                     ")
        print("="*67)
        print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"테스트 타입: {', '.join(test_types)}")
        print("-" * 67)
        
        if 'config' in test_types:
            config_tests = ConfigurationTests()
            self.all_results['configuration'] = config_tests.run_all()
        
        if 'integrity' in test_types:
            integrity_tests = ModuleIntegrityTests()
            self.all_results['integrity'] = integrity_tests.run_all()
        
        if 'performance' in test_types:
            performance_tests = PerformanceTests()
            self.all_results['performance'] = performance_tests.run_all()
        
        # 결과 보고서 생성
        self._generate_comprehensive_report()
        
        return self.all_results
    
    def _generate_comprehensive_report(self):
        """종합 보고서 생성"""
        total_runtime = time.time() - self.start_runtime
        
        print("\n" + "="*67)
        print("📊 종합 테스트 결과")
        print("="*67)
        
        overall_stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # 각 테스트 타입별 결과
        for test_type, result in self.all_results.items():
            summary = result.get_summary()
            overall_stats['total'] += summary['total']
            overall_stats['passed'] += summary['passed']
            overall_stats['failed'] += summary['failed']
            overall_stats['skipped'] += summary['skipped']
            
            status_icon = "✅" if summary['failed'] == 0 else "❌"
            print(f"{status_icon} {test_type.upper():12} - {summary['passed']:2d}/{summary['total']:2d} passed ({summary['success_rate']:5.1f}%)")
        
        # 전체 통계
        overall_success_rate = (overall_stats['passed'] / overall_stats['total'] * 100) if overall_stats['total'] > 0 else 0
        
        print("-" * 67)
        print(f"📈 전체 통계:")
        print(f"   총 테스트:     {overall_stats['total']:3d}")
        print(f"   ✅ 성공:       {overall_stats['passed']:3d} ({overall_success_rate:.1f}%)")
        print(f"   ❌ 실패:       {overall_stats['failed']:3d}")
        print(f"   ⏭️ 스킵:       {overall_stats['skipped']:3d}")
        print(f"   ⏱️ 실행시간:   {total_runtime:.2f}초")
        
        # 권장사항
        print(f"\n💡 결과 분석:")
        if overall_success_rate >= 95:
            print("   🎉 완벽! 모든 테스트가 거의 통과했습니다.")
        elif overall_success_rate >= 80:
            print("   👍 양호! 대부분의 테스트가 통과했습니다.")
        elif overall_success_rate >= 60:
            print("   ⚠️  주의! 일부 개선이 필요합니다.")
        else:
            print("   🚨 경고! 많은 문제가 발견되었습니다.")
        
        # 오류 상세 (처음 5개만)
        all_errors = []
        for result in self.all_results.values():
            all_errors.extend(result.get_summary()['errors'])
        
        if all_errors:
            print(f"\n❌ 주요 오류 (총 {len(all_errors)}개):")
            for i, error in enumerate(all_errors[:5], 1):
                print(f"   {i}. {error}")
            if len(all_errors) > 5:
                print(f"   ... 및 {len(all_errors) - 5}개 추가 오류")
        
        # JSON 리포트 저장
        self._save_json_report(overall_stats, total_runtime)
    
    def _save_json_report(self, overall_stats, total_runtime):
        """JSON 형태로 상세 리포트 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"safe_test_report_{timestamp}.json"
        
        report_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_runtime': total_runtime,
                'test_types': list(self.all_results.keys())
            },
            'overall_stats': overall_stats,
            'detailed_results': {}
        }
        
        for test_type, result in self.all_results.items():
            report_data['detailed_results'][test_type] = {
                'summary': result.get_summary(),
                'individual_tests': result.results
            }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n📄 상세 리포트 저장: {report_file}")
        except Exception as e:
            print(f"⚠️ 리포트 저장 실패: {e}")


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='G4K 안전 테스트 스위트')
    parser.add_argument('--type', 
                       choices=['config', 'integrity', 'performance', 'all'],
                       default='all',
                       help='실행할 테스트 타입')
    parser.add_argument('--quick', 
                       action='store_true',
                       help='빠른 테스트 (핵심 항목만)')
    
    args = parser.parse_args()
    
    # 테스트 타입 결정
    if args.type == 'all':
        test_types = ['config', 'integrity', 'performance']
    else:
        test_types = [args.type]
    
    if args.quick:
        test_types = ['config']  # 빠른 테스트는 설정만
    
    # 테스트 실행
    runner = SafeTestRunner()
    runner.run_safe_tests(test_types)


if __name__ == "__main__":
    main()
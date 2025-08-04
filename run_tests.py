#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 테스트 실행기
모든 테스트를 한 번에 실행하고 결과 정리
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime


class TestRunner:
    """통합 테스트 실행기"""
    
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 60)
        print("🧪 G4K 자동화 시스템 통합 테스트 실행")
        print("=" * 60)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. 기본 구조 테스트
        print("1️⃣ 기본 구조 테스트...")
        basic_result = self._run_basic_tests()
        self.results['basic'] = basic_result
        
        # 2. 단위 테스트들
        print("\n2️⃣ 단위 테스트...")
        unit_result = self._run_unit_tests()
        self.results['unit'] = unit_result
        
        # 3. 커버리지 분석
        print("\n3️⃣ 커버리지 분석...")
        coverage_result = self._run_coverage_analysis()
        self.results['coverage'] = coverage_result
        
        # 4. 성능 테스트
        print("\n4️⃣ 성능 검증...")
        performance_result = self._run_performance_tests()
        self.results['performance'] = performance_result
        
        # 5. 통합 결과
        self._generate_summary_report()
    
    def _run_basic_tests(self):
        """기본 테스트 실행"""
        try:
            result = subprocess.run([
                sys.executable, 'simple_test_runner.py'
            ], capture_output=True, text=True, timeout=30)
            
            success = result.returncode == 0
            
            if success:
                print("   ✅ 기본 테스트 통과")
            else:
                print("   ❌ 기본 테스트 실패")
                print(f"   오류: {result.stderr[:100]}...")
            
            return {
                'status': 'PASS' if success else 'FAIL',
                'output': result.stdout,
                'error': result.stderr,
                'execution_time': time.time() - self.start_time
            }
            
        except subprocess.TimeoutExpired:
            print("   ⏰ 기본 테스트 타임아웃")
            return {'status': 'TIMEOUT', 'output': '', 'error': 'Timeout after 30s'}
        except Exception as e:
            print(f"   💥 기본 테스트 실행 오류: {e}")
            return {'status': 'ERROR', 'output': '', 'error': str(e)}
    
    def _run_unit_tests(self):
        """단위 테스트 실행"""
        unit_tests = [
            ('stealth_browser', 'tests/test_stealth_browser.py'),
            ('profile_manager', 'tests/test_profile_manager.py'),
            ('ultra_lag_bypass', 'tests/test_ultra_lag_bypass.py')
        ]
        
        unit_results = {}
        
        for test_name, test_file in unit_tests:
            if os.path.exists(test_file):
                try:
                    print(f"   🔬 {test_name} 테스트 실행...")
                    result = subprocess.run([
                        sys.executable, test_file
                    ], capture_output=True, text=True, timeout=60)
                    
                    success = result.returncode == 0
                    status_icon = "✅" if success else "❌"
                    print(f"      {status_icon} {test_name}: {'PASS' if success else 'FAIL'}")
                    
                    unit_results[test_name] = {
                        'status': 'PASS' if success else 'FAIL',
                        'output': result.stdout[-500:],  # 마지막 500자만
                        'error': result.stderr[-200:] if result.stderr else ''
                    }
                    
                except subprocess.TimeoutExpired:
                    print(f"      ⏰ {test_name}: TIMEOUT")
                    unit_results[test_name] = {'status': 'TIMEOUT'}
                except Exception as e:
                    print(f"      💥 {test_name}: ERROR - {e}")
                    unit_results[test_name] = {'status': 'ERROR', 'error': str(e)}
            else:
                print(f"      ⏭️ {test_name}: SKIP (파일 없음)")
                unit_results[test_name] = {'status': 'SKIP'}
        
        return unit_results
    
    def _run_coverage_analysis(self):
        """커버리지 분석 실행"""
        try:
            result = subprocess.run([
                sys.executable, 'test_coverage_analyzer.py'
            ], capture_output=True, text=True, timeout=45)
            
            success = result.returncode == 0
            
            if success:
                print("   📊 커버리지 분석 완료")
                # 출력에서 커버리지 퍼센트 추출 시도
                coverage_percent = self._extract_coverage_from_output(result.stdout)
            else:
                print("   ❌ 커버리지 분석 실패")
                coverage_percent = 0
            
            return {
                'status': 'PASS' if success else 'FAIL',
                'coverage_percent': coverage_percent,
                'output': result.stdout[-300:],
                'error': result.stderr[-200:] if result.stderr else ''
            }
            
        except subprocess.TimeoutExpired:
            print("   ⏰ 커버리지 분석 타임아웃")
            return {'status': 'TIMEOUT', 'coverage_percent': 0}
        except Exception as e:
            print(f"   💥 커버리지 분석 오류: {e}")
            return {'status': 'ERROR', 'coverage_percent': 0, 'error': str(e)}
    
    def _extract_coverage_from_output(self, output):
        """출력에서 커버리지 퍼센트 추출"""
        import re
        
        # "커버리지 추정: XX.X%" 패턴 찾기
        match = re.search(r'커버리지 압정:\s*(\d+\.?\d*)%', output)
        if match:
            return float(match.group(1))
        
        # "XX.X%" 패턴 찾기
        match = re.search(r'(\d+\.?\d*)%', output)
        if match:
            return float(match.group(1))
        
        return 0
    
    def _run_performance_tests(self):
        """성능 테스트 실행"""
        try:
            # 간단한 성능 측정
            import glob
            
            start = time.time()
            
            # Python 파일 개수 세기
            py_files = glob.glob('*.py')
            file_count = len(py_files)
            
            # 간단한 파일 읽기 성능 테스트
            total_size = 0
            read_time = 0
            
            for py_file in py_files[:10]:  # 처음 10개만
                file_start = time.time()
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        total_size += len(content)
                    read_time += time.time() - file_start
                except:
                    pass
            
            total_time = time.time() - start
            avg_read_time = read_time / min(len(py_files), 10) if py_files else 0
            
            performance_ok = avg_read_time < 0.1 and total_time < 5.0
            
            print(f"   ⚡ 성능 테스트: {'PASS' if performance_ok else 'FAIL'}")
            print(f"      파일 {file_count}개, 평균 읽기: {avg_read_time:.3f}초")
            
            return {
                'status': 'PASS' if performance_ok else 'FAIL',
                'file_count': file_count,
                'avg_read_time': avg_read_time,
                'total_time': total_time
            }
            
        except Exception as e:
            print(f"   💥 성능 테스트 오류: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    def _generate_summary_report(self):
        """요약 보고서 생성"""
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        
        # 각 테스트 결과
        basic_status = self.results.get('basic', {}).get('status', 'ERROR')
        unit_results = self.results.get('unit', {})
        coverage_result = self.results.get('coverage', {})
        performance_result = self.results.get('performance', {})
        
        print(f"🔍 기본 테스트:     {self._status_icon(basic_status)} {basic_status}")
        
        # 단위 테스트 요약
        if unit_results:
            unit_pass = sum(1 for result in unit_results.values() if result.get('status') == 'PASS')
            unit_total = len(unit_results)
            print(f"🔬 단위 테스트:     {'✅' if unit_pass == unit_total else '❌'} {unit_pass}/{unit_total}")
        
        # 커버리지
        coverage_percent = coverage_result.get('coverage_percent', 0)
        coverage_status = coverage_result.get('status', 'ERROR')
        print(f"📊 커버리지:       {self._status_icon(coverage_status)} {coverage_percent:.1f}%")
        
        # 성능
        perf_status = performance_result.get('status', 'ERROR')
        print(f"⚡ 성능:           {self._status_icon(perf_status)} {perf_status}")
        
        print(f"⏱️ 총 실행 시간:   {total_time:.2f}초")
        
        # 전체 평가
        print(f"\n🎯 전체 평가:")
        overall_score = self._calculate_overall_score()
        print(f"   점수: {overall_score['score']}/100")
        print(f"   등급: {overall_score['grade']}")
        
        # 개선사항
        recommendations = self._generate_recommendations()
        if recommendations:
            print(f"\n💡 개선 권장사항:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        # JSON 보고서 저장
        self._save_json_report(total_time)
    
    def _status_icon(self, status):
        """상태 아이콘 반환"""
        icons = {
            'PASS': '✅',
            'FAIL': '❌', 
            'ERROR': '💥',
            'TIMEOUT': '⏰',
            'SKIP': '⏭️'
        }
        return icons.get(status, '❓')
    
    def _calculate_overall_score(self):
        """전체 점수 계산"""
        score = 0
        
        # 기본 테스트 (30점)
        if self.results.get('basic', {}).get('status') == 'PASS':
            score += 30
        
        # 단위 테스트 (30점)
        unit_results = self.results.get('unit', {})
        if unit_results:
            unit_pass = sum(1 for result in unit_results.values() if result.get('status') == 'PASS')
            unit_total = len(unit_results)
            score += int(30 * unit_pass / unit_total) if unit_total > 0 else 0
        
        # 커버리지 (25점)
        coverage_percent = self.results.get('coverage', {}).get('coverage_percent', 0)
        score += int(25 * coverage_percent / 100)
        
        # 성능 (15점)
        if self.results.get('performance', {}).get('status') == 'PASS':
            score += 15
        
        # 등급 계산
        if score >= 90:
            grade = 'A+'
        elif score >= 85:
            grade = 'A'
        elif score >= 80:
            grade = 'B+'
        elif score >= 75:
            grade = 'B'
        elif score >= 70:
            grade = 'C+'
        elif score >= 65:
            grade = 'C'
        else:
            grade = 'D'
        
        return {'score': score, 'grade': grade}
    
    def _generate_recommendations(self):
        """개선 권장사항 생성"""
        recommendations = []
        
        # 기본 테스트 실패
        if self.results.get('basic', {}).get('status') != 'PASS':
            recommendations.append("기본 구조 문제를 해결하세요")
        
        # 단위 테스트 부족
        unit_results = self.results.get('unit', {})
        if unit_results:
            failed_tests = [name for name, result in unit_results.items() 
                          if result.get('status') not in ['PASS', 'SKIP']]
            if failed_tests:
                recommendations.append(f"실패한 단위 테스트를 수정하세요: {', '.join(failed_tests)}")
        
        # 커버리지 부족
        coverage_percent = self.results.get('coverage', {}).get('coverage_percent', 0)
        if coverage_percent < 60:
            recommendations.append("테스트 커버리지를 60% 이상으로 높이세요")
        
        # 성능 문제
        if self.results.get('performance', {}).get('status') != 'PASS':
            recommendations.append("성능 문제를 확인하고 최적화하세요")
        
        return recommendations[:5]  # 최대 5개
    
    def _save_json_report(self, total_time):
        """JSON 보고서 저장"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_execution_time': total_time,
            'results': self.results,
            'overall_score': self._calculate_overall_score(),
            'recommendations': self._generate_recommendations()
        }
        
        report_file = f"integrated_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 상세 보고서: {report_file}")
        except Exception as e:
            print(f"⚠️ 보고서 저장 실패: {e}")


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='G4K 통합 테스트 실행기')
    parser.add_argument('--quick', action='store_true', help='빠른 테스트만 실행')
    parser.add_argument('--verbose', action='store_true', help='상세 출력')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.quick:
        print("🚀 빠른 테스트 모드")
        # 빠른 테스트만 실행
        runner._run_basic_tests()
    else:
        # 전체 테스트 실행
        runner.run_all_tests()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G4K 자동화 시스템 간단 테스트 실행기
Windows 인코딩 문제 해결 버전
"""

import os
import json
import time
import sys
from datetime import datetime


def test_file_structure():
    """파일 구조 테스트"""
    print("=== 파일 구조 테스트 ===")
    
    required_files = [
        'requirements.txt',
        'config.yaml', 
        'CLAUDE.md',
        'README.md',
        'stealth_browser.py',
        'profile_manager.py',
        'adaptive_calendar_refresher.py',
        'ultra_lag_bypass.py',
        'multi_profile_ticketing.py',
        'cancellation_hunter.py'
    ]
    
    results = {'total': len(required_files), 'passed': 0, 'failed': 0}
    
    for file in required_files:
        if os.path.exists(file):
            print(f"[PASS] {file}")
            results['passed'] += 1
        else:
            print(f"[FAIL] {file} - Not found")
            results['failed'] += 1
    
    print(f"파일 구조 테스트: {results['passed']}/{results['total']} 통과")
    return results


def test_json_files():
    """JSON 파일 테스트"""
    print("\n=== JSON 파일 테스트 ===")
    
    json_files = [
        'user_profiles.json',
        'auto_check_settings.json', 
        'reservation_templates.json'
    ]
    
    results = {'total': 0, 'passed': 0, 'failed': 0}
    
    for json_file in json_files:
        if os.path.exists(json_file):
            results['total'] += 1
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"[PASS] {json_file} - Valid JSON")
                results['passed'] += 1
            except json.JSONDecodeError as e:
                print(f"[FAIL] {json_file} - Invalid JSON: {str(e)}")
                results['failed'] += 1
            except Exception as e:
                print(f"[FAIL] {json_file} - Error: {str(e)}")
                results['failed'] += 1
        else:
            print(f"[SKIP] {json_file} - Not found")
    
    if results['total'] == 0:
        print("JSON 파일이 없습니다.")
    else:
        print(f"JSON 파일 테스트: {results['passed']}/{results['total']} 통과")
    
    return results


def test_python_syntax():
    """Python 파일 문법 테스트"""
    print("\n=== Python 문법 테스트 ===")
    
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    results = {'total': len(python_files), 'passed': 0, 'failed': 0}
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 문법 검사
            compile(code, py_file, 'exec')
            print(f"[PASS] {py_file}")
            results['passed'] += 1
            
        except SyntaxError as e:
            print(f"[FAIL] {py_file} - Syntax Error: Line {e.lineno}: {e.msg}")
            results['failed'] += 1
        except Exception as e:
            print(f"[FAIL] {py_file} - Error: {str(e)}")
            results['failed'] += 1
    
    print(f"Python 문법 테스트: {results['passed']}/{results['total']} 통과")
    return results


def test_requirements():
    """requirements.txt 테스트"""
    print("\n=== Requirements 테스트 ===")
    
    if not os.path.exists('requirements.txt'):
        print("[FAIL] requirements.txt not found")
        return {'total': 1, 'passed': 0, 'failed': 1}
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        packages = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                packages.append(line)
        
        print(f"[PASS] requirements.txt - {len(packages)} packages found")
        
        # 핵심 패키지 확인
        required_packages = ['selenium', 'requests', 'beautifulsoup4']
        found_packages = []
        
        for req_pkg in required_packages:
            for pkg in packages:
                if req_pkg in pkg.lower():
                    found_packages.append(req_pkg)
                    break
        
        print(f"[INFO] 핵심 패키지: {len(found_packages)}/{len(required_packages)} 발견")
        
        return {'total': 1, 'passed': 1, 'failed': 0}
        
    except Exception as e:
        print(f"[FAIL] requirements.txt - Error: {str(e)}")
        return {'total': 1, 'passed': 0, 'failed': 1}


def test_performance():
    """간단한 성능 테스트"""
    print("\n=== 성능 테스트 ===")
    
    python_files = [f for f in os.listdir('.') if f.endswith('.py')][:5]
    results = {'total': len(python_files), 'passed': 0, 'failed': 0}
    
    slow_files = []
    
    for py_file in python_files:
        start_time = time.time()
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                f.read()
            
            load_time = time.time() - start_time
            
            if load_time < 0.1:  # 0.1초 이하
                print(f"[PASS] {py_file} - {load_time:.3f}s")
                results['passed'] += 1
            else:
                print(f"[SLOW] {py_file} - {load_time:.3f}s")
                slow_files.append(py_file)
                results['failed'] += 1
                
        except Exception as e:
            print(f"[FAIL] {py_file} - Error: {str(e)}")
            results['failed'] += 1
    
    if slow_files:
        print(f"[INFO] 느린 파일들: {', '.join(slow_files)}")
    
    print(f"성능 테스트: {results['passed']}/{results['total']} 통과")
    return results


def main():
    """메인 실행 함수"""
    print("G4K 자동화 시스템 테스트 실행기")
    print("=" * 50)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"작업 디렉토리: {os.getcwd()}")
    print("=" * 50)
    
    start_time = time.time()
    
    # 테스트 실행
    all_results = []
    
    all_results.append(test_file_structure())
    all_results.append(test_json_files()) 
    all_results.append(test_python_syntax())
    all_results.append(test_requirements())
    all_results.append(test_performance())
    
    # 전체 결과 계산
    total_tests = sum(r['total'] for r in all_results)
    total_passed = sum(r['passed'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    runtime = time.time() - start_time
    
    # 결과 출력
    print("\n" + "=" * 50)
    print("전체 테스트 결과")
    print("=" * 50)
    print(f"총 테스트:     {total_tests:3d}")
    print(f"통과:         {total_passed:3d} ({success_rate:.1f}%)")
    print(f"실패:         {total_failed:3d}")
    print(f"실행 시간:    {runtime:.2f}초")
    
    # 결과 분석
    print(f"\n결과 분석:")
    if success_rate >= 95:
        print("  완벽! 모든 테스트가 거의 통과했습니다.")
        status = "EXCELLENT"
    elif success_rate >= 80:
        print("  양호! 대부분의 테스트가 통과했습니다.")
        status = "GOOD"
    elif success_rate >= 60:
        print("  주의! 일부 개선이 필요합니다.")
        status = "WARNING"
    else:
        print("  경고! 많은 문제가 발견되었습니다.")
        status = "CRITICAL"
    
    # JSON 보고서 저장
    report = {
        'timestamp': datetime.now().isoformat(),
        'runtime': runtime,
        'summary': {
            'total': total_tests,
            'passed': total_passed,
            'failed': total_failed,
            'success_rate': success_rate,
            'status': status
        },
        'detailed_results': all_results
    }
    
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n보고서 저장: {report_file}")
    except Exception as e:
        print(f"보고서 저장 실패: {e}")
    
    return success_rate >= 80


if __name__ == "__main__":
    # Windows 콘솔 인코딩 설정
    if sys.platform.startswith('win'):
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    success = main()
    sys.exit(0 if success else 1)
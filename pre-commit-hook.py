#!/usr/bin/env python3
"""
Pre-commit hook for G4K automation project
커밋 전 자동 테스트 실행
"""

import sys
import subprocess
import os


def run_pre_commit_tests():
    """커밋 전 테스트 실행"""
    print("🔍 Pre-commit 테스트 실행 중...")
    
    tests_passed = True
    
    # 1. 기본 구조 테스트
    print("1️⃣ 기본 구조 확인...")
    try:
        result = subprocess.run([
            sys.executable, 'simple_test_runner.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ 기본 구조 테스트 통과")
        else:
            print("   ❌ 기본 구조 테스트 실패")
            print(f"   오류: {result.stderr[:200]}...")
            tests_passed = False
    except Exception as e:
        print(f"   💥 기본 구조 테스트 오류: {e}")
        tests_passed = False
    
    # 2. Python 문법 검사
    print("\n2️⃣ Python 문법 검사...")
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    syntax_errors = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, py_file, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{py_file}:{e.lineno}: {e.msg}")
            tests_passed = False
        except Exception:
            pass  # 다른 오류는 무시
    
    if syntax_errors:
        print("   ❌ 문법 오류 발견:")
        for error in syntax_errors[:3]:  # 처음 3개만 표시
            print(f"      {error}")
    else:
        print("   ✅ Python 문법 검사 통과")
    
    # 3. JSON 파일 검증
    print("\n3️⃣ 설정 파일 검증...")
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    json_errors = []
    
    for json_file in json_files:
        try:
            import json
            with open(json_file, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            json_errors.append(f"{json_file}: {str(e)}")
            tests_passed = False
        except Exception:
            pass
    
    if json_errors:
        print("   ❌ JSON 파일 오류:")
        for error in json_errors[:2]:
            print(f"      {error}")
    else:
        print("   ✅ 설정 파일 검증 통과")
    
    # 결과 출력
    print("\n" + "="*50)
    if tests_passed:
        print("✅ Pre-commit 테스트 모두 통과!")
        print("커밋을 진행할 수 있습니다.")
        return True
    else:
        print("❌ Pre-commit 테스트 실패!")
        print("문제를 해결한 후 다시 커밋해주세요.")
        return False


def install_git_hook():
    """Git hook 설치"""
    if not os.path.exists('.git'):
        print("Git 저장소가 아닙니다.")
        return False
    
    hook_dir = '.git/hooks'
    hook_file = os.path.join(hook_dir, 'pre-commit')
    
    hook_content = f"""#!/bin/sh
# G4K Automation Pre-commit Hook
echo "🔍 Pre-commit 테스트 실행 중..."

python "{os.path.abspath(__file__)}"
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "❌ Pre-commit 테스트 실패. 커밋이 중단됩니다."
    exit 1
fi

echo "✅ Pre-commit 테스트 통과. 커밋을 진행합니다."
exit 0
"""
    
    try:
        os.makedirs(hook_dir, exist_ok=True)
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        # 실행 권한 부여 (Unix 계열)
        if hasattr(os, 'chmod'):
            os.chmod(hook_file, 0o755)
        
        print(f"✅ Git pre-commit hook 설치 완료: {hook_file}")
        return True
        
    except Exception as e:
        print(f"❌ Git hook 설치 실패: {e}")
        return False


def main():
    """메인 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description='G4K Pre-commit Hook')
    parser.add_argument('--install', action='store_true', help='Git hook 설치')
    parser.add_argument('--test', action='store_true', help='테스트만 실행')
    
    args = parser.parse_args()
    
    if args.install:
        success = install_git_hook()
        sys.exit(0 if success else 1)
    elif args.test or len(sys.argv) == 1:
        success = run_pre_commit_tests()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
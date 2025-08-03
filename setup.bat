@echo off
echo ========================================
echo G4K 방문예약 자동화 시스템 - 환경 설정
echo ========================================
echo.

echo [1/4] Python 버전 확인...
python --version
if errorlevel 1 (
    echo 오류: Python이 설치되지 않았습니다.
    echo https://www.python.org/downloads/ 에서 Python을 설치해주세요.
    pause
    exit /b 1
)

echo.
echo [2/4] 가상환경 생성 중...
if exist g4k_env (
    echo 기존 가상환경을 삭제합니다...
    rmdir /s /q g4k_env
)
python -m venv g4k_env
if errorlevel 1 (
    echo 오류: 가상환경 생성 실패
    pause
    exit /b 1
)

echo.
echo [3/4] 가상환경 활성화 중...
call g4k_env\Scripts\activate
if errorlevel 1 (
    echo 오류: 가상환경 활성화 실패
    pause
    exit /b 1
)

echo.
echo [4/4] 패키지 설치 중...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo 오류: 패키지 설치 실패
    echo 수동으로 다음 명령어를 실행해주세요:
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 환경 설정 완료!
echo ========================================
echo.
echo 🚀 프로그램 실행 방법:
echo.
echo 1. GUI 프로그램 (추천):
echo    python gui_manager.py
echo.
echo 2. 웹 대시보드:
echo    python web_dashboard.py
echo    브라우저에서 http://localhost:8080 접속
echo.
echo 3. CLI 도구:
echo    python config_manager_cli.py
echo.
echo 📝 가상환경 활성화:
echo    g4k_env\Scripts\activate
echo.
echo 📝 가상환경 비활성화:
echo    deactivate
echo.
echo ========================================
pause 
@echo off
echo =====================================
echo G4K 스텔스 자동화 시스템 v2
echo =====================================
echo.

REM Python 가상환경 활성화
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [경고] 가상환경이 없습니다. 생성 중...
    python -m venv venv
    call venv\Scripts\activate.bat
    
    echo 필수 패키지 설치 중...
    pip install --upgrade pip
    pip install undetected-chromedriver
    pip install -r requirements.txt
)

echo.
echo undetected-chromedriver 설치 확인 중...
pip show undetected-chromedriver >nul 2>&1
if errorlevel 1 (
    echo undetected-chromedriver 설치 중...
    pip install undetected-chromedriver
)

echo.
echo =====================================
echo 실행 옵션을 선택하세요:
echo 1. 스텔스 브라우저 테스트
echo 2. 개선된 하이브리드 자동화 (v2)
echo 3. 기존 자동화 시스템
echo =====================================
set /p choice="선택 (1-3): "

if "%choice%"=="1" (
    echo.
    echo 스텔스 브라우저 테스트를 시작합니다...
    python stealth_browser.py
) else if "%choice%"=="2" (
    echo.
    echo 개선된 하이브리드 자동화를 시작합니다...
    python g4k_hybrid_automation_v2.py
) else if "%choice%"=="3" (
    echo.
    echo 기존 자동화 시스템을 시작합니다...
    python g4k_hybrid_automation.py
) else (
    echo 잘못된 선택입니다.
)

echo.
pause
@echo off
title G4K 티켓팅 전용 시스템

echo =====================================
echo    G4K 티켓팅 전용 시스템 v2.0
echo =====================================
echo.
echo  9시 정각 예약 전쟁 최적화 버전
echo  0.05초의 차이가 승부를 가릅니다!
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
echo 시스템 체크 중...

REM undetected-chromedriver 확인
pip show undetected-chromedriver >nul 2>&1
if errorlevel 1 (
    echo undetected-chromedriver 설치 중...
    pip install undetected-chromedriver
)

REM Chrome 버전 확인
echo.
echo Chrome 버전 확인 중...
reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version 2>nul || (
    echo [경고] Chrome이 설치되어 있지 않거나 버전을 확인할 수 없습니다.
    echo Chrome 120 이상 버전이 필요합니다.
)

echo.
echo =====================================
echo        준비 완료! 시작합니다...
echo =====================================
echo.

REM 티켓팅 전용 모드 실행
python g4k_ticketing_automation.py

echo.
pause
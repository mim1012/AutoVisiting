@echo off
echo ========================================
echo G4K 방문예약 자동화 시스템 - 웹 대시보드
echo ========================================
echo.

echo 가상환경 활성화 중...
call g4k_env\Scripts\activate
if errorlevel 1 (
    echo 오류: 가상환경을 찾을 수 없습니다.
    echo setup.bat을 먼저 실행해주세요.
    pause
    exit /b 1
)

echo.
echo 웹 대시보드 시작 중...
echo 브라우저에서 http://localhost:8080 으로 접속하세요.
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.
python web_dashboard.py

echo.
echo 웹 대시보드가 종료되었습니다.
pause 
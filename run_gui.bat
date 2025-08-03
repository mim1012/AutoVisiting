@echo off
echo ========================================
echo G4K 방문예약 자동화 시스템 - GUI 실행
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
echo GUI 프로그램 시작 중...
python gui_manager.py

echo.
echo 프로그램이 종료되었습니다.
pause 
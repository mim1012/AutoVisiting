@echo off
echo ===============================================
echo G4K 자동화 시스템 통합 테스트 실행
echo ===============================================

echo.
echo 🚀 통합 테스트 실행 중...
python run_tests.py

echo.
echo 📊 결과 확인을 위해 아무 키나 누르세요...
pause > nul

echo.
echo ✅ 테스트 완료!
echo 상세 결과는 생성된 JSON 파일을 확인하세요.

pause
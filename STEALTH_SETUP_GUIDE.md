# 🛡️ G4K 스텔스 자동화 설치 및 사용 가이드

## 📋 사전 준비사항

1. **Chrome 브라우저 최신 버전** (120 이상)
2. **Python 3.8 이상** 설치
3. **Windows Defender 실시간 보호 일시 중지** (선택사항)

## 🚀 빠른 시작

### 1. 실행
```batch
run_stealth.bat
```

### 2. 옵션 선택
- **옵션 1**: 스텔스 브라우저 테스트 (404 에러 확인용)
- **옵션 2**: 개선된 자동화 시스템 (권장)
- **옵션 3**: 기존 시스템 (문제 발생 시)

## 🔧 수동 설치 (run_stealth.bat 실패 시)

```batch
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
venv\Scripts\activate.bat

# 3. 패키지 설치
pip install --upgrade pip
pip install undetected-chromedriver
pip install -r requirements.txt

# 4. 실행
python g4k_hybrid_automation_v2.py
```

## 📖 사용 방법

### 스텝 1: 프로그램 시작
1. `run_stealth.bat` 실행
2. 옵션 2 선택 (개선된 하이브리드 자동화)

### 스텝 2: 수동 로그인
1. 자동으로 Chrome이 열립니다
2. G4K 사이트에서 **수동으로 로그인**
3. 로그인 완료 후 콘솔에서 **Enter** 키

### 스텝 3: 3단계까지 수동 진행
1. 방문예약 메뉴 클릭
2. 주의사항 동의
3. 서비스 선택
4. **날짜 선택 화면**까지 진행
5. 콘솔에서 **Enter** 키

### 스텝 4: 자동화 시작
- 프로그램이 자동으로:
  - ✅ 캘린더 모니터링
  - ✅ 예약 가능 날짜 감지
  - ✅ 날짜 자동 선택
  - ✅ 여권번호 자동 입력

## 🔍 문제 해결

### 404 에러가 계속 발생하는 경우

1. **Chrome 프로필 초기화**
   ```batch
   rmdir /s /q %TEMP%\chrome_debug_profile
   ```

2. **다른 시간대 시도**
   - 새벽 3-6시 (서버 부하 적음)
   - 점심시간 피하기

3. **VPN 확인**
   - VPN 사용 중이면 끄기
   - 한국 IP 확인

### "undetected-chromedriver" 설치 실패

```batch
# 관리자 권한으로 CMD 실행 후
pip install --upgrade pip
pip install undetected-chromedriver --no-cache-dir
```

### Chrome 버전 불일치

1. Chrome 버전 확인: `chrome://version`
2. 버전이 120 미만이면 Chrome 업데이트
3. `stealth_browser.py`에서 버전 수정:
   ```python
   driver = uc.Chrome(options=options, version_main=YOUR_VERSION)
   ```

## ⚡ 성능 팁

1. **불필요한 확장 프로그램 비활성화**
2. **다른 Chrome 창 모두 닫기**
3. **백신 프로그램 일시 중지**

## 📊 테스트 결과 확인

로그 파일 위치:
- `g4k_automation_v2.log` - 실행 로그
- `debug_log.json` - 디버그 정보

## 🚨 주의사항

1. **과도한 사용 금지** - 계정 차단 위험
2. **개인정보 보호** - 로그 파일 공유 주의
3. **합법적 사용** - 본인 예약만 사용

## 💡 추가 기능

### 프로필 변경
```batch
python config_manager_cli.py profile set-active user1
```

### 자동 체크 설정
```batch
python config_manager_cli.py auto-check enable accept_terms
```

---

문제가 지속되면 `g4k_automation_v2.log` 파일 내용을 확인하세요.
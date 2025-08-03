# G4K 방문예약 하이브리드 자동화 시스템

## 개요

G4K 재외동포365민원포털의 방문예약을 효율적으로 처리하기 위한 하이브리드 자동화 시스템입니다. 
사용자가 로그인을 수동으로 처리하고, 나머지 예약 과정은 자동화하여 보안성과 편의성을 모두 확보했습니다.

## 주요 특징

- **하이브리드 방식**: 로그인은 수동, 예약 과정은 자동화
- **페이지 렉 대응**: 적응형 타임아웃 및 지능적 재시도 메커니즘
- **서버 과부하 대응**: 네트워크 상태 모니터링 및 백오프 알고리즘
- **사용자 친화적**: 직관적인 진행 상황 표시 및 안내
- **안정성**: 다단계 오류 처리 및 복구 메커니즘

## 시스템 요구사항

- Python 3.8 이상
- Chrome 브라우저
- 안정적인 인터넷 연결
- Windows 10/11, macOS 10.14+, Ubuntu 18.04+ 지원

## 설치 방법

### 1. 저장소 클론 및 디렉토리 이동
```bash
git clone <repository-url>
cd g4k-automation
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 3. 필수 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. Chrome 브라우저 및 ChromeDriver 설치
- Chrome 브라우저가 설치되어 있지 않다면 [공식 사이트](https://www.google.com/chrome/)에서 다운로드
- ChromeDriver는 webdriver-manager가 자동으로 관리

## 설정 방법

### 1. 설정 파일 수정
`config.yaml` 파일을 열어 개인 정보를 입력합니다:

```yaml
user_profiles:
  default:
    name: "홍길동"           # 실제 이름으로 변경
    phone: "010-1234-5678"   # 실제 연락처로 변경
    email: "user@example.com" # 실제 이메일로 변경

reservation_settings:
  preferred_dates:
    - "2024-01-15"  # 희망 날짜로 변경
    - "2024-01-16"
  preferred_times:
    - "09:00"       # 희망 시간으로 변경
    - "10:00"
```

### 2. 알림 설정 (선택사항)
이메일 알림을 원하는 경우:

```yaml
notifications:
  email:
    enabled: true
    username: "your_email@gmail.com"
    password: "your_app_password"
    recipient: "your_email@gmail.com"
```

## 사용 방법

### 1. 프로그램 실행
```bash
python g4k_hybrid_automation.py
```

### 2. 로그인 수행
- 프로그램이 Chrome 브라우저를 열고 G4K 사이트로 이동합니다
- 브라우저에서 직접 로그인을 수행합니다:
  - 회원 로그인 또는 비회원 로그인 선택
  - 필요한 정보 입력 및 보안문자 해결
  - 이메일/SMS 인증 완료

### 3. 자동화 진행
- 로그인 완료가 감지되면 자동으로 예약 과정이 시작됩니다
- 진행 상황이 콘솔에 실시간으로 표시됩니다
- 문제 발생 시 자동으로 재시도하거나 사용자에게 안내합니다

### 4. 결과 확인
- 예약 완료 시 성공 메시지가 표시됩니다
- 실패 시 오류 원인과 해결 방안이 안내됩니다
- 모든 과정은 로그 파일에 기록됩니다

## 문제 해결

### 자주 발생하는 문제

#### 1. 로그인 감지 실패
**증상**: 로그인했는데 자동화가 시작되지 않음
**해결방법**: 
- 로그인 후 메인 페이지로 이동했는지 확인
- 브라우저를 새로고침하고 다시 시도
- 로그아웃 후 다시 로그인

#### 2. 페이지 로딩 오류
**증상**: "요소를 찾을 수 없습니다" 오류
**해결방법**:
- 네트워크 연결 상태 확인
- config.yaml에서 timeout 값 증가
- 서버 부하가 높은 시간대 피하기

#### 3. 예약 가능 시간 없음
**증상**: 모든 희망 시간 선택 실패
**해결방법**:
- config.yaml에서 더 많은 날짜/시간 추가
- 인기가 적은 시간대 선택
- 주기적으로 재시도

### 로그 파일 확인
상세한 오류 정보는 `g4k_automation.log` 파일에서 확인할 수 있습니다:

```bash
tail -f g4k_automation.log  # 실시간 로그 확인
```

## 고급 설정

### 성능 최적화
시스템 리소스가 제한적인 경우:

```yaml
performance:
  max_memory_usage: "1GB"
  cpu_limit_percent: 30
  block_resources:
    images: true
    css: true
    fonts: true
```

### 네트워크 최적화
느린 네트워크 환경의 경우:

```yaml
network:
  response_time_threshold: 20.0
  connection_timeout: 60
  read_timeout: 120

system:
  retry:
    max_attempts: 10
    max_delay: 60
```

### 디버그 모드
문제 진단을 위한 디버그 설정:

```yaml
debug:
  screenshot_on_error: true
  save_page_source: true
  verbose_logging: true
  step_by_step_mode: true
```

## 보안 고려사항

### 개인정보 보호
- 설정 파일에 저장된 개인정보는 암호화되지 않으므로 주의
- 공용 컴퓨터에서 사용 후 설정 파일 삭제 권장
- 로그 파일에는 개인정보가 기록되지 않음

### 세션 보안
- 프로그램 종료 시 브라우저 세션 자동 삭제
- 세션 타임아웃 설정으로 장시간 방치 방지
- 의심스러운 활동 감지 시 자동 중단

## 법적 고지사항

- 본 프로그램은 개인 사용 목적으로만 제공됩니다
- G4K 사이트의 이용약관을 준수해야 합니다
- 과도한 사용으로 인한 서버 부하 방지에 협조해 주세요
- 상업적 이용이나 대량 처리는 금지됩니다

## 지원 및 문의

### 기술 지원
- GitHub Issues를 통한 버그 신고
- 사용법 문의는 Discussion 활용
- 긴급한 문제는 이메일로 연락

### 기여 방법
- Fork 후 Pull Request 제출
- 코딩 스타일 가이드 준수
- 테스트 코드 작성 필수

## 라이선스

MIT License - 자세한 내용은 LICENSE 파일 참조

## 업데이트 내역

### v1.0.0 (2024-01-01)
- 초기 릴리스
- 하이브리드 자동화 시스템 구현
- 페이지 렉 및 서버 과부하 대응 메커니즘 추가

### v1.1.0 (예정)
- 다중 사용자 지원
- 웹 대시보드 추가
- 머신러닝 기반 최적화


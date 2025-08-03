# G4K 방문예약 자동화 시스템 - 자동 입력 설정 가이드

## 📋 개요

이 시스템은 G4K 재외동포365민원포털의 방문예약 과정에서 **약관 동의**, **센터/공관 선택**, **민원/방문일시 선택**, **신청자 정보 입력** 등을 자동으로 처리할 수 있도록 설계되었습니다.

## 🚀 주요 기능

### 1. 자동 입력 기능
- ✅ **약관 동의**: 모든 체크박스 자동 선택
- 🏢 **센터/공관 선택**: 설정된 센터 자동 선택
- 📅 **날짜/시간 선택**: 희망 날짜/시간 우선순위별 자동 선택
- 👤 **신청자 정보 입력**: 프로필 정보 자동 입력
- 🔄 **최종 확인**: 요약 정보 표시 및 자동/수동 확인

### 2. 설정 관리
- 👥 **다중 사용자 프로필**: 여러 사용자 정보 관리
- 📝 **예약 템플릿**: 다양한 서비스별 예약 설정
- ⚙️ **자동 체크 설정**: 각 단계별 자동화 옵션 설정

## 📁 파일 구조

```
프로젝트/
├── user_profiles.json              # 사용자 프로필 정보
├── reservation_templates.json      # 예약 템플릿 설정
├── auto_check_settings.json        # 자동 체크 설정
├── profile_manager.py              # 프로필 관리 모듈
├── auto_input_handler.py           # 자동 입력 처리 모듈
├── config_manager_cli.py           # 설정 관리 CLI 도구
└── g4k_hybrid_automation.py        # 통합 자동화 시스템
```

## 🛠️ 초기 설정

### 1. 기본 설정 파일 생성
```bash
python config_manager_cli.py init
```

이 명령어는 다음 파일들을 자동으로 생성합니다:
- `user_profiles.json`: 기본 사용자 프로필
- `reservation_templates.json`: 기본 예약 템플릿
- `auto_check_settings.json`: 기본 자동 체크 설정

### 2. 설정 검증
```bash
python config_manager_cli.py validate
```

## 👤 사용자 프로필 관리

### 프로필 목록 조회
```bash
python config_manager_cli.py profile list
```

### 새 프로필 추가
```bash
python config_manager_cli.py profile add my_profile
```
- 이름, 영문 이름, 전화번호, 이메일, 신분증 정보 등을 입력
- 비상연락처 정보 선택적 추가

### 프로필 정보 조회
```bash
python config_manager_cli.py profile show my_profile
```

### 활성 프로필 설정
```bash
python config_manager_cli.py profile set-active my_profile
```

### 프로필 정보 업데이트
```bash
python config_manager_cli.py profile update my_profile --phone "010-9876-5432"
```

## 📝 예약 템플릿 관리

### 템플릿 목록 조회
```bash
python config_manager_cli.py template list
```

### 새 템플릿 추가
```bash
python config_manager_cli.py template add my_template
```
- 서비스 타입, 센터 타입, 희망 날짜/시간 설정
- 구비서류 목록 설정
- 자동 재시도 설정

### 템플릿 정보 조회
```bash
python config_manager_cli.py template show my_template
```

### 활성 템플릿 설정
```bash
python config_manager_cli.py template set-active my_template
```

## ⚙️ 자동 체크 설정 관리

### 자동 체크 설정 조회
```bash
python config_manager_cli.py auto-check show
```

### 특정 자동 체크 활성화/비활성화
```bash
# 약관 동의 자동 체크 활성화
python config_manager_cli.py auto-check enable terms_agreement

# 센터 선택 자동 체크 비활성화
python config_manager_cli.py auto-check disable center_selection
```

## 🔧 설정 파일 직접 편집

### 1. 사용자 프로필 (user_profiles.json)
```json
{
  "profiles": {
    "default": {
      "name": "홍길동",
      "name_english": "Hong Gildong",
      "phone": "010-1234-5678",
      "email": "user@example.com",
      "id_type": "passport",
      "id_number": "M12345678",
      "birth_date": "1990-01-01",
      "nationality": "KR",
      "address": "서울특별시 강남구",
      "emergency_contact": {
        "name": "김철수",
        "phone": "010-9876-5432",
        "relationship": "친구"
      }
    }
  },
  "active_profile": "default"
}
```

### 2. 예약 템플릿 (reservation_templates.json)
```json
{
  "templates": {
    "drivers_license_renewal": {
      "name": "운전면허증 갱신",
      "center_type": "gwanghwamun",
      "service_type": "drivers_license",
      "service_detail": "renewal",
      "service_code": "DL001",
      "description": "운전면허증 갱신 예약",
      "required_documents": [
        "재외국민 주민등록증 또는 국내거소신고증(F-4)",
        "구 운전면허증"
      ],
      "preferred_dates": [
        "2024-01-15",
        "2024-01-16",
        "2024-01-17"
      ],
      "preferred_times": [
        "09:00",
        "10:00",
        "11:00"
      ],
      "auto_retry": {
        "enabled": true,
        "interval_minutes": 30,
        "max_retries": 10
      }
    }
  },
  "active_template": "drivers_license_renewal"
}
```

### 3. 자동 체크 설정 (auto_check_settings.json)
```json
{
  "auto_check_settings": {
    "terms_agreement": {
      "enabled": true,
      "auto_check_all": true,
      "required_checks": [
        "privacy_policy",
        "terms_of_service",
        "data_collection"
      ]
    },
    "center_selection": {
      "enabled": true,
      "auto_select": true,
      "preferred_centers": ["gwanghwamun", "embassy"]
    },
    "service_selection": {
      "enabled": true,
      "auto_select": true,
      "preferred_services": ["drivers_license", "passport"]
    },
    "date_time_selection": {
      "enabled": true,
      "auto_select": true,
      "flexible_dates": true,
      "flexible_times": true
    },
    "applicant_info": {
      "enabled": true,
      "auto_fill": true,
      "required_fields": ["name", "phone", "email", "id_type", "id_number"]
    },
    "confirmation": {
      "enabled": true,
      "auto_confirm": false,
      "require_user_confirmation": true,
      "show_summary": true
    }
  }
}
```

## 🚀 자동화 실행

### 1. 설정 확인
```bash
python config_manager_cli.py show-config
```

### 2. 자동화 실행
```bash
python g4k_hybrid_automation.py
```

## 📋 사용 시나리오

### 시나리오 1: 운전면허증 갱신 예약
1. **프로필 설정**: 사용자 정보 입력
2. **템플릿 설정**: 운전면허증 갱신 템플릿 선택
3. **자동 체크 설정**: 모든 단계 자동화 활성화
4. **자동화 실행**: 프로그램 실행 후 로그인만 수동 처리

### 시나리오 2: 여권 갱신 예약
1. **프로필 설정**: 사용자 정보 입력
2. **템플릿 설정**: 여권 갱신 템플릿 선택
3. **자동 체크 설정**: 신청자 정보 입력만 자동화
4. **자동화 실행**: 일부 단계는 수동 처리

## ⚠️ 주의사항

### 1. 보안 고려사항
- 개인정보가 포함된 설정 파일은 안전하게 보관
- 설정 파일 백업 권장
- 공용 컴퓨터에서는 사용 금지

### 2. 사용 제한
- G4K 사이트 정책 준수
- 과도한 요청 방지
- 서버 부하 고려

### 3. 오류 처리
- 네트워크 오류 시 자동 재시도
- 설정 오류 시 검증 메시지 표시
- 로그 파일 확인 권장

## 🔍 문제 해결

### 설정 오류
```bash
# 설정 검증
python config_manager_cli.py validate

# 설정 요약 확인
python config_manager_cli.py show-config
```

### 자동화 실패
1. 로그 파일 확인: `g4k_automation.log`
2. 설정 파일 유효성 검증
3. 네트워크 연결 상태 확인
4. G4K 사이트 접근 가능 여부 확인

### 프로필 오류
- 필수 필드 누락 확인
- 데이터 형식 검증 (전화번호, 이메일 등)
- 신분증 번호 형식 확인

## 📞 지원

문제가 발생하거나 추가 기능이 필요한 경우:
1. 로그 파일 확인
2. 설정 파일 검증
3. 네트워크 상태 확인
4. G4K 사이트 정책 확인

---

**🎯 이 시스템을 통해 G4K 방문예약을 더욱 편리하고 효율적으로 처리할 수 있습니다!** 
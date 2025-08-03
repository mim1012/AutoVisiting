#!/usr/bin/env python3
"""
G4K 방문예약 자동화 시스템 - 프로필 관리 모듈
사용자 프로필, 예약 템플릿, 자동 체크 설정을 관리
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class ProfileManager:
    """사용자 프로필 관리 클래스"""
    
    def __init__(self, profiles_file: str = "user_profiles.json"):
        self.profiles_file = profiles_file
        self.profiles = {}
        self.active_profile = None
        self.load_profiles()
    
    def load_profiles(self) -> bool:
        """프로필 파일 로드"""
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.profiles = data.get('profiles', {})
                    self.active_profile = data.get('active_profile', 'default')
                logger.info(f"프로필 로드 완료: {len(self.profiles)}개 프로필")
                return True
            else:
                logger.warning(f"프로필 파일이 존재하지 않습니다: {self.profiles_file}")
                return False
        except Exception as e:
            logger.error(f"프로필 로드 실패: {e}")
            return False
    
    def save_profiles(self) -> bool:
        """프로필 파일 저장"""
        try:
            data = {
                'profiles': self.profiles,
                'active_profile': self.active_profile
            }
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("프로필 저장 완료")
            return True
        except Exception as e:
            logger.error(f"프로필 저장 실패: {e}")
            return False
    
    def get_active_profile(self) -> Optional[Dict[str, Any]]:
        """현재 활성 프로필 반환"""
        return self.profiles.get(self.active_profile)
    
    def set_active_profile(self, profile_name: str) -> bool:
        """활성 프로필 설정"""
        if profile_name in self.profiles:
            self.active_profile = profile_name
            self.save_profiles()
            logger.info(f"활성 프로필 변경: {profile_name}")
            return True
        else:
            logger.error(f"프로필이 존재하지 않습니다: {profile_name}")
            return False
    
    def add_profile(self, name: str, profile_data: Dict[str, Any]) -> bool:
        """새 프로필 추가"""
        try:
            # 필수 필드 검증
            required_fields = ['name', 'phone', 'email', 'id_type', 'id_number']
            for field in required_fields:
                if field not in profile_data:
                    logger.error(f"필수 필드 누락: {field}")
                    return False
            
            self.profiles[name] = profile_data
            self.save_profiles()
            logger.info(f"프로필 추가 완료: {name}")
            return True
        except Exception as e:
            logger.error(f"프로필 추가 실패: {e}")
            return False
    
    def update_profile(self, name: str, profile_data: Dict[str, Any]) -> bool:
        """프로필 업데이트"""
        if name in self.profiles:
            self.profiles[name].update(profile_data)
            self.save_profiles()
            logger.info(f"프로필 업데이트 완료: {name}")
            return True
        else:
            logger.error(f"프로필이 존재하지 않습니다: {name}")
            return False
    
    def delete_profile(self, name: str) -> bool:
        """프로필 삭제"""
        if name in self.profiles and name != 'default':
            del self.profiles[name]
            if self.active_profile == name:
                self.active_profile = 'default'
            self.save_profiles()
            logger.info(f"프로필 삭제 완료: {name}")
            return True
        else:
            logger.error(f"프로필 삭제 실패: {name}")
            return False
    
    def list_profiles(self) -> List[str]:
        """프로필 목록 반환"""
        return list(self.profiles.keys())
    
    def validate_profile(self, profile_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """프로필 데이터 검증"""
        errors = []
        warnings = []
        
        # 전화번호 형식 검증
        phone = profile_data.get('phone', '')
        if not re.match(r'^01[0-9]-[0-9]{4}-[0-9]{4}$', phone):
            errors.append("전화번호 형식이 올바르지 않습니다 (예: 010-1234-5678)")
        
        # 이메일 형식 검증
        email = profile_data.get('email', '')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append("이메일 형식이 올바르지 않습니다")
        
        # 여권번호 형식 검증
        id_type = profile_data.get('id_type', '')
        id_number = profile_data.get('id_number', '')
        
        if id_type == 'passport':
            if not re.match(r'^[A-Z][0-9]{8}$', id_number):
                errors.append("여권번호 형식이 올바르지 않습니다 (예: M12345678)")
        elif id_type == 'residence_card':
            if not re.match(r'^F-4-[0-9]{9}$', id_number):
                errors.append("거소신고증 번호 형식이 올바르지 않습니다 (예: F-4-123456789)")
        
        # 생년월일 검증
        birth_date = profile_data.get('birth_date', '')
        if birth_date:
            try:
                datetime.strptime(birth_date, '%Y-%m-%d')
            except ValueError:
                errors.append("생년월일 형식이 올바르지 않습니다 (예: 1990-01-01)")
        
        return {'errors': errors, 'warnings': warnings}


class ReservationTemplateManager:
    """예약 템플릿 관리 클래스"""
    
    def __init__(self, templates_file: str = "reservation_templates.json"):
        self.templates_file = templates_file
        self.templates = {}
        self.active_template = None
        self.load_templates()
    
    def load_templates(self) -> bool:
        """템플릿 파일 로드"""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.templates = data.get('templates', {})
                    self.active_template = data.get('active_template', 'drivers_license_renewal')
                logger.info(f"템플릿 로드 완료: {len(self.templates)}개 템플릿")
                return True
            else:
                logger.warning(f"템플릿 파일이 존재하지 않습니다: {self.templates_file}")
                return False
        except Exception as e:
            logger.error(f"템플릿 로드 실패: {e}")
            return False
    
    def save_templates(self) -> bool:
        """템플릿 파일 저장"""
        try:
            data = {
                'templates': self.templates,
                'active_template': self.active_template
            }
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("템플릿 저장 완료")
            return True
        except Exception as e:
            logger.error(f"템플릿 저장 실패: {e}")
            return False
    
    def get_active_template(self) -> Optional[Dict[str, Any]]:
        """현재 활성 템플릿 반환"""
        return self.templates.get(self.active_template)
    
    def set_active_template(self, template_name: str) -> bool:
        """활성 템플릿 설정"""
        if template_name in self.templates:
            self.active_template = template_name
            self.save_templates()
            logger.info(f"활성 템플릿 변경: {template_name}")
            return True
        else:
            logger.error(f"템플릿이 존재하지 않습니다: {template_name}")
            return False
    
    def add_template(self, name: str, template_data: Dict[str, Any]) -> bool:
        """새 템플릿 추가"""
        try:
            # 필수 필드 검증
            required_fields = ['name', 'center_type', 'service_type', 'service_detail']
            for field in required_fields:
                if field not in template_data:
                    logger.error(f"필수 필드 누락: {field}")
                    return False
            
            self.templates[name] = template_data
            self.save_templates()
            logger.info(f"템플릿 추가 완료: {name}")
            return True
        except Exception as e:
            logger.error(f"템플릿 추가 실패: {e}")
            return False
    
    def update_template(self, name: str, template_data: Dict[str, Any]) -> bool:
        """템플릿 업데이트"""
        if name in self.templates:
            self.templates[name].update(template_data)
            self.save_templates()
            logger.info(f"템플릿 업데이트 완료: {name}")
            return True
        else:
            logger.error(f"템플릿이 존재하지 않습니다: {name}")
            return False
    
    def delete_template(self, name: str) -> bool:
        """템플릿 삭제"""
        if name in self.templates and name != 'drivers_license_renewal':
            del self.templates[name]
            if self.active_template == name:
                self.active_template = 'drivers_license_renewal'
            self.save_templates()
            logger.info(f"템플릿 삭제 완료: {name}")
            return True
        else:
            logger.error(f"템플릿 삭제 실패: {name}")
            return False
    
    def list_templates(self) -> List[str]:
        """템플릿 목록 반환"""
        return list(self.templates.keys())
    
    def get_template_by_service(self, service_type: str, service_detail: str) -> Optional[Dict[str, Any]]:
        """서비스 타입으로 템플릿 찾기"""
        for template in self.templates.values():
            if (template.get('service_type') == service_type and 
                template.get('service_detail') == service_detail):
                return template
        return None


class AutoCheckManager:
    """자동 체크 설정 관리 클래스"""
    
    def __init__(self, settings_file: str = "auto_check_settings.json"):
        self.settings_file = settings_file
        self.settings = {}
        self.load_settings()
    
    def load_settings(self) -> bool:
        """설정 파일 로드"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                logger.info("자동 체크 설정 로드 완료")
                return True
            else:
                logger.warning(f"설정 파일이 존재하지 않습니다: {self.settings_file}")
                return False
        except Exception as e:
            logger.error(f"설정 로드 실패: {e}")
            return False
    
    def save_settings(self) -> bool:
        """설정 파일 저장"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.info("자동 체크 설정 저장 완료")
            return True
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """설정값 가져오기"""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set_setting(self, key: str, value: Any) -> bool:
        """설정값 설정"""
        try:
            keys = key.split('.')
            current = self.settings
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
            self.save_settings()
            return True
        except Exception as e:
            logger.error(f"설정 변경 실패: {e}")
            return False
    
    def is_auto_check_enabled(self, check_type: str) -> bool:
        """자동 체크 활성화 여부 확인"""
        return self.get_setting(f'auto_check_settings.{check_type}.enabled', False)
    
    def get_required_checks(self, check_type: str) -> List[str]:
        """필수 체크 항목 가져오기"""
        return self.get_setting(f'auto_check_settings.{check_type}.required_checks', [])
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """검증 규칙 가져오기"""
        return self.get_setting('validation_rules', {})


class ConfigManager:
    """통합 설정 관리 클래스"""
    
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.template_manager = ReservationTemplateManager()
        self.auto_check_manager = AutoCheckManager()
    
    def get_reservation_config(self) -> Dict[str, Any]:
        """예약 설정 통합 반환"""
        profile = self.profile_manager.get_active_profile()
        template = self.template_manager.get_active_template()
        
        if not profile or not template:
            logger.error("활성 프로필 또는 템플릿이 설정되지 않았습니다")
            return {}
        
        config = {
            'user_info': profile,
            'reservation_info': template,
            'auto_check_settings': self.auto_check_manager.settings.get('auto_check_settings', {}),
            'validation_rules': self.auto_check_manager.settings.get('validation_rules', {})
        }
        
        return config
    
    def validate_config(self) -> Dict[str, List[str]]:
        """설정 유효성 검증"""
        errors = []
        warnings = []
        
        # 프로필 검증
        profile = self.profile_manager.get_active_profile()
        if profile:
            profile_errors = self.profile_manager.validate_profile(profile)
            errors.extend(profile_errors['errors'])
            warnings.extend(profile_errors['warnings'])
        else:
            errors.append("활성 프로필이 설정되지 않았습니다")
        
        # 템플릿 검증
        template = self.template_manager.get_active_template()
        if not template:
            errors.append("활성 템플릿이 설정되지 않았습니다")
        
        return {'errors': errors, 'warnings': warnings}
    
    def create_reservation_request(self) -> Dict[str, Any]:
        """예약 요청 데이터 생성"""
        config = self.get_reservation_config()
        
        if not config:
            return {}
        
        request_data = {
            'user_profile': config['user_info'],
            'reservation_template': config['reservation_info'],
            'auto_check_settings': config['auto_check_settings'],
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        return request_data


def main():
    """테스트 함수"""
    config_manager = ConfigManager()
    
    # 설정 검증
    validation = config_manager.validate_config()
    if validation['errors']:
        print("오류:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    if validation['warnings']:
        print("경고:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    # 예약 요청 데이터 생성
    request_data = config_manager.create_reservation_request()
    if request_data:
        print("\n예약 요청 데이터:")
        print(json.dumps(request_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main() 
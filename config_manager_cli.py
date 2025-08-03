#!/usr/bin/env python3
"""
G4K 방문예약 자동화 시스템 - 설정 관리 CLI 도구
사용자 프로필, 예약 템플릿, 자동 체크 설정을 관리하는 명령줄 인터페이스
"""

import click
import json
import os
from typing import Dict, Any
from profile_manager import ConfigManager, ProfileManager, ReservationTemplateManager, AutoCheckManager

@click.group()
def cli():
    """G4K 방문예약 자동화 시스템 설정 관리 도구"""
    pass

@cli.group()
def profile():
    """사용자 프로필 관리"""
    pass

@profile.command('list')
def list_profiles():
    """프로필 목록 조회"""
    manager = ProfileManager()
    profiles = manager.list_profiles()
    active_profile = manager.active_profile
    
    click.echo("=== 사용자 프로필 목록 ===")
    for profile_name in profiles:
        if profile_name == active_profile:
            click.echo(f"* {profile_name} (활성)")
        else:
            click.echo(f"  {profile_name}")
    
    if not profiles:
        click.echo("등록된 프로필이 없습니다.")

@profile.command('show')
@click.argument('profile_name', default=None)
def show_profile(profile_name):
    """프로필 상세 정보 조회"""
    manager = ProfileManager()
    
    if profile_name is None:
        profile_name = manager.active_profile
    
    profile_data = manager.profiles.get(profile_name)
    if not profile_data:
        click.echo(f"프로필 '{profile_name}'을 찾을 수 없습니다.")
        return
    
    click.echo(f"=== 프로필: {profile_name} ===")
    for key, value in profile_data.items():
        if key == 'emergency_contact':
            click.echo(f"  {key}:")
            for ek, ev in value.items():
                click.echo(f"    {ek}: {ev}")
        else:
            click.echo(f"  {key}: {value}")

@profile.command('add')
@click.argument('profile_name')
@click.option('--name', prompt='이름', help='한글 이름')
@click.option('--name-english', prompt='영문 이름', help='영문 이름')
@click.option('--phone', prompt='전화번호', help='전화번호 (예: 010-1234-5678)')
@click.option('--email', prompt='이메일', help='이메일 주소')
@click.option('--id-type', type=click.Choice(['passport', 'residence_card']), prompt='신분증 종류', help='신분증 종류')
@click.option('--id-number', prompt='신분증 번호', help='신분증 번호')
@click.option('--birth-date', help='생년월일 (예: 1990-01-01)')
@click.option('--nationality', default='KR', help='국적 (기본값: KR)')
@click.option('--address', help='주소')
def add_profile(profile_name, **kwargs):
    """새 프로필 추가"""
    manager = ProfileManager()
    
    # 필수 필드 검증
    required_fields = ['name', 'name_english', 'phone', 'email', 'id_type', 'id_number']
    for field in required_fields:
        if not kwargs.get(field):
            click.echo(f"오류: 필수 필드 '{field}'이 누락되었습니다.")
            return
    
    # 프로필 데이터 구성
    profile_data = {k: v for k, v in kwargs.items() if v is not None}
    
    # 비상연락처 정보 추가
    if click.confirm('비상연락처 정보를 추가하시겠습니까?'):
        emergency_contact = {}
        emergency_contact['name'] = click.prompt('비상연락처 이름')
        emergency_contact['phone'] = click.prompt('비상연락처 전화번호')
        emergency_contact['relationship'] = click.prompt('관계')
        profile_data['emergency_contact'] = emergency_contact
    
    # 프로필 추가
    if manager.add_profile(profile_name, profile_data):
        click.echo(f"프로필 '{profile_name}'이 성공적으로 추가되었습니다.")
    else:
        click.echo("프로필 추가에 실패했습니다.")

@profile.command('set-active')
@click.argument('profile_name')
def set_active_profile(profile_name):
    """활성 프로필 설정"""
    manager = ProfileManager()
    
    if manager.set_active_profile(profile_name):
        click.echo(f"활성 프로필이 '{profile_name}'으로 변경되었습니다.")
    else:
        click.echo("활성 프로필 변경에 실패했습니다.")

@profile.command('update')
@click.argument('profile_name')
@click.option('--name', help='한글 이름')
@click.option('--name-english', help='영문 이름')
@click.option('--phone', help='전화번호')
@click.option('--email', help='이메일 주소')
@click.option('--id-type', type=click.Choice(['passport', 'residence_card']), help='신분증 종류')
@click.option('--id-number', help='신분증 번호')
@click.option('--birth-date', help='생년월일')
@click.option('--nationality', help='국적')
@click.option('--address', help='주소')
def update_profile(profile_name, **kwargs):
    """프로필 정보 업데이트"""
    manager = ProfileManager()
    
    # 업데이트할 필드만 필터링
    update_data = {k: v for k, v in kwargs.items() if v is not None}
    
    if not update_data:
        click.echo("업데이트할 필드가 지정되지 않았습니다.")
        return
    
    if manager.update_profile(profile_name, update_data):
        click.echo(f"프로필 '{profile_name}'이 성공적으로 업데이트되었습니다.")
    else:
        click.echo("프로필 업데이트에 실패했습니다.")

@profile.command('delete')
@click.argument('profile_name')
def delete_profile(profile_name):
    """프로필 삭제"""
    if not click.confirm(f"프로필 '{profile_name}'을 삭제하시겠습니까?'"):
        return
    
    manager = ProfileManager()
    if manager.delete_profile(profile_name):
        click.echo(f"프로필 '{profile_name}'이 삭제되었습니다.")
    else:
        click.echo("프로필 삭제에 실패했습니다.")

@cli.group()
def template():
    """예약 템플릿 관리"""
    pass

@template.command('list')
def list_templates():
    """템플릿 목록 조회"""
    manager = ReservationTemplateManager()
    templates = manager.list_templates()
    active_template = manager.active_template
    
    click.echo("=== 예약 템플릿 목록 ===")
    for template_name in templates:
        template_data = manager.templates.get(template_name, {})
        if template_name == active_template:
            click.echo(f"* {template_name} (활성) - {template_data.get('name', 'N/A')}")
        else:
            click.echo(f"  {template_name} - {template_data.get('name', 'N/A')}")
    
    if not templates:
        click.echo("등록된 템플릿이 없습니다.")

@template.command('show')
@click.argument('template_name', default=None)
def show_template(template_name):
    """템플릿 상세 정보 조회"""
    manager = ReservationTemplateManager()
    
    if template_name is None:
        template_name = manager.active_template
    
    template_data = manager.templates.get(template_name)
    if not template_data:
        click.echo(f"템플릿 '{template_name}'을 찾을 수 없습니다.")
        return
    
    click.echo(f"=== 템플릿: {template_name} ===")
    for key, value in template_data.items():
        if key in ['preferred_dates', 'preferred_times', 'required_documents']:
            click.echo(f"  {key}:")
            for item in value:
                click.echo(f"    - {item}")
        elif key == 'auto_retry':
            click.echo(f"  {key}:")
            for ek, ev in value.items():
                click.echo(f"    {ek}: {ev}")
        else:
            click.echo(f"  {key}: {value}")

@template.command('set-active')
@click.argument('template_name')
def set_active_template(template_name):
    """활성 템플릿 설정"""
    manager = ReservationTemplateManager()
    
    if manager.set_active_template(template_name):
        click.echo(f"활성 템플릿이 '{template_name}'으로 변경되었습니다.")
    else:
        click.echo("활성 템플릿 변경에 실패했습니다.")

@template.command('add')
@click.argument('template_name')
@click.option('--name', prompt='템플릿 이름', help='템플릿 표시 이름')
@click.option('--center-type', type=click.Choice(['gwanghwamun', 'embassy']), prompt='센터 타입', help='센터 타입')
@click.option('--service-type', prompt='서비스 타입', help='서비스 타입')
@click.option('--service-detail', prompt='서비스 상세', help='서비스 상세')
@click.option('--service-code', help='서비스 코드')
@click.option('--description', help='설명')
def add_template(template_name, **kwargs):
    """새 템플릿 추가"""
    manager = ReservationTemplateManager()
    
    # 필수 필드 검증
    required_fields = ['name', 'center_type', 'service_type', 'service_detail']
    for field in required_fields:
        if not kwargs.get(field):
            click.echo(f"오류: 필수 필드 '{field}'이 누락되었습니다.")
            return
    
    # 템플릿 데이터 구성
    template_data = {k: v for k, v in kwargs.items() if v is not None}
    
    # 추가 정보 입력
    if click.confirm('희망 날짜를 설정하시겠습니까?'):
        dates = []
        while True:
            date = click.prompt('희망 날짜 (YYYY-MM-DD, 빈 값으로 종료)')
            if not date:
                break
            dates.append(date)
        template_data['preferred_dates'] = dates
    
    if click.confirm('희망 시간을 설정하시겠습니까?'):
        times = []
        while True:
            time_slot = click.prompt('희망 시간 (HH:MM, 빈 값으로 종료)')
            if not time_slot:
                break
            times.append(time_slot)
        template_data['preferred_times'] = times
    
    if click.confirm('구비서류를 설정하시겠습니까?'):
        documents = []
        while True:
            doc = click.prompt('구비서류 (빈 값으로 종료)')
            if not doc:
                break
            documents.append(doc)
        template_data['required_documents'] = documents
    
    # 자동 재시도 설정
    template_data['auto_retry'] = {
        'enabled': click.confirm('자동 재시도를 활성화하시겠습니까?'),
        'interval_minutes': click.prompt('재시도 간격 (분)', type=int, default=30),
        'max_retries': click.prompt('최대 재시도 횟수', type=int, default=10)
    }
    
    # 템플릿 추가
    if manager.add_template(template_name, template_data):
        click.echo(f"템플릿 '{template_name}'이 성공적으로 추가되었습니다.")
    else:
        click.echo("템플릿 추가에 실패했습니다.")

@cli.group()
def auto_check():
    """자동 체크 설정 관리"""
    pass

@auto_check.command('show')
def show_auto_check_settings():
    """자동 체크 설정 조회"""
    manager = AutoCheckManager()
    settings = manager.settings.get('auto_check_settings', {})
    
    click.echo("=== 자동 체크 설정 ===")
    for check_type, config in settings.items():
        enabled = config.get('enabled', False)
        status = "활성화" if enabled else "비활성화"
        click.echo(f"  {check_type}: {status}")
        
        if enabled:
            for key, value in config.items():
                if key != 'enabled':
                    click.echo(f"    {key}: {value}")

@auto_check.command('enable')
@click.argument('check_type')
def enable_auto_check(check_type):
    """자동 체크 활성화"""
    manager = AutoCheckManager()
    
    if manager.set_setting(f'auto_check_settings.{check_type}.enabled', True):
        click.echo(f"'{check_type}' 자동 체크가 활성화되었습니다.")
    else:
        click.echo("자동 체크 활성화에 실패했습니다.")

@auto_check.command('disable')
@click.argument('check_type')
def disable_auto_check(check_type):
    """자동 체크 비활성화"""
    manager = AutoCheckManager()
    
    if manager.set_setting(f'auto_check_settings.{check_type}.enabled', False):
        click.echo(f"'{check_type}' 자동 체크가 비활성화되었습니다.")
    else:
        click.echo("자동 체크 비활성화에 실패했습니다.")

@cli.command()
def validate():
    """설정 유효성 검증"""
    config_manager = ConfigManager()
    validation = config_manager.validate_config()
    
    if validation['errors']:
        click.echo("❌ 설정 오류:")
        for error in validation['errors']:
            click.echo(f"  - {error}")
        return False
    
    if validation['warnings']:
        click.echo("⚠️  설정 경고:")
        for warning in validation['warnings']:
            click.echo(f"  - {warning}")
    
    click.echo("✅ 설정이 유효합니다.")
    return True

@cli.command()
def show_config():
    """전체 설정 요약 조회"""
    config_manager = ConfigManager()
    
    click.echo("=== G4K 방문예약 자동화 시스템 설정 요약 ===")
    
    # 활성 프로필
    profile = config_manager.profile_manager.get_active_profile()
    if profile:
        click.echo(f"활성 프로필: {profile.get('name', 'N/A')}")
    else:
        click.echo("활성 프로필: 설정되지 않음")
    
    # 활성 템플릿
    template = config_manager.template_manager.get_active_template()
    if template:
        click.echo(f"활성 템플릿: {template.get('name', 'N/A')}")
    else:
        click.echo("활성 템플릿: 설정되지 않음")
    
    # 자동 체크 설정
    auto_check_settings = config_manager.auto_check_manager.settings.get('auto_check_settings', {})
    enabled_checks = [k for k, v in auto_check_settings.items() if v.get('enabled', False)]
    click.echo(f"활성화된 자동 체크: {', '.join(enabled_checks) if enabled_checks else '없음'}")

@cli.command()
def init():
    """초기 설정 파일 생성"""
    # 기본 프로필 생성
    if not os.path.exists('user_profiles.json'):
        default_profile = {
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
        
        with open('user_profiles.json', 'w', encoding='utf-8') as f:
            json.dump(default_profile, f, ensure_ascii=False, indent=2)
        click.echo("✅ 기본 프로필 파일이 생성되었습니다.")
    
    # 기본 템플릿 생성
    if not os.path.exists('reservation_templates.json'):
        default_template = {
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
                        "enabled": True,
                        "interval_minutes": 30,
                        "max_retries": 10
                    }
                }
            },
            "active_template": "drivers_license_renewal"
        }
        
        with open('reservation_templates.json', 'w', encoding='utf-8') as f:
            json.dump(default_template, f, ensure_ascii=False, indent=2)
        click.echo("✅ 기본 템플릿 파일이 생성되었습니다.")
    
    # 기본 자동 체크 설정 생성
    if not os.path.exists('auto_check_settings.json'):
        default_auto_check = {
            "auto_check_settings": {
                "terms_agreement": {
                    "enabled": True,
                    "auto_check_all": True,
                    "required_checks": [
                        "privacy_policy",
                        "terms_of_service",
                        "data_collection"
                    ]
                },
                "center_selection": {
                    "enabled": True,
                    "auto_select": True,
                    "preferred_centers": ["gwanghwamun", "embassy"]
                },
                "service_selection": {
                    "enabled": True,
                    "auto_select": True,
                    "preferred_services": ["drivers_license", "passport"]
                },
                "date_time_selection": {
                    "enabled": True,
                    "auto_select": True,
                    "flexible_dates": True,
                    "flexible_times": True
                },
                "applicant_info": {
                    "enabled": True,
                    "auto_fill": True,
                    "required_fields": ["name", "phone", "email", "id_type", "id_number"]
                },
                "confirmation": {
                    "enabled": True,
                    "auto_confirm": False,
                    "require_user_confirmation": True,
                    "show_summary": True
                }
            }
        }
        
        with open('auto_check_settings.json', 'w', encoding='utf-8') as f:
            json.dump(default_auto_check, f, ensure_ascii=False, indent=2)
        click.echo("✅ 기본 자동 체크 설정 파일이 생성되었습니다.")
    
    click.echo("🎉 초기 설정이 완료되었습니다!")

if __name__ == '__main__':
    cli() 
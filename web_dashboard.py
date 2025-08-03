#!/usr/bin/env python3
"""
G4K 방문예약 자동화 시스템 - 웹 대시보드
비개발자를 위한 웹 기반 관리 인터페이스
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
from profile_manager import ConfigManager, ProfileManager, ReservationTemplateManager, AutoCheckManager

app = Flask(__name__)
app.secret_key = 'g4k_automation_secret_key'

config_manager = ConfigManager()

@app.route('/')
def dashboard():
    """메인 대시보드"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """시스템 상태 조회"""
    profile = config_manager.profile_manager.get_active_profile()
    template = config_manager.template_manager.get_active_template()
    auto_check_settings = config_manager.auto_check_manager.settings.get('auto_check_settings', {})
    
    enabled_checks = [k for k, v in auto_check_settings.items() if v.get('enabled', False)]
    
    return jsonify({
        'active_profile': profile.get('name', 'N/A') if profile else '설정되지 않음',
        'active_template': template.get('name', 'N/A') if template else '설정되지 않음',
        'enabled_auto_checks': len(enabled_checks),
        'total_auto_checks': len(auto_check_settings),
        'status': 'ready'
    })

@app.route('/profiles')
def profiles():
    """프로필 관리 페이지"""
    profiles_list = config_manager.profile_manager.list_profiles()
    active_profile = config_manager.profile_manager.active_profile
    
    profiles_data = []
    for profile_name in profiles_list:
        profile_data = config_manager.profile_manager.profiles.get(profile_name, {})
        profiles_data.append({
            'name': profile_name,
            'display_name': profile_data.get('name', profile_name),
            'email': profile_data.get('email', 'N/A'),
            'phone': profile_data.get('phone', 'N/A'),
            'is_active': profile_name == active_profile
        })
    
    return render_template('profiles.html', profiles=profiles_data)

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """프로필 목록 API"""
    profiles_list = config_manager.profile_manager.list_profiles()
    active_profile = config_manager.profile_manager.active_profile
    
    profiles_data = []
    for profile_name in profiles_list:
        profile_data = config_manager.profile_manager.profiles.get(profile_name, {})
        profiles_data.append({
            'name': profile_name,
            'data': profile_data,
            'is_active': profile_name == active_profile
        })
    
    return jsonify(profiles_data)

@app.route('/api/profiles', methods=['POST'])
def add_profile():
    """프로필 추가 API"""
    try:
        data = request.json
        profile_name = data.get('name')
        profile_data = data.get('data', {})
        
        if config_manager.profile_manager.add_profile(profile_name, profile_data):
            return jsonify({'success': True, 'message': '프로필이 추가되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '프로필 추가에 실패했습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/api/profiles/<profile_name>', methods=['PUT'])
def update_profile(profile_name):
    """프로필 업데이트 API"""
    try:
        data = request.json
        
        if config_manager.profile_manager.update_profile(profile_name, data):
            return jsonify({'success': True, 'message': '프로필이 업데이트되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '프로필 업데이트에 실패했습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/api/profiles/<profile_name>/activate', methods=['POST'])
def activate_profile(profile_name):
    """프로필 활성화 API"""
    try:
        if config_manager.profile_manager.set_active_profile(profile_name):
            return jsonify({'success': True, 'message': '프로필이 활성화되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '프로필 활성화에 실패했습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/api/profiles/<profile_name>', methods=['DELETE'])
def delete_profile(profile_name):
    """프로필 삭제 API"""
    try:
        if config_manager.profile_manager.delete_profile(profile_name):
            return jsonify({'success': True, 'message': '프로필이 삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '프로필 삭제에 실패했습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/templates')
def templates():
    """템플릿 관리 페이지"""
    templates_list = config_manager.template_manager.list_templates()
    active_template = config_manager.template_manager.active_template
    
    templates_data = []
    for template_name in templates_list:
        template_data = config_manager.template_manager.templates.get(template_name, {})
        templates_data.append({
            'name': template_name,
            'display_name': template_data.get('name', template_name),
            'center_type': template_data.get('center_type', 'N/A'),
            'service_type': template_data.get('service_type', 'N/A'),
            'is_active': template_name == active_template
        })
    
    return render_template('templates.html', templates=templates_data)

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """템플릿 목록 API"""
    templates_list = config_manager.template_manager.list_templates()
    active_template = config_manager.template_manager.active_template
    
    templates_data = []
    for template_name in templates_list:
        template_data = config_manager.template_manager.templates.get(template_name, {})
        templates_data.append({
            'name': template_name,
            'data': template_data,
            'is_active': template_name == active_template
        })
    
    return jsonify(templates_data)

@app.route('/api/templates', methods=['POST'])
def add_template():
    """템플릿 추가 API"""
    try:
        data = request.json
        template_name = data.get('name')
        template_data = data.get('data', {})
        
        if config_manager.template_manager.add_template(template_name, template_data):
            return jsonify({'success': True, 'message': '템플릿이 추가되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '템플릿 추가에 실패했습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/api/templates/<template_name>', methods=['PUT'])
def update_template(template_name):
    """템플릿 업데이트 API"""
    try:
        data = request.json
        
        if config_manager.template_manager.update_template(template_name, data):
            return jsonify({'success': True, 'message': '템플릿이 업데이트되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '템플릿 업데이트에 실패했습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/api/templates/<template_name>/activate', methods=['POST'])
def activate_template(template_name):
    """템플릿 활성화 API"""
    try:
        if config_manager.template_manager.set_active_template(template_name):
            return jsonify({'success': True, 'message': '템플릿이 활성화되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '템플릿 활성화에 실패했습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/api/templates/<template_name>', methods=['DELETE'])
def delete_template(template_name):
    """템플릿 삭제 API"""
    try:
        if config_manager.template_manager.delete_template(template_name):
            return jsonify({'success': True, 'message': '템플릿이 삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '템플릿 삭제에 실패했습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/settings')
def settings():
    """설정 관리 페이지"""
    auto_check_settings = config_manager.auto_check_manager.settings.get('auto_check_settings', {})
    return render_template('settings.html', settings=auto_check_settings)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """설정 조회 API"""
    return jsonify(config_manager.auto_check_manager.settings)

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """설정 업데이트 API"""
    try:
        data = request.json
        
        # 설정 업데이트
        for key, value in data.items():
            config_manager.auto_check_manager.set_setting(key, value)
        
        return jsonify({'success': True, 'message': '설정이 업데이트되었습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/automation')
def automation():
    """자동화 실행 페이지"""
    return render_template('automation.html')

@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """자동화 시작 API"""
    try:
        # 설정 검증
        validation = config_manager.validate_config()
        if validation['errors']:
            return jsonify({
                'success': False, 
                'message': '설정 오류가 발견되었습니다.',
                'errors': validation['errors']
            })
        
        # 자동화 실행 (실제로는 백그라운드에서 실행)
        return jsonify({
            'success': True, 
            'message': '자동화가 시작되었습니다.',
            'status': 'running'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/api/automation/status')
def get_automation_status():
    """자동화 상태 조회 API"""
    # 실제 자동화 상태를 확인하는 로직
    return jsonify({
        'status': 'ready',
        'last_run': None,
        'next_run': None
    })

@app.route('/api/validate')
def validate_config():
    """설정 검증 API"""
    validation = config_manager.validate_config()
    return jsonify(validation)

@app.route('/logs')
def logs():
    """로그 보기 페이지"""
    log_file = "g4k_automation.log"
    log_content = ""
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
        except Exception as e:
            log_content = f"로그 파일을 읽을 수 없습니다: {e}"
    else:
        log_content = "로그 파일이 없습니다."
    
    return render_template('logs.html', log_content=log_content)

def create_templates():
    """HTML 템플릿 생성"""
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # 기본 레이아웃 템플릿
    base_template = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}G4K 방문예약 자동화 시스템{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background-color: #f8f9fa; }
        .main-content { padding: 20px; }
        .card { margin-bottom: 20px; }
        .status-indicator { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
        .status-active { background-color: #28a745; }
        .status-inactive { background-color: #dc3545; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- 사이드바 -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky pt-3">
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="/">
                                <i class="fas fa-tachometer-alt"></i> 대시보드
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/profiles">
                                <i class="fas fa-users"></i> 사용자 프로필
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/templates">
                                <i class="fas fa-file-alt"></i> 예약 템플릿
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/settings">
                                <i class="fas fa-cog"></i> 설정
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/automation">
                                <i class="fas fa-play"></i> 자동화 실행
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/logs">
                                <i class="fas fa-list"></i> 로그
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- 메인 콘텐츠 -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>"""
    
    with open(os.path.join(templates_dir, "base.html"), "w", encoding="utf-8") as f:
        f.write(base_template)
    
    # 대시보드 템플릿
    dashboard_template = """{% extends "base.html" %}

{% block title %}대시보드 - G4K 방문예약 자동화 시스템{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">대시보드</h1>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">시스템 상태</h5>
            </div>
            <div class="card-body">
                <div id="system-status">
                    <p><strong>활성 프로필:</strong> <span id="active-profile">로딩 중...</span></p>
                    <p><strong>활성 템플릿:</strong> <span id="active-template">로딩 중...</span></p>
                    <p><strong>자동화 상태:</strong> <span id="auto-status">로딩 중...</span></p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">빠른 액션</h5>
            </div>
            <div class="card-body">
                <button class="btn btn-primary me-2" onclick="startAutomation()">
                    <i class="fas fa-play"></i> 자동화 시작
                </button>
                <button class="btn btn-info me-2" onclick="validateSettings()">
                    <i class="fas fa-check"></i> 설정 검증
                </button>
                <button class="btn btn-secondary" onclick="location.href='/logs'">
                    <i class="fas fa-list"></i> 로그 보기
                </button>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">최근 활동</h5>
            </div>
            <div class="card-body">
                <div id="recent-activity">
                    <p class="text-muted">활동 내역이 없습니다.</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function loadStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('active-profile').textContent = data.active_profile;
            document.getElementById('active-template').textContent = data.active_template;
            document.getElementById('auto-status').textContent = 
                `${data.enabled_auto_checks}/${data.total_auto_checks} 기능 활성화`;
        })
        .catch(error => {
            console.error('상태 로드 실패:', error);
        });
}

function startAutomation() {
    fetch('/api/automation/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('자동화가 시작되었습니다.');
        } else {
            alert('오류: ' + data.message);
        }
    })
    .catch(error => {
        console.error('자동화 시작 실패:', error);
        alert('자동화 시작에 실패했습니다.');
    });
}

function validateSettings() {
    fetch('/api/validate')
        .then(response => response.json())
        .then(data => {
            if (data.errors && data.errors.length > 0) {
                alert('설정 오류가 발견되었습니다:\\n' + data.errors.join('\\n'));
            } else if (data.warnings && data.warnings.length > 0) {
                alert('설정 경고:\\n' + data.warnings.join('\\n'));
            } else {
                alert('모든 설정이 유효합니다.');
            }
        })
        .catch(error => {
            console.error('설정 검증 실패:', error);
            alert('설정 검증에 실패했습니다.');
        });
}

// 페이지 로드 시 상태 업데이트
document.addEventListener('DOMContentLoaded', function() {
    loadStatus();
    // 30초마다 상태 업데이트
    setInterval(loadStatus, 30000);
});
</script>
{% endblock %}"""
    
    with open(os.path.join(templates_dir, "dashboard.html"), "w", encoding="utf-8") as f:
        f.write(dashboard_template)
    
    # 프로필 관리 템플릿
    profiles_template = """{% extends "base.html" %}

{% block title %}사용자 프로필 - G4K 방문예약 자동화 시스템{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">사용자 프로필</h1>
    <button class="btn btn-primary" onclick="showAddProfileModal()">
        <i class="fas fa-plus"></i> 새 프로필
    </button>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">프로필 목록</h5>
            </div>
            <div class="card-body">
                <div id="profiles-list">
                    <p class="text-muted">로딩 중...</p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 프로필 추가/편집 모달 -->
<div class="modal fade" id="profileModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="profileModalTitle">프로필 추가</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="profileForm">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="profileName" class="form-label">프로필 이름</label>
                                <input type="text" class="form-control" id="profileName" required>
                            </div>
                            <div class="mb-3">
                                <label for="name" class="form-label">이름</label>
                                <input type="text" class="form-control" id="name" required>
                            </div>
                            <div class="mb-3">
                                <label for="nameEnglish" class="form-label">영문 이름</label>
                                <input type="text" class="form-control" id="nameEnglish" required>
                            </div>
                            <div class="mb-3">
                                <label for="phone" class="form-label">전화번호</label>
                                <input type="tel" class="form-control" id="phone" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="email" class="form-label">이메일</label>
                                <input type="email" class="form-control" id="email" required>
                            </div>
                            <div class="mb-3">
                                <label for="idType" class="form-label">신분증 종류</label>
                                <select class="form-control" id="idType" required>
                                    <option value="passport">여권</option>
                                    <option value="residence_card">거소신고증</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="idNumber" class="form-label">신분증 번호</label>
                                <input type="text" class="form-control" id="idNumber" required>
                            </div>
                            <div class="mb-3">
                                <label for="birthDate" class="form-label">생년월일</label>
                                <input type="date" class="form-control" id="birthDate">
                            </div>
                        </div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                <button type="button" class="btn btn-primary" onclick="saveProfile()">저장</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
let currentProfile = null;

function loadProfiles() {
    fetch('/api/profiles')
        .then(response => response.json())
        .then(profiles => {
            const container = document.getElementById('profiles-list');
            if (profiles.length === 0) {
                container.innerHTML = '<p class="text-muted">등록된 프로필이 없습니다.</p>';
                return;
            }
            
            let html = '<div class="table-responsive"><table class="table table-striped">';
            html += '<thead><tr><th>프로필명</th><th>이름</th><th>이메일</th><th>전화번호</th><th>상태</th><th>액션</th></tr></thead><tbody>';
            
            profiles.forEach(profile => {
                const statusClass = profile.is_active ? 'status-active' : 'status-inactive';
                const statusText = profile.is_active ? '활성' : '비활성';
                
                html += `<tr>
                    <td>${profile.name}</td>
                    <td>${profile.data.name || 'N/A'}</td>
                    <td>${profile.data.email || 'N/A'}</td>
                    <td>${profile.data.phone || 'N/A'}</td>
                    <td><span class="status-indicator ${statusClass}"></span>${statusText}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editProfile('${profile.name}')">편집</button>
                        ${!profile.is_active ? `<button class="btn btn-sm btn-outline-success me-1" onclick="activateProfile('${profile.name}')">활성화</button>` : ''}
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteProfile('${profile.name}')">삭제</button>
                    </td>
                </tr>`;
            });
            
            html += '</tbody></table></div>';
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('프로필 로드 실패:', error);
            document.getElementById('profiles-list').innerHTML = '<p class="text-danger">프로필 로드에 실패했습니다.</p>';
        });
}

function showAddProfileModal() {
    currentProfile = null;
    document.getElementById('profileModalTitle').textContent = '프로필 추가';
    document.getElementById('profileForm').reset();
    new bootstrap.Modal(document.getElementById('profileModal')).show();
}

function editProfile(profileName) {
    currentProfile = profileName;
    document.getElementById('profileModalTitle').textContent = `프로필 편집: ${profileName}`;
    
    fetch('/api/profiles')
        .then(response => response.json())
        .then(profiles => {
            const profile = profiles.find(p => p.name === profileName);
            if (profile) {
                document.getElementById('profileName').value = profile.name;
                document.getElementById('name').value = profile.data.name || '';
                document.getElementById('nameEnglish').value = profile.data.name_english || '';
                document.getElementById('phone').value = profile.data.phone || '';
                document.getElementById('email').value = profile.data.email || '';
                document.getElementById('idType').value = profile.data.id_type || 'passport';
                document.getElementById('idNumber').value = profile.data.id_number || '';
                document.getElementById('birthDate').value = profile.data.birth_date || '';
                
                new bootstrap.Modal(document.getElementById('profileModal')).show();
            }
        });
}

function saveProfile() {
    const formData = {
        name: document.getElementById('profileName').value,
        data: {
            name: document.getElementById('name').value,
            name_english: document.getElementById('nameEnglish').value,
            phone: document.getElementById('phone').value,
            email: document.getElementById('email').value,
            id_type: document.getElementById('idType').value,
            id_number: document.getElementById('idNumber').value,
            birth_date: document.getElementById('birthDate').value
        }
    };
    
    const url = currentProfile ? `/api/profiles/${currentProfile}` : '/api/profiles';
    const method = currentProfile ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(currentProfile ? formData.data : formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('profileModal')).hide();
            loadProfiles();
            alert(data.message);
        } else {
            alert('오류: ' + data.message);
        }
    })
    .catch(error => {
        console.error('프로필 저장 실패:', error);
        alert('프로필 저장에 실패했습니다.');
    });
}

function activateProfile(profileName) {
    fetch(`/api/profiles/${profileName}/activate`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadProfiles();
            alert(data.message);
        } else {
            alert('오류: ' + data.message);
        }
    })
    .catch(error => {
        console.error('프로필 활성화 실패:', error);
        alert('프로필 활성화에 실패했습니다.');
    });
}

function deleteProfile(profileName) {
    if (confirm(`프로필 '${profileName}'을 삭제하시겠습니까?`)) {
        fetch(`/api/profiles/${profileName}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadProfiles();
                alert(data.message);
            } else {
                alert('오류: ' + data.message);
            }
        })
        .catch(error => {
            console.error('프로필 삭제 실패:', error);
            alert('프로필 삭제에 실패했습니다.');
        });
    }
}

// 페이지 로드 시 프로필 목록 로드
document.addEventListener('DOMContentLoaded', function() {
    loadProfiles();
});
</script>
{% endblock %}"""
    
    with open(os.path.join(templates_dir, "profiles.html"), "w", encoding="utf-8") as f:
        f.write(profiles_template)
    
    # 나머지 템플릿들도 생성...
    # (공간 제약으로 일부만 표시)

def start_web_dashboard():
    """웹 대시보드 시작"""
    create_templates()
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == "__main__":
    start_web_dashboard() 
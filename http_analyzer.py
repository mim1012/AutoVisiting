#!/usr/bin/env python3
"""
G4K HTTP 요청 분석 도구
브라우저의 네트워크 트래픽을 분석하여 API 엔드포인트와 파라미터 구조 파악
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs, unquote
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HttpRequestAnalyzer:
    """HTTP 요청 분석 클래스"""
    
    def __init__(self):
        self.endpoints = {}
        self.form_structures = {}
        self.ajax_patterns = {}
        
    def analyze_har_file(self, har_file_path: str) -> Dict[str, Any]:
        """HAR 파일 분석 (브라우저 개발자 도구에서 내보낸 네트워크 로그)"""
        try:
            with open(har_file_path, 'r', encoding='utf-8') as f:
                har_data = json.load(f)
            
            entries = har_data.get('log', {}).get('entries', [])
            analysis_result = {
                'endpoints': [],
                'forms': [],
                'ajax_requests': [],
                'cookies': [],
                'headers': []
            }
            
            for entry in entries:
                request = entry.get('request', {})
                response = entry.get('response', {})
                
                url = request.get('url', '')
                method = request.get('method', '')
                
                # G4K 관련 요청만 분석
                if 'g4k.go.kr' in url:
                    endpoint_info = self._analyze_endpoint(request, response)
                    analysis_result['endpoints'].append(endpoint_info)
                    
                    # AJAX 요청 식별
                    if self._is_ajax_request(request):
                        ajax_info = self._analyze_ajax_request(request, response)
                        analysis_result['ajax_requests'].append(ajax_info)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"HAR 파일 분석 실패: {e}")
            return {}
    
    def _analyze_endpoint(self, request: Dict, response: Dict) -> Dict[str, Any]:
        """개별 엔드포인트 분석"""
        url = request.get('url', '')
        method = request.get('method', '')
        
        parsed_url = urlparse(url)
        
        endpoint_info = {
            'url': url,
            'method': method,
            'path': parsed_url.path,
            'query_params': parse_qs(parsed_url.query),
            'headers': {},
            'post_data': {},
            'response_status': response.get('status', 0),
            'response_type': '',
            'csrf_token_required': False
        }
        
        # 헤더 분석
        for header in request.get('headers', []):
            name = header.get('name', '').lower()
            value = header.get('value', '')
            endpoint_info['headers'][name] = value
            
            # CSRF 토큰 확인
            if 'csrf' in name or 'x-csrf-token' in name:
                endpoint_info['csrf_token_required'] = True
        
        # POST 데이터 분석
        post_data = request.get('postData', {})
        if post_data:
            content_type = post_data.get('mimeType', '')
            text = post_data.get('text', '')
            
            if 'application/x-www-form-urlencoded' in content_type:
                endpoint_info['post_data'] = parse_qs(text)
            elif 'application/json' in content_type:
                try:
                    endpoint_info['post_data'] = json.loads(text)
                except:
                    endpoint_info['post_data'] = {'raw': text}
        
        # 응답 타입 분석
        content_type = response.get('content', {}).get('mimeType', '')
        if 'json' in content_type:
            endpoint_info['response_type'] = 'json'
        elif 'html' in content_type:
            endpoint_info['response_type'] = 'html'
        
        return endpoint_info
    
    def _is_ajax_request(self, request: Dict) -> bool:
        """AJAX 요청 여부 확인"""
        headers = {h.get('name', '').lower(): h.get('value', '') 
                  for h in request.get('headers', [])}
        
        return (headers.get('x-requested-with') == 'XMLHttpRequest' or
                'application/json' in headers.get('accept', '') or
                'application/json' in headers.get('content-type', ''))
    
    def _analyze_ajax_request(self, request: Dict, response: Dict) -> Dict[str, Any]:
        """AJAX 요청 상세 분석"""
        ajax_info = self._analyze_endpoint(request, response)
        
        # AJAX 특화 분석
        ajax_info['is_ajax'] = True
        
        # 응답 데이터 구조 분석
        response_content = response.get('content', {}).get('text', '')
        if response_content:
            try:
                json_data = json.loads(response_content)
                ajax_info['response_structure'] = self._analyze_json_structure(json_data)
            except:
                pass
        
        return ajax_info
    
    def _analyze_json_structure(self, json_data: Any, depth: int = 0) -> Dict[str, Any]:
        """JSON 데이터 구조 분석"""
        if depth > 3:  # 깊이 제한
            return {'type': 'deep_object'}
        
        if isinstance(json_data, dict):
            structure = {'type': 'object', 'fields': {}}
            for key, value in json_data.items():
                structure['fields'][key] = self._analyze_json_structure(value, depth + 1)
            return structure
        elif isinstance(json_data, list):
            if json_data:
                return {
                    'type': 'array',
                    'item_type': self._analyze_json_structure(json_data[0], depth + 1),
                    'length': len(json_data)
                }
            else:
                return {'type': 'empty_array'}
        else:
            return {'type': type(json_data).__name__, 'sample_value': str(json_data)[:100]}
    
    def analyze_page_forms(self, html_content: str, page_url: str) -> List[Dict[str, Any]]:
        """페이지의 폼 구조 분석"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            forms = []
            
            for form in soup.find_all('form'):
                form_info = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET').upper(),
                    'fields': [],
                    'hidden_fields': [],
                    'csrf_token': None,
                    'page_url': page_url
                }
                
                # 절대 URL로 변환
                if form_info['action']:
                    if form_info['action'].startswith('/'):
                        form_info['action'] = f"https://www.g4k.go.kr{form_info['action']}"
                    elif not form_info['action'].startswith('http'):
                        base_url = '/'.join(page_url.split('/')[:-1])
                        form_info['action'] = f"{base_url}/{form_info['action']}"
                
                # 입력 필드 분석
                for input_elem in form.find_all(['input', 'select', 'textarea']):
                    field_info = {
                        'name': input_elem.get('name', ''),
                        'type': input_elem.get('type', 'text'),
                        'required': input_elem.has_attr('required'),
                        'value': input_elem.get('value', ''),
                        'placeholder': input_elem.get('placeholder', ''),
                        'options': []
                    }
                    
                    # select 옵션 분석
                    if input_elem.name == 'select':
                        for option in input_elem.find_all('option'):
                            field_info['options'].append({
                                'value': option.get('value', ''),
                                'text': option.get_text(strip=True)
                            })
                    
                    if field_info['type'] == 'hidden':
                        form_info['hidden_fields'].append(field_info)
                        
                        # CSRF 토큰 식별
                        if any(token_name in field_info['name'].lower() 
                               for token_name in ['csrf', 'token', '_token']):
                            form_info['csrf_token'] = field_info['value']
                    else:
                        form_info['fields'].append(field_info)
                
                forms.append(form_info)
            
            return forms
            
        except Exception as e:
            logger.error(f"폼 분석 실패: {e}")
            return []
    
    def generate_request_template(self, endpoint_info: Dict[str, Any]) -> str:
        """분석 결과를 바탕으로 Python requests 코드 템플릿 생성"""
        template = f"""
# {endpoint_info['method']} {endpoint_info['url']}
def make_request_{endpoint_info['path'].replace('/', '_').replace('.', '_')}(session, **kwargs):
    url = "{endpoint_info['url']}"
    
    headers = {{"""
        
        for name, value in endpoint_info['headers'].items():
            if name not in ['cookie', 'content-length']:
                template += f'\n        "{name}": "{value}",'
        
        template += "\n    }\n"
        
        if endpoint_info['method'] == 'POST':
            template += "\n    data = {\n"
            for key, values in endpoint_info['post_data'].items():
                if isinstance(values, list) and values:
                    template += f'        "{key}": "{values[0]}",\n'
                else:
                    template += f'        "{key}": kwargs.get("{key}", ""),\n'
            template += "    }\n"
            
            template += f'\n    response = session.{endpoint_info["method"].lower()}(url, data=data, headers=headers)'
        else:
            template += f'\n    response = session.{endpoint_info["method"].lower()}(url, headers=headers)'
        
        template += """
    
    if response.status_code == 200:
        return response
    else:
        raise Exception(f"Request failed: {response.status_code}")
"""
        
        return template
    
    def save_analysis_report(self, analysis_result: Dict[str, Any], filename: str):
        """분석 결과를 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            logger.info(f"분석 결과 저장 완료: {filename}")
        except Exception as e:
            logger.error(f"분석 결과 저장 실패: {e}")


class G4KApiMapper:
    """G4K API 엔드포인트 매핑 클래스"""
    
    def __init__(self):
        self.api_map = {
            'login': {
                'url': '/biz/login/loginProc.do',
                'method': 'POST',
                'description': '로그인 처리'
            },
            'main': {
                'url': '/biz/main/main.do',
                'method': 'GET',
                'description': '메인 페이지'
            },
            'visit_gwanghwamun': {
                'url': '/biz/visit/gwanghwamun/main.do',
                'method': 'GET',
                'description': '광화문 센터 방문예약'
            },
            'visit_embassy': {
                'url': '/biz/visit/embassy/main.do',
                'method': 'GET',
                'description': '재외공관 방문예약'
            },
            'terms_agree': {
                'url': '/biz/visit/gwanghwamun/terms.do',
                'method': 'POST',
                'description': '주의사항 동의'
            },
            'select_service': {
                'url': '/biz/visit/gwanghwamun/selectService.do',
                'method': 'POST',
                'description': '서비스 선택'
            },
            'available_dates': {
                'url': '/api/visit/available-dates',
                'method': 'GET',
                'description': '가용 날짜 조회 (AJAX)'
            },
            'available_times': {
                'url': '/api/visit/available-times',
                'method': 'GET',
                'description': '가용 시간 조회 (AJAX)'
            },
            'select_datetime': {
                'url': '/biz/visit/gwanghwamun/selectDateTime.do',
                'method': 'POST',
                'description': '날짜/시간 선택'
            },
            'applicant_info': {
                'url': '/biz/visit/gwanghwamun/applicantInfo.do',
                'method': 'POST',
                'description': '신청자 정보 입력'
            },
            'submit': {
                'url': '/biz/visit/gwanghwamun/submit.do',
                'method': 'POST',
                'description': '최종 예약 제출'
            }
        }
    
    def get_endpoint(self, action: str) -> Optional[Dict[str, str]]:
        """액션에 해당하는 엔드포인트 정보 반환"""
        return self.api_map.get(action)
    
    def get_full_url(self, action: str, base_url: str = "https://www.g4k.go.kr") -> Optional[str]:
        """전체 URL 반환"""
        endpoint = self.get_endpoint(action)
        if endpoint:
            return f"{base_url}{endpoint['url']}"
        return None


def main():
    """사용 예시"""
    analyzer = HttpRequestAnalyzer()
    
    # HAR 파일 분석 예시
    # har_result = analyzer.analyze_har_file('g4k_network.har')
    # analyzer.save_analysis_report(har_result, 'g4k_api_analysis.json')
    
    # 페이지 폼 분석 예시
    html_content = """
    <form action="/biz/visit/gwanghwamun/terms.do" method="POST">
        <input type="hidden" name="_token" value="abc123">
        <input type="checkbox" name="agree" value="Y" required>
        <button type="submit">동의</button>
    </form>
    """
    
    forms = analyzer.analyze_page_forms(html_content, "https://www.g4k.go.kr/test")
    print("폼 분석 결과:")
    print(json.dumps(forms, indent=2, ensure_ascii=False))
    
    # API 매퍼 사용 예시
    api_mapper = G4KApiMapper()
    login_url = api_mapper.get_full_url('login')
    print(f"로그인 URL: {login_url}")


if __name__ == "__main__":
    main()


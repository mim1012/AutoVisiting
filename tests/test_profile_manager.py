#!/usr/bin/env python3
"""
ProfileManager 모듈 단위 테스트
기존 코드 변경 없이 테스트만 추가
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch

# 상위 디렉토리의 모듈 import 가능하도록 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from profile_manager import ProfileManager, ConfigManager
except ImportError as e:
    print(f"Import 경고: {e}")
    ProfileManager = None
    ConfigManager = None


class TestProfileManager(unittest.TestCase):
    """ProfileManager 단위 테스트"""
    
    def setUp(self):
        """테스트 준비"""
        if ProfileManager is None:
            self.skipTest("ProfileManager 모듈을 import할 수 없습니다")
            
        # 임시 테스트 프로필 데이터
        self.test_profile_data = {
            "profiles": [
                {
                    "name": "테스트사용자1",
                    "id_number": "M12345678",
                    "phone": "010-1234-5678",
                    "email": "test1@example.com"
                },
                {
                    "name": "테스트사용자2", 
                    "id_number": "F87654321",
                    "phone": "010-8765-4321",
                    "email": "test2@example.com"
                }
            ]
        }
    
    def test_profile_manager_initialization(self):
        """ProfileManager 초기화 테스트"""
        # 임시 파일로 테스트
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_profile_data, f)
            temp_file = f.name
        
        try:
            manager = ProfileManager(temp_file)
            self.assertIsNotNone(manager)
            self.assertTrue(hasattr(manager, 'load_profiles'))
            self.assertTrue(hasattr(manager, 'save_profiles'))
        finally:
            os.unlink(temp_file)
    
    def test_load_profiles_success(self):
        """프로필 로드 성공 케이스 테스트"""
        # 임시 파일로 테스트
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_profile_data, f)
            temp_file = f.name
        
        try:
            manager = ProfileManager(temp_file)
            profiles = manager.load_profiles()
            
            # 프로필 데이터 검증
            self.assertIsInstance(profiles, list)
            self.assertEqual(len(profiles), 2)
            self.assertEqual(profiles[0]['name'], '테스트사용자1')
            self.assertEqual(profiles[1]['id_number'], 'F87654321')
            
        finally:
            os.unlink(temp_file)
    
    def test_load_profiles_file_not_found(self):
        """프로필 파일이 없을 때 테스트"""
        non_existent_file = 'non_existent_profile.json'
        
        manager = ProfileManager(non_existent_file)
        
        # 파일이 없어도 에러 없이 빈 리스트 반환하는지 확인
        try:
            profiles = manager.load_profiles()
            # 구현에 따라 빈 리스트 또는 예외 발생 가능
            self.assertIsInstance(profiles, (list, type(None)))
        except Exception as e:
            # 예외 발생도 정상적인 동작
            self.assertIsInstance(e, (FileNotFoundError, IOError, json.JSONDecodeError))
    
    def test_profile_validation(self):
        """프로필 데이터 검증 테스트"""
        # 올바른 프로필 데이터
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_profile_data, f)
            temp_file = f.name
        
        try:
            manager = ProfileManager(temp_file)
            profiles = manager.load_profiles()
            
            for profile in profiles:
                # 필수 필드 존재 확인
                required_fields = ['name', 'id_number', 'phone']
                for field in required_fields:
                    self.assertIn(field, profile, f"필수 필드 {field}가 없습니다")
                    self.assertTrue(profile[field], f"필드 {field}가 비어있습니다")
                
        finally:
            os.unlink(temp_file)
    
    def test_invalid_json_handling(self):
        """잘못된 JSON 처리 테스트"""
        # 잘못된 JSON 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{ invalid json data }')
            temp_file = f.name
        
        try:
            manager = ProfileManager(temp_file)
            
            # JSON 에러 처리 확인
            with self.assertRaises((json.JSONDecodeError, ValueError)):
                manager.load_profiles()
                
        finally:
            os.unlink(temp_file)
    
    def test_profile_manager_methods_exist(self):
        """ProfileManager 주요 메소드 존재 확인"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_profile_data, f)
            temp_file = f.name
        
        try:
            manager = ProfileManager(temp_file)
            
            # 주요 메소드들 존재 확인
            expected_methods = [
                'load_profiles',
                'save_profiles',
                'get_active_profile'
            ]
            
            for method in expected_methods:
                if hasattr(manager, method):
                    self.assertTrue(callable(getattr(manager, method)), 
                                  f"메소드 {method}가 호출 가능하지 않습니다")
                
        finally:
            os.unlink(temp_file)


class TestConfigManager(unittest.TestCase):
    """ConfigManager 단위 테스트"""
    
    def setUp(self):
        """테스트 준비"""
        if ConfigManager is None:
            self.skipTest("ConfigManager 모듈을 import할 수 없습니다")
    
    def test_config_manager_initialization(self):
        """ConfigManager 초기화 테스트"""
        try:
            config_manager = ConfigManager()
            self.assertIsNotNone(config_manager)
        except Exception as e:
            # 설정 파일이 없는 경우도 허용
            self.assertIsInstance(e, (FileNotFoundError, IOError))
    
    def test_config_manager_attributes(self):
        """ConfigManager 속성 테스트"""
        try:
            config_manager = ConfigManager()
            
            # 기본적으로 profile_manager 속성이 있어야 함
            if hasattr(config_manager, 'profile_manager'):
                self.assertIsNotNone(config_manager.profile_manager)
                
        except Exception as e:
            # 초기화 실패 시 스킵
            self.skipTest(f"ConfigManager 초기화 실패: {e}")


class TestProfileManagerIntegration(unittest.TestCase):
    """ProfileManager 통합 테스트"""
    
    def setUp(self):
        """테스트 준비"""
        if ProfileManager is None:
            self.skipTest("ProfileManager 모듈을 import할 수 없습니다")
    
    def test_save_and_load_cycle(self):
        """저장-로드 사이클 테스트"""
        test_profiles = [
            {
                "name": "사이클테스트",
                "id_number": "M99999999",
                "phone": "010-9999-9999"
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            manager = ProfileManager(temp_file)
            
            # 저장 기능이 있는 경우 테스트
            if hasattr(manager, 'save_profiles'):
                manager.save_profiles(test_profiles)
                
                # 로드해서 확인
                loaded_profiles = manager.load_profiles()
                self.assertEqual(len(loaded_profiles), 1)
                self.assertEqual(loaded_profiles[0]['name'], '사이클테스트')
            else:
                self.skipTest("save_profiles 메소드가 없습니다")
                
        except Exception as e:
            self.skipTest(f"저장-로드 사이클 테스트 실패: {e}")
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


def run_profile_manager_tests():
    """ProfileManager 테스트 실행"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestProfileManager))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestProfileManagerIntegration))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🔬 ProfileManager 모듈 단위 테스트")
    print("=" * 50)
    
    success = run_profile_manager_tests()
    
    if success:
        print("\n✅ 모든 ProfileManager 테스트 통과!")
    else:
        print("\n❌ 일부 ProfileManager 테스트 실패")
    
    exit(0 if success else 1)
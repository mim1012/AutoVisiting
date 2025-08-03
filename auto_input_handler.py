#!/usr/bin/env python3
"""
G4K 방문예약 자동화 시스템 - 자동 입력 처리 모듈
약관 동의, 센터/공관 선택, 민원/방문일시 선택, 신청자 정보 입력을 자동화
"""

import time
import logging
from typing import Dict, List, Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from profile_manager import ConfigManager

logger = logging.getLogger(__name__)


class AutoInputHandler:
    """자동 입력 처리 클래스"""
    
    def __init__(self, driver, config_manager: ConfigManager):
        self.driver = driver
        self.config_manager = config_manager
        self.wait = WebDriverWait(driver, 10)
        
    def handle_terms_agreement(self) -> bool:
        """약관 동의 자동 처리"""
        try:
            logger.info("약관 동의 자동 처리 시작")
            
            # 자동 체크 설정 확인
            auto_check_settings = self.config_manager.auto_check_manager.settings.get('auto_check_settings', {})
            terms_settings = auto_check_settings.get('terms_agreement', {})
            
            if not terms_settings.get('enabled', False):
                logger.info("약관 동의 자동 체크가 비활성화되어 있습니다")
                return True
            
            # 모든 체크박스 찾기
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            
            if not checkboxes:
                logger.warning("체크박스를 찾을 수 없습니다")
                return False
            
            # 자동 체크 처리
            for checkbox in checkboxes:
                try:
                    if not checkbox.is_selected():
                        # 체크박스가 화면에 보이도록 스크롤
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                        time.sleep(0.5)
                        
                        # 체크박스 클릭
                        checkbox.click()
                        logger.info(f"체크박스 선택: {checkbox.get_attribute('name') or checkbox.get_attribute('id')}")
                        time.sleep(0.3)
                except Exception as e:
                    logger.warning(f"체크박스 선택 실패: {e}")
                    continue
            
            # 신청하기 버튼 클릭
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .btn-submit"))
            )
            submit_button.click()
            logger.info("약관 동의 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"약관 동의 처리 실패: {e}")
            return False
    
    def handle_center_selection(self) -> bool:
        """센터/공관 선택 자동 처리"""
        try:
            logger.info("센터/공관 선택 자동 처리 시작")
            
            auto_check_settings = self.config_manager.auto_check_manager.settings.get('auto_check_settings', {})
            center_settings = auto_check_settings.get('center_selection', {})
            
            if not center_settings.get('enabled', False):
                logger.info("센터 선택 자동 처리가 비활성화되어 있습니다")
                return True
            
            # 활성 템플릿에서 센터 타입 가져오기
            template = self.config_manager.template_manager.get_active_template()
            if not template:
                logger.error("활성 템플릿이 설정되지 않았습니다")
                return False
            
            center_type = template.get('center_type', 'gwanghwamun')
            preferred_centers = center_settings.get('preferred_centers', [center_type])
            
            # 센터 선택 처리
            for center in preferred_centers:
                try:
                    # 라디오 버튼 또는 링크로 센터 선택
                    center_selectors = [
                        f"input[value='{center}']",
                        f"input[name*='{center}']",
                        f"a[href*='{center}']",
                        f".{center}-center",
                        f"#{center}_center"
                    ]
                    
                    center_element = None
                    for selector in center_selectors:
                        try:
                            center_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except NoSuchElementException:
                            continue
                    
                    if center_element:
                        center_element.click()
                        logger.info(f"센터 선택 완료: {center}")
                        time.sleep(1)
                        return True
                        
                except Exception as e:
                    logger.warning(f"센터 선택 실패 ({center}): {e}")
                    continue
            
            logger.error("모든 센터 선택 시도 실패")
            return False
            
        except Exception as e:
            logger.error(f"센터 선택 처리 실패: {e}")
            return False
    
    def handle_service_selection(self) -> bool:
        """서비스 선택 자동 처리"""
        try:
            logger.info("서비스 선택 자동 처리 시작")
            
            auto_check_settings = self.config_manager.auto_check_manager.settings.get('auto_check_settings', {})
            service_settings = auto_check_settings.get('service_selection', {})
            
            if not service_settings.get('enabled', False):
                logger.info("서비스 선택 자동 처리가 비활성화되어 있습니다")
                return True
            
            # 활성 템플릿에서 서비스 정보 가져오기
            template = self.config_manager.template_manager.get_active_template()
            if not template:
                logger.error("활성 템플릿이 설정되지 않았습니다")
                return False
            
            service_type = template.get('service_type', 'drivers_license')
            service_detail = template.get('service_detail', 'renewal')
            service_code = template.get('service_code', '')
            
            # 서비스 선택 처리
            service_selectors = [
                f"input[value='{service_code}']",
                f"input[name*='{service_type}']",
                f"a[href*='{service_type}']",
                f".{service_type}-service",
                f"#{service_type}_service"
            ]
            
            service_element = None
            for selector in service_selectors:
                try:
                    service_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if service_element:
                service_element.click()
                logger.info(f"서비스 선택 완료: {service_type} - {service_detail}")
                time.sleep(1)
                return True
            else:
                logger.error(f"서비스 요소를 찾을 수 없습니다: {service_type}")
                return False
                
        except Exception as e:
            logger.error(f"서비스 선택 처리 실패: {e}")
            return False
    
    def handle_datetime_selection(self) -> bool:
        """날짜/시간 선택 자동 처리"""
        try:
            logger.info("날짜/시간 선택 자동 처리 시작")
            
            auto_check_settings = self.config_manager.auto_check_manager.settings.get('auto_check_settings', {})
            datetime_settings = auto_check_settings.get('date_time_selection', {})
            
            if not datetime_settings.get('enabled', False):
                logger.info("날짜/시간 선택 자동 처리가 비활성화되어 있습니다")
                return True
            
            # 활성 템플릿에서 날짜/시간 정보 가져오기
            template = self.config_manager.template_manager.get_active_template()
            if not template:
                logger.error("활성 템플릿이 설정되지 않았습니다")
                return False
            
            preferred_dates = template.get('preferred_dates', [])
            preferred_times = template.get('preferred_times', [])
            
            # 날짜 선택 처리
            date_selected = False
            for date in preferred_dates:
                try:
                    # 날짜 선택자들
                    date_selectors = [
                        f"input[value='{date}']",
                        f"a[data-date='{date}']",
                        f".date-{date}",
                        f"td[data-date='{date}']"
                    ]
                    
                    date_element = None
                    for selector in date_selectors:
                        try:
                            date_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except NoSuchElementException:
                            continue
                    
                    if date_element:
                        date_element.click()
                        logger.info(f"날짜 선택 완료: {date}")
                        date_selected = True
                        time.sleep(1)
                        break
                        
                except Exception as e:
                    logger.warning(f"날짜 선택 실패 ({date}): {e}")
                    continue
            
            if not date_selected:
                logger.error("모든 날짜 선택 시도 실패")
                return False
            
            # 시간 선택 처리
            time_selected = False
            for time_slot in preferred_times:
                try:
                    # 시간 선택자들
                    time_selectors = [
                        f"input[value='{time_slot}']",
                        f"a[data-time='{time_slot}']",
                        f".time-{time_slot.replace(':', '-')}",
                        f"td[data-time='{time_slot}']"
                    ]
                    
                    time_element = None
                    for selector in time_selectors:
                        try:
                            time_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except NoSuchElementException:
                            continue
                    
                    if time_element:
                        time_element.click()
                        logger.info(f"시간 선택 완료: {time_slot}")
                        time_selected = True
                        time.sleep(1)
                        break
                        
                except Exception as e:
                    logger.warning(f"시간 선택 실패 ({time_slot}): {e}")
                    continue
            
            if not time_selected:
                logger.error("모든 시간 선택 시도 실패")
                return False
            
            logger.info("날짜/시간 선택 완료")
            return True
            
        except Exception as e:
            logger.error(f"날짜/시간 선택 처리 실패: {e}")
            return False
    
    def handle_applicant_info(self) -> bool:
        """신청자 정보 자동 입력"""
        try:
            logger.info("신청자 정보 자동 입력 시작")
            
            auto_check_settings = self.config_manager.auto_check_manager.settings.get('auto_check_settings', {})
            applicant_settings = auto_check_settings.get('applicant_info', {})
            
            if not applicant_settings.get('enabled', False):
                logger.info("신청자 정보 자동 입력이 비활성화되어 있습니다")
                return True
            
            # 활성 프로필에서 사용자 정보 가져오기
            profile = self.config_manager.profile_manager.get_active_profile()
            if not profile:
                logger.error("활성 프로필이 설정되지 않았습니다")
                return False
            
            # 필수 필드 입력
            required_fields = applicant_settings.get('required_fields', [])
            for field in required_fields:
                try:
                    value = profile.get(field, '')
                    if not value:
                        logger.warning(f"필수 필드 값이 없습니다: {field}")
                        continue
                    
                    # 필드 선택자들
                    field_selectors = [
                        f"input[name='{field}']",
                        f"input[id='{field}']",
                        f"input[placeholder*='{field}']",
                        f"textarea[name='{field}']",
                        f"select[name='{field}']"
                    ]
                    
                    field_element = None
                    for selector in field_selectors:
                        try:
                            field_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except NoSuchElementException:
                            continue
                    
                    if field_element:
                        # 기존 값 지우기
                        field_element.clear()
                        time.sleep(0.2)
                        
                        # 새 값 입력
                        field_element.send_keys(str(value))
                        logger.info(f"필드 입력 완료: {field} = {value}")
                        time.sleep(0.3)
                    else:
                        logger.warning(f"필드 요소를 찾을 수 없습니다: {field}")
                        
                except Exception as e:
                    logger.warning(f"필드 입력 실패 ({field}): {e}")
                    continue
            
            # 선택적 필드 입력
            optional_fields = applicant_settings.get('optional_fields', [])
            for field in optional_fields:
                try:
                    value = profile.get(field, '')
                    if not value:
                        continue
                    
                    # 필드 선택자들
                    field_selectors = [
                        f"input[name='{field}']",
                        f"input[id='{field}']",
                        f"input[placeholder*='{field}']",
                        f"textarea[name='{field}']",
                        f"select[name='{field}']"
                    ]
                    
                    field_element = None
                    for selector in field_selectors:
                        try:
                            field_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except NoSuchElementException:
                            continue
                    
                    if field_element:
                        # 기존 값 지우기
                        field_element.clear()
                        time.sleep(0.2)
                        
                        # 새 값 입력
                        field_element.send_keys(str(value))
                        logger.info(f"선택적 필드 입력 완료: {field} = {value}")
                        time.sleep(0.3)
                        
                except Exception as e:
                    logger.warning(f"선택적 필드 입력 실패 ({field}): {e}")
                    continue
            
            logger.info("신청자 정보 입력 완료")
            return True
            
        except Exception as e:
            logger.error(f"신청자 정보 입력 처리 실패: {e}")
            return False
    
    def handle_confirmation(self) -> bool:
        """최종 확인 처리"""
        try:
            logger.info("최종 확인 처리 시작")
            
            auto_check_settings = self.config_manager.auto_check_manager.settings.get('auto_check_settings', {})
            confirmation_settings = auto_check_settings.get('confirmation', {})
            
            # 요약 정보 표시
            if confirmation_settings.get('show_summary', False):
                self._show_reservation_summary()
            
            # 사용자 확인 필요 여부
            if confirmation_settings.get('require_user_confirmation', True):
                logger.info("사용자 확인이 필요합니다. 수동으로 확인해주세요.")
                return True
            
            # 자동 확인 처리
            if confirmation_settings.get('auto_confirm', False):
                # 확인 버튼 클릭
                confirm_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    ".btn-confirm",
                    ".btn-submit",
                    "#confirmButton",
                    "#submitButton"
                ]
                
                confirm_button = None
                for selector in confirm_selectors:
                    try:
                        confirm_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if confirm_button:
                    confirm_button.click()
                    logger.info("자동 확인 완료")
                    return True
                else:
                    logger.error("확인 버튼을 찾을 수 없습니다")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"최종 확인 처리 실패: {e}")
            return False
    
    def _show_reservation_summary(self):
        """예약 요약 정보 표시"""
        try:
            profile = self.config_manager.profile_manager.get_active_profile()
            template = self.config_manager.template_manager.get_active_template()
            
            if profile and template:
                logger.info("=== 예약 요약 정보 ===")
                logger.info(f"신청자: {profile.get('name', 'N/A')}")
                logger.info(f"서비스: {template.get('name', 'N/A')}")
                logger.info(f"센터: {template.get('center_type', 'N/A')}")
                logger.info(f"희망 날짜: {', '.join(template.get('preferred_dates', []))}")
                logger.info(f"희망 시간: {', '.join(template.get('preferred_times', []))}")
                logger.info("=====================")
        except Exception as e:
            logger.warning(f"요약 정보 표시 실패: {e}")
    
    def execute_full_auto_input(self) -> bool:
        """전체 자동 입력 프로세스 실행"""
        try:
            logger.info("전체 자동 입력 프로세스 시작")
            
            # 1. 약관 동의
            if not self.handle_terms_agreement():
                logger.error("약관 동의 처리 실패")
                return False
            
            # 2. 센터/공관 선택
            if not self.handle_center_selection():
                logger.error("센터/공관 선택 처리 실패")
                return False
            
            # 3. 서비스 선택
            if not self.handle_service_selection():
                logger.error("서비스 선택 처리 실패")
                return False
            
            # 4. 날짜/시간 선택
            if not self.handle_datetime_selection():
                logger.error("날짜/시간 선택 처리 실패")
                return False
            
            # 5. 신청자 정보 입력
            if not self.handle_applicant_info():
                logger.error("신청자 정보 입력 처리 실패")
                return False
            
            # 6. 최종 확인
            if not self.handle_confirmation():
                logger.error("최종 확인 처리 실패")
                return False
            
            logger.info("전체 자동 입력 프로세스 완료")
            return True
            
        except Exception as e:
            logger.error(f"전체 자동 입력 프로세스 실패: {e}")
            return False


def main():
    """테스트 함수"""
    config_manager = ConfigManager()
    
    # 설정 검증
    validation = config_manager.validate_config()
    if validation['errors']:
        print("설정 오류:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    if validation['warnings']:
        print("설정 경고:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    print("자동 입력 핸들러 준비 완료")


if __name__ == "__main__":
    main() 
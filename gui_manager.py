#!/usr/bin/env python3
"""
G4K 방문예약 자동화 시스템 - GUI 관리 도구
비개발자를 위한 사용자 친화적인 데스크톱 인터페이스
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import webbrowser
from datetime import datetime
from profile_manager import ConfigManager, ProfileManager, ReservationTemplateManager, AutoCheckManager

class G4KGuiManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("G4K 방문예약 자동화 시스템")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        self.config_manager = ConfigManager()
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 타이틀
        title_label = ttk.Label(main_frame, text="G4K 방문예약 자동화 시스템", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 노트북 (탭) 생성
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 탭 생성
        self.create_dashboard_tab(notebook)
        self.create_profile_tab(notebook)
        self.create_template_tab(notebook)
        self.create_settings_tab(notebook)
        self.create_automation_tab(notebook)
        
        # 상태바
        self.status_var = tk.StringVar()
        self.status_var.set("준비됨")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def create_dashboard_tab(self, notebook):
        """대시보드 탭 생성"""
        dashboard_frame = ttk.Frame(notebook)
        notebook.add(dashboard_frame, text="대시보드")
        
        # 현재 설정 요약
        summary_frame = ttk.LabelFrame(dashboard_frame, text="현재 설정 요약", padding="10")
        summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 활성 프로필
        ttk.Label(summary_frame, text="활성 프로필:").grid(row=0, column=0, sticky=tk.W)
        self.active_profile_var = tk.StringVar()
        ttk.Label(summary_frame, textvariable=self.active_profile_var, font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 활성 템플릿
        ttk.Label(summary_frame, text="활성 템플릿:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.active_template_var = tk.StringVar()
        ttk.Label(summary_frame, textvariable=self.active_template_var, font=('Arial', 10, 'bold')).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # 자동화 상태
        ttk.Label(summary_frame, text="자동화 상태:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.auto_status_var = tk.StringVar()
        ttk.Label(summary_frame, textvariable=self.auto_status_var, font=('Arial', 10, 'bold')).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # 빠른 액션 버튼들
        actions_frame = ttk.LabelFrame(dashboard_frame, text="빠른 액션", padding="10")
        actions_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        ttk.Button(actions_frame, text="자동화 시작", command=self.start_automation).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(actions_frame, text="설정 검증", command=self.validate_settings).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(actions_frame, text="로그 보기", command=self.view_logs).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(actions_frame, text="웹 대시보드 열기", command=self.open_web_dashboard).grid(row=0, column=3, padx=5, pady=5)
        
        # 최근 활동
        activity_frame = ttk.LabelFrame(dashboard_frame, text="최근 활동", padding="10")
        activity_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.activity_text = tk.Text(activity_frame, height=8, width=60)
        self.activity_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=self.activity_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.activity_text.configure(yscrollcommand=scrollbar.set)
        
    def create_profile_tab(self, notebook):
        """프로필 관리 탭 생성"""
        profile_frame = ttk.Frame(notebook)
        notebook.add(profile_frame, text="사용자 프로필")
        
        # 프로필 목록
        list_frame = ttk.LabelFrame(profile_frame, text="프로필 목록", padding="10")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 프로필 리스트박스
        self.profile_listbox = tk.Listbox(list_frame, height=10, width=30)
        self.profile_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        self.profile_listbox.bind('<<ListboxSelect>>', self.on_profile_select)
        
        # 프로필 버튼들
        profile_buttons_frame = ttk.Frame(list_frame)
        profile_buttons_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        ttk.Button(profile_buttons_frame, text="새 프로필", command=self.add_profile).grid(row=0, column=0, pady=2)
        ttk.Button(profile_buttons_frame, text="편집", command=self.edit_profile).grid(row=1, column=0, pady=2)
        ttk.Button(profile_buttons_frame, text="삭제", command=self.delete_profile).grid(row=2, column=0, pady=2)
        ttk.Button(profile_buttons_frame, text="활성화", command=self.activate_profile).grid(row=3, column=0, pady=2)
        
        # 프로필 상세 정보
        detail_frame = ttk.LabelFrame(profile_frame, text="프로필 상세 정보", padding="10")
        detail_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 프로필 정보 표시
        self.profile_info_text = tk.Text(detail_frame, height=15, width=40)
        self.profile_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        profile_frame.columnconfigure(1, weight=1)
        profile_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
    def create_template_tab(self, notebook):
        """템플릿 관리 탭 생성"""
        template_frame = ttk.Frame(notebook)
        notebook.add(template_frame, text="예약 템플릿")
        
        # 템플릿 목록
        list_frame = ttk.LabelFrame(template_frame, text="템플릿 목록", padding="10")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 템플릿 리스트박스
        self.template_listbox = tk.Listbox(list_frame, height=10, width=30)
        self.template_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        self.template_listbox.bind('<<ListboxSelect>>', self.on_template_select)
        
        # 템플릿 버튼들
        template_buttons_frame = ttk.Frame(list_frame)
        template_buttons_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        ttk.Button(template_buttons_frame, text="새 템플릿", command=self.add_template).grid(row=0, column=0, pady=2)
        ttk.Button(template_buttons_frame, text="편집", command=self.edit_template).grid(row=1, column=0, pady=2)
        ttk.Button(template_buttons_frame, text="삭제", command=self.delete_template).grid(row=2, column=0, pady=2)
        ttk.Button(template_buttons_frame, text="활성화", command=self.activate_template).grid(row=3, column=0, pady=2)
        
        # 템플릿 상세 정보
        detail_frame = ttk.LabelFrame(template_frame, text="템플릿 상세 정보", padding="10")
        detail_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 템플릿 정보 표시
        self.template_info_text = tk.Text(detail_frame, height=15, width=40)
        self.template_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        template_frame.columnconfigure(1, weight=1)
        template_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
    def create_settings_tab(self, notebook):
        """설정 관리 탭 생성"""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="자동화 설정")
        
        # 자동 체크 설정
        auto_check_frame = ttk.LabelFrame(settings_frame, text="자동 체크 설정", padding="10")
        auto_check_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 체크박스들
        self.auto_check_vars = {}
        auto_check_options = [
            ("terms_agreement", "약관 동의 자동 체크"),
            ("center_selection", "센터/공관 자동 선택"),
            ("service_selection", "서비스 자동 선택"),
            ("date_time_selection", "날짜/시간 자동 선택"),
            ("applicant_info", "신청자 정보 자동 입력"),
            ("confirmation", "최종 확인 자동 처리")
        ]
        
        for i, (key, text) in enumerate(auto_check_options):
            var = tk.BooleanVar()
            self.auto_check_vars[key] = var
            ttk.Checkbutton(auto_check_frame, text=text, variable=var, 
                           command=lambda k=key: self.update_auto_check_setting(k)).grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # 설정 저장/불러오기
        settings_buttons_frame = ttk.Frame(settings_frame)
        settings_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Button(settings_buttons_frame, text="설정 저장", command=self.save_settings).grid(row=0, column=0, padx=5)
        ttk.Button(settings_buttons_frame, text="설정 불러오기", command=self.load_settings).grid(row=0, column=1, padx=5)
        ttk.Button(settings_buttons_frame, text="기본값으로 복원", command=self.reset_settings).grid(row=0, column=2, padx=5)
        
    def create_automation_tab(self, notebook):
        """자동화 실행 탭 생성"""
        automation_frame = ttk.Frame(notebook)
        notebook.add(automation_frame, text="자동화 실행")
        
        # 자동화 상태
        status_frame = ttk.LabelFrame(automation_frame, text="자동화 상태", padding="10")
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.automation_status_var = tk.StringVar(value="대기 중")
        ttk.Label(status_frame, textvariable=self.automation_status_var, font=('Arial', 12, 'bold')).grid(row=0, column=0, pady=10)
        
        # 자동화 제어 버튼들
        control_frame = ttk.LabelFrame(automation_frame, text="자동화 제어", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Button(control_frame, text="자동화 시작", command=self.start_automation).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="자동화 중지", command=self.stop_automation).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="설정 검증", command=self.validate_settings).grid(row=0, column=2, padx=5, pady=5)
        
        # 로그 표시
        log_frame = ttk.LabelFrame(automation_frame, text="실행 로그", padding="10")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # 그리드 가중치 설정
        automation_frame.columnconfigure(0, weight=1)
        automation_frame.rowconfigure(2, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def load_data(self):
        """데이터 로드"""
        self.refresh_profile_list()
        self.refresh_template_list()
        self.load_auto_check_settings()
        self.update_dashboard()
        
    def refresh_profile_list(self):
        """프로필 목록 새로고침"""
        self.profile_listbox.delete(0, tk.END)
        profiles = self.config_manager.profile_manager.list_profiles()
        active_profile = self.config_manager.profile_manager.active_profile
        
        for profile in profiles:
            if profile == active_profile:
                self.profile_listbox.insert(tk.END, f"* {profile}")
            else:
                self.profile_listbox.insert(tk.END, profile)
                
    def refresh_template_list(self):
        """템플릿 목록 새로고침"""
        self.template_listbox.delete(0, tk.END)
        templates = self.config_manager.template_manager.list_templates()
        active_template = self.config_manager.template_manager.active_template
        
        for template in templates:
            template_data = self.config_manager.template_manager.templates.get(template, {})
            display_name = f"{template} - {template_data.get('name', 'N/A')}"
            if template == active_template:
                self.template_listbox.insert(tk.END, f"* {display_name}")
            else:
                self.template_listbox.insert(tk.END, display_name)
                
    def load_auto_check_settings(self):
        """자동 체크 설정 로드"""
        settings = self.config_manager.auto_check_manager.settings.get('auto_check_settings', {})
        for key, var in self.auto_check_vars.items():
            var.set(settings.get(key, {}).get('enabled', False))
            
    def update_dashboard(self):
        """대시보드 업데이트"""
        # 활성 프로필
        profile = self.config_manager.profile_manager.get_active_profile()
        if profile:
            self.active_profile_var.set(profile.get('name', 'N/A'))
        else:
            self.active_profile_var.set("설정되지 않음")
            
        # 활성 템플릿
        template = self.config_manager.template_manager.get_active_template()
        if template:
            self.active_template_var.set(template.get('name', 'N/A'))
        else:
            self.active_template_var.set("설정되지 않음")
            
        # 자동화 상태
        enabled_checks = [k for k, v in self.auto_check_vars.items() if v.get()]
        if enabled_checks:
            self.auto_status_var.set(f"활성화됨 ({len(enabled_checks)}개 기능)")
        else:
            self.auto_status_var.set("비활성화됨")
            
    def on_profile_select(self, event):
        """프로필 선택 이벤트"""
        selection = self.profile_listbox.curselection()
        if selection:
            profile_name = self.profile_listbox.get(selection[0]).replace("* ", "")
            profile_data = self.config_manager.profile_manager.profiles.get(profile_name)
            if profile_data:
                self.profile_info_text.delete(1.0, tk.END)
                self.profile_info_text.insert(tk.END, json.dumps(profile_data, ensure_ascii=False, indent=2))
                
    def on_template_select(self, event):
        """템플릿 선택 이벤트"""
        selection = self.template_listbox.curselection()
        if selection:
            template_name = self.template_listbox.get(selection[0]).split(" - ")[0].replace("* ", "")
            template_data = self.config_manager.template_manager.templates.get(template_name)
            if template_data:
                self.template_info_text.delete(1.0, tk.END)
                self.template_info_text.insert(tk.END, json.dumps(template_data, ensure_ascii=False, indent=2))
                
    def add_profile(self):
        """프로필 추가"""
        # 간단한 프로필 추가 다이얼로그
        dialog = ProfileDialog(self.root, "새 프로필 추가")
        if dialog.result:
            profile_data = dialog.result
            profile_name = profile_data.pop('name', '새프로필')
            
            if self.config_manager.profile_manager.add_profile(profile_name, profile_data):
                self.refresh_profile_list()
                self.update_dashboard()
                messagebox.showinfo("성공", f"프로필 '{profile_name}'이 추가되었습니다.")
            else:
                messagebox.showerror("오류", "프로필 추가에 실패했습니다.")
                
    def edit_profile(self):
        """프로필 편집"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "편집할 프로필을 선택해주세요.")
            return
            
        profile_name = self.profile_listbox.get(selection[0]).replace("* ", "")
        profile_data = self.config_manager.profile_manager.profiles.get(profile_name)
        
        if profile_data:
            dialog = ProfileDialog(self.root, f"프로필 '{profile_name}' 편집", profile_data)
            if dialog.result:
                updated_data = dialog.result
                if self.config_manager.profile_manager.update_profile(profile_name, updated_data):
                    self.refresh_profile_list()
                    self.update_dashboard()
                    messagebox.showinfo("성공", "프로필이 업데이트되었습니다.")
                else:
                    messagebox.showerror("오류", "프로필 업데이트에 실패했습니다.")
                    
    def delete_profile(self):
        """프로필 삭제"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 프로필을 선택해주세요.")
            return
            
        profile_name = self.profile_listbox.get(selection[0]).replace("* ", "")
        
        if messagebox.askyesno("확인", f"프로필 '{profile_name}'을 삭제하시겠습니까?"):
            if self.config_manager.profile_manager.delete_profile(profile_name):
                self.refresh_profile_list()
                self.update_dashboard()
                messagebox.showinfo("성공", "프로필이 삭제되었습니다.")
            else:
                messagebox.showerror("오류", "프로필 삭제에 실패했습니다.")
                
    def activate_profile(self):
        """프로필 활성화"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "활성화할 프로필을 선택해주세요.")
            return
            
        profile_name = self.profile_listbox.get(selection[0]).replace("* ", "")
        
        if self.config_manager.profile_manager.set_active_profile(profile_name):
            self.refresh_profile_list()
            self.update_dashboard()
            messagebox.showinfo("성공", f"프로필 '{profile_name}'이 활성화되었습니다.")
        else:
            messagebox.showerror("오류", "프로필 활성화에 실패했습니다.")
            
    def add_template(self):
        """템플릿 추가"""
        dialog = TemplateDialog(self.root, "새 템플릿 추가")
        if dialog.result:
            template_data = dialog.result
            template_name = template_data.pop('name', '새템플릿')
            
            if self.config_manager.template_manager.add_template(template_name, template_data):
                self.refresh_template_list()
                self.update_dashboard()
                messagebox.showinfo("성공", f"템플릿 '{template_name}'이 추가되었습니다.")
            else:
                messagebox.showerror("오류", "템플릿 추가에 실패했습니다.")
                
    def edit_template(self):
        """템플릿 편집"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "편집할 템플릿을 선택해주세요.")
            return
            
        template_name = self.template_listbox.get(selection[0]).split(" - ")[0].replace("* ", "")
        template_data = self.config_manager.template_manager.templates.get(template_name)
        
        if template_data:
            dialog = TemplateDialog(self.root, f"템플릿 '{template_name}' 편집", template_data)
            if dialog.result:
                updated_data = dialog.result
                if self.config_manager.template_manager.update_template(template_name, updated_data):
                    self.refresh_template_list()
                    self.update_dashboard()
                    messagebox.showinfo("성공", "템플릿이 업데이트되었습니다.")
                else:
                    messagebox.showerror("오류", "템플릿 업데이트에 실패했습니다.")
                    
    def delete_template(self):
        """템플릿 삭제"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 템플릿을 선택해주세요.")
            return
            
        template_name = self.template_listbox.get(selection[0]).split(" - ")[0].replace("* ", "")
        
        if messagebox.askyesno("확인", f"템플릿 '{template_name}'을 삭제하시겠습니까?"):
            if self.config_manager.template_manager.delete_template(template_name):
                self.refresh_template_list()
                self.update_dashboard()
                messagebox.showinfo("성공", "템플릿이 삭제되었습니다.")
            else:
                messagebox.showerror("오류", "템플릿 삭제에 실패했습니다.")
                
    def activate_template(self):
        """템플릿 활성화"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "활성화할 템플릿을 선택해주세요.")
            return
            
        template_name = self.template_listbox.get(selection[0]).split(" - ")[0].replace("* ", "")
        
        if self.config_manager.template_manager.set_active_template(template_name):
            self.refresh_template_list()
            self.update_dashboard()
            messagebox.showinfo("성공", f"템플릿 '{template_name}'이 활성화되었습니다.")
        else:
            messagebox.showerror("오류", "템플릿 활성화에 실패했습니다.")
            
    def update_auto_check_setting(self, key):
        """자동 체크 설정 업데이트"""
        enabled = self.auto_check_vars[key].get()
        self.config_manager.auto_check_manager.set_setting(f'auto_check_settings.{key}.enabled', enabled)
        self.update_dashboard()
        
    def save_settings(self):
        """설정 저장"""
        try:
            self.config_manager.auto_check_manager.save_settings()
            messagebox.showinfo("성공", "설정이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장에 실패했습니다: {e}")
            
    def load_settings(self):
        """설정 불러오기"""
        try:
            self.config_manager.auto_check_manager.load_settings()
            self.load_auto_check_settings()
            self.update_dashboard()
            messagebox.showinfo("성공", "설정을 불러왔습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 불러오기에 실패했습니다: {e}")
            
    def reset_settings(self):
        """설정 초기화"""
        if messagebox.askyesno("확인", "설정을 기본값으로 복원하시겠습니까?"):
            # 기본 설정으로 복원
            default_settings = {
                "auto_check_settings": {
                    "terms_agreement": {"enabled": True},
                    "center_selection": {"enabled": True},
                    "service_selection": {"enabled": True},
                    "date_time_selection": {"enabled": True},
                    "applicant_info": {"enabled": True},
                    "confirmation": {"enabled": True, "auto_confirm": False}
                }
            }
            
            self.config_manager.auto_check_manager.settings = default_settings
            self.config_manager.auto_check_manager.save_settings()
            self.load_auto_check_settings()
            self.update_dashboard()
            messagebox.showinfo("성공", "설정이 기본값으로 복원되었습니다.")
            
    def start_automation(self):
        """자동화 시작"""
        # 설정 검증
        validation = self.config_manager.validate_config()
        if validation['errors']:
            error_msg = "설정 오류가 발견되었습니다:\n" + "\n".join(validation['errors'])
            messagebox.showerror("오류", error_msg)
            return
            
        # 자동화 실행 (별도 스레드)
        self.automation_status_var.set("실행 중...")
        self.status_var.set("자동화 실행 중")
        
        def run_automation():
            try:
                # 여기에 실제 자동화 코드 추가
                import g4k_hybrid_automation
                # 자동화 실행 로직
                self.log_message("자동화가 시작되었습니다.")
                self.log_message("G4K 사이트에 접속 중...")
                # 실제 자동화 실행
                
            except Exception as e:
                self.log_message(f"자동화 실행 중 오류 발생: {e}")
                self.automation_status_var.set("오류 발생")
            finally:
                self.automation_status_var.set("완료")
                self.status_var.set("준비됨")
                
        threading.Thread(target=run_automation, daemon=True).start()
        
    def stop_automation(self):
        """자동화 중지"""
        self.automation_status_var.set("중지됨")
        self.status_var.set("준비됨")
        self.log_message("자동화가 중지되었습니다.")
        
    def validate_settings(self):
        """설정 검증"""
        validation = self.config_manager.validate_config()
        
        if validation['errors']:
            error_msg = "설정 오류:\n" + "\n".join(validation['errors'])
            messagebox.showerror("검증 실패", error_msg)
        elif validation['warnings']:
            warning_msg = "설정 경고:\n" + "\n".join(validation['warnings'])
            messagebox.showwarning("검증 경고", warning_msg)
        else:
            messagebox.showinfo("검증 성공", "모든 설정이 유효합니다.")
            
    def view_logs(self):
        """로그 보기"""
        log_file = "g4k_automation.log"
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    
                # 로그 창 생성
                log_window = tk.Toplevel(self.root)
                log_window.title("로그 보기")
                log_window.geometry("800x600")
                
                text_widget = tk.Text(log_window)
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text_widget.insert(tk.END, log_content)
                
            except Exception as e:
                messagebox.showerror("오류", f"로그 파일을 읽을 수 없습니다: {e}")
        else:
            messagebox.showinfo("정보", "로그 파일이 없습니다.")
            
    def open_web_dashboard(self):
        """웹 대시보드 열기"""
        try:
            # 웹 대시보드 서버 시작 (별도 스레드)
            def start_web_server():
                from web_dashboard import start_web_dashboard
                start_web_dashboard()
                
            threading.Thread(target=start_web_server, daemon=True).start()
            
            # 브라우저에서 열기
            webbrowser.open("http://localhost:8080")
            
        except Exception as e:
            messagebox.showerror("오류", f"웹 대시보드를 열 수 없습니다: {e}")
            
    def log_message(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 활동 로그에도 추가
        self.activity_text.insert(tk.END, log_entry)
        self.activity_text.see(tk.END)
        
    def run(self):
        """GUI 실행"""
        self.root.mainloop()


class ProfileDialog:
    """프로필 추가/편집 다이얼로그"""
    def __init__(self, parent, title, profile_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui(profile_data)
        
    def setup_ui(self, profile_data):
        """UI 구성"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 입력 필드들
        fields = [
            ("name", "이름", "홍길동"),
            ("name_english", "영문 이름", "Hong Gildong"),
            ("phone", "전화번호", "010-1234-5678"),
            ("email", "이메일", "user@example.com"),
            ("id_type", "신분증 종류", "passport"),
            ("id_number", "신분증 번호", "M12345678"),
            ("birth_date", "생년월일", "1990-01-01"),
            ("nationality", "국적", "KR"),
            ("address", "주소", "서울특별시 강남구")
        ]
        
        self.entries = {}
        for i, (key, label, default) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            
            if key == "id_type":
                # 콤보박스
                var = tk.StringVar(value=profile_data.get(key, default) if profile_data else default)
                combo = ttk.Combobox(main_frame, textvariable=var, values=["passport", "residence_card"])
                combo.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                self.entries[key] = var
            else:
                # 텍스트 입력
                var = tk.StringVar(value=profile_data.get(key, default) if profile_data else default)
                entry = ttk.Entry(main_frame, textvariable=var, width=30)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                self.entries[key] = var
                
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="저장", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(1, weight=1)
        
    def save(self):
        """저장"""
        self.result = {key: var.get() for key, var in self.entries.items()}
        self.dialog.destroy()
        
    def cancel(self):
        """취소"""
        self.dialog.destroy()


class TemplateDialog:
    """템플릿 추가/편집 다이얼로그"""
    def __init__(self, parent, title, template_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui(template_data)
        
    def setup_ui(self, template_data):
        """UI 구성"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 입력 필드들
        fields = [
            ("name", "템플릿 이름", "운전면허증 갱신"),
            ("center_type", "센터 타입", "gwanghwamun"),
            ("service_type", "서비스 타입", "drivers_license"),
            ("service_detail", "서비스 상세", "renewal"),
            ("service_code", "서비스 코드", "DL001"),
            ("description", "설명", "운전면허증 갱신 예약")
        ]
        
        self.entries = {}
        for i, (key, label, default) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            
            if key == "center_type":
                var = tk.StringVar(value=template_data.get(key, default) if template_data else default)
                combo = ttk.Combobox(main_frame, textvariable=var, values=["gwanghwamun", "embassy"])
                combo.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                self.entries[key] = var
            else:
                var = tk.StringVar(value=template_data.get(key, default) if template_data else default)
                entry = ttk.Entry(main_frame, textvariable=var, width=30)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                self.entries[key] = var
                
        # 희망 날짜/시간
        ttk.Label(main_frame, text="희망 날짜 (한 줄에 하나씩)").grid(row=len(fields), column=0, sticky=tk.W, pady=(10, 2))
        self.dates_text = tk.Text(main_frame, height=3, width=30)
        self.dates_text.grid(row=len(fields), column=1, sticky=(tk.W, tk.E), pady=(10, 2), padx=(10, 0))
        
        if template_data and 'preferred_dates' in template_data:
            self.dates_text.insert(tk.END, "\n".join(template_data['preferred_dates']))
        else:
            self.dates_text.insert(tk.END, "2024-01-15\n2024-01-16\n2024-01-17")
            
        ttk.Label(main_frame, text="희망 시간 (한 줄에 하나씩)").grid(row=len(fields)+1, column=0, sticky=tk.W, pady=(10, 2))
        self.times_text = tk.Text(main_frame, height=3, width=30)
        self.times_text.grid(row=len(fields)+1, column=1, sticky=(tk.W, tk.E), pady=(10, 2), padx=(10, 0))
        
        if template_data and 'preferred_times' in template_data:
            self.times_text.insert(tk.END, "\n".join(template_data['preferred_times']))
        else:
            self.times_text.insert(tk.END, "09:00\n10:00\n11:00")
            
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="저장", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(1, weight=1)
        
    def save(self):
        """저장"""
        self.result = {key: var.get() for key, var in self.entries.items()}
        
        # 날짜/시간 파싱
        dates = [line.strip() for line in self.dates_text.get(1.0, tk.END).split('\n') if line.strip()]
        times = [line.strip() for line in self.times_text.get(1.0, tk.END).split('\n') if line.strip()]
        
        self.result['preferred_dates'] = dates
        self.result['preferred_times'] = times
        
        # 기본 자동 재시도 설정
        self.result['auto_retry'] = {
            'enabled': True,
            'interval_minutes': 30,
            'max_retries': 10
        }
        
        self.dialog.destroy()
        
    def cancel(self):
        """취소"""
        self.dialog.destroy()


def main():
    """메인 함수"""
    app = G4KGuiManager()
    app.run()


if __name__ == "__main__":
    main() 
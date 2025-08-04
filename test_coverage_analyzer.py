#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G4K 자동화 시스템 테스트 커버리지 분석기
코드 품질 및 테스트 범위 분석
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Set


class CodeAnalyzer:
    """코드 분석기"""
    
    def __init__(self):
        self.python_files = []
        self.functions = {}
        self.classes = {}
        self.imports = {}
        self.complexity_scores = {}
    
    def analyze_codebase(self):
        """코드베이스 분석"""
        self.python_files = [f for f in os.listdir('.') if f.endswith('.py')]
        
        for py_file in self.python_files:
            self._analyze_file(py_file)
        
        return {
            'files_analyzed': len(self.python_files),
            'total_functions': sum(len(funcs) for funcs in self.functions.values()),
            'total_classes': sum(len(classes) for classes in self.classes.values()),
            'complexity_analysis': self._analyze_complexity()
        }
    
    def _analyze_file(self, filename: str):
        """개별 파일 분석"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 함수 찾기
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            self.functions[filename] = functions
            
            # 클래스 찾기
            classes = re.findall(r'class\s+(\w+)\s*[\(:]', content)
            self.classes[filename] = classes
            
            # import 찾기
            imports = re.findall(r'(?:from\s+\w+\s+)?import\s+([^\n]+)', content)
            self.imports[filename] = imports
            
            # 복잡도 점수 계산
            self.complexity_scores[filename] = self._calculate_complexity(content)
            
        except Exception as e:
            print(f"파일 분석 오류 {filename}: {e}")
    
    def _calculate_complexity(self, content: str) -> Dict:
        """코드 복잡도 계산"""
        lines = content.split('\n')
        
        # 기본 메트릭
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        # 제어 구조 카운트
        if_count = len(re.findall(r'\bif\b', content))
        for_count = len(re.findall(r'\bfor\b', content))
        while_count = len(re.findall(r'\bwhile\b', content))
        try_count = len(re.findall(r'\btry\b', content))
        
        # 복잡도 점수 (McCabe Cyclomatic Complexity 근사)
        complexity_score = 1 + if_count + for_count + while_count + try_count
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'comment_ratio': comment_lines / total_lines if total_lines > 0 else 0,
            'control_structures': if_count + for_count + while_count,
            'complexity_score': complexity_score,
            'complexity_level': self._get_complexity_level(complexity_score)
        }
    
    def _get_complexity_level(self, score: int) -> str:
        """복잡도 레벨 반환"""
        if score <= 10:
            return 'LOW'
        elif score <= 20:
            return 'MEDIUM'
        elif score <= 50:
            return 'HIGH'
        else:
            return 'VERY_HIGH'
    
    def _analyze_complexity(self) -> Dict:
        """전체 복잡도 분석"""
        if not self.complexity_scores:
            return {}
        
        total_complexity = sum(score['complexity_score'] for score in self.complexity_scores.values())
        avg_complexity = total_complexity / len(self.complexity_scores)
        
        complexity_levels = {}
        for filename, metrics in self.complexity_scores.items():
            level = metrics['complexity_level']
            complexity_levels[level] = complexity_levels.get(level, 0) + 1
        
        return {
            'average_complexity': round(avg_complexity, 2),
            'total_complexity': total_complexity,
            'complexity_distribution': complexity_levels,
            'high_complexity_files': [
                filename for filename, metrics in self.complexity_scores.items()
                if metrics['complexity_level'] in ['HIGH', 'VERY_HIGH']
            ]
        }


class TestCoverageAnalyzer:
    """테스트 커버리지 분석기"""
    
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.test_files = []
        self.coverage_report = {}
    
    def analyze_coverage(self):
        """테스트 커버리지 분석"""
        # 코드베이스 분석
        code_analysis = self.code_analyzer.analyze_codebase()
        
        # 테스트 파일 찾기
        self.test_files = [f for f in os.listdir('.') if 'test' in f.lower() and f.endswith('.py')]
        
        # 커버리지 분석
        coverage_analysis = self._analyze_test_coverage()
        
        # 품질 점수 계산
        quality_score = self._calculate_quality_score(code_analysis, coverage_analysis)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'code_analysis': code_analysis,
            'test_coverage': coverage_analysis,
            'quality_metrics': quality_score,
            'recommendations': self._generate_recommendations(code_analysis, coverage_analysis)
        }
    
    def _analyze_test_coverage(self) -> Dict:
        """테스트 커버리지 세부 분석"""
        if not self.test_files:
            return {
                'test_files_count': 0,
                'estimated_coverage': 0,
                'coverage_level': 'NONE',
                'tested_modules': []
            }
        
        # 테스트 파일에서 import된 모듈 찾기
        tested_modules = set()
        test_functions = []
        
        for test_file in self.test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # import된 모듈 찾기
                imports = re.findall(r'from\s+(\w+)\s+import', content)
                tested_modules.update(imports)
                
                # 테스트 함수 찾기
                test_funcs = re.findall(r'def\s+(test_\w+)', content)
                test_functions.extend(test_funcs)
                
            except Exception as e:
                print(f"테스트 파일 분석 오류 {test_file}: {e}")
        
        # 커버리지 추정
        total_modules = len(self.code_analyzer.python_files)
        tested_module_count = len(tested_modules)
        
        estimated_coverage = (tested_module_count / total_modules * 100) if total_modules > 0 else 0
        
        coverage_level = self._get_coverage_level(estimated_coverage)
        
        return {
            'test_files_count': len(self.test_files),
            'test_functions_count': len(test_functions),
            'tested_modules': list(tested_modules),
            'tested_module_count': tested_module_count,
            'total_modules': total_modules,
            'estimated_coverage': round(estimated_coverage, 1),
            'coverage_level': coverage_level
        }
    
    def _get_coverage_level(self, coverage: float) -> str:
        """커버리지 레벨 반환"""
        if coverage >= 80:
            return 'EXCELLENT'
        elif coverage >= 60:
            return 'GOOD'
        elif coverage >= 40:
            return 'FAIR'
        elif coverage >= 20:
            return 'POOR'
        else:
            return 'NONE'
    
    def _calculate_quality_score(self, code_analysis: Dict, coverage_analysis: Dict) -> Dict:
        """품질 점수 계산"""
        scores = {}
        
        # 코드 구조 점수 (40점)
        structure_score = 0
        if code_analysis.get('total_functions', 0) > 0:
            structure_score += 10  # 함수가 있음
        if code_analysis.get('total_classes', 0) > 0:
            structure_score += 10  # 클래스가 있음
        
        complexity = code_analysis.get('complexity_analysis', {})
        if complexity.get('average_complexity', 0) <= 15:
            structure_score += 20  # 적절한 복잡도
        elif complexity.get('average_complexity', 0) <= 25:
            structure_score += 10  # 보통 복잡도
        
        scores['structure'] = min(structure_score, 40)
        
        # 테스트 점수 (30점)
        test_score = 0
        coverage = coverage_analysis.get('estimated_coverage', 0)
        if coverage >= 80:
            test_score = 30
        elif coverage >= 60:
            test_score = 25
        elif coverage >= 40:
            test_score = 20
        elif coverage >= 20:
            test_score = 15
        else:
            test_score = 5 if coverage_analysis.get('test_files_count', 0) > 0 else 0
        
        scores['testing'] = test_score
        
        # 문서화 점수 (20점)
        doc_score = 0
        if os.path.exists('README.md'):
            doc_score += 10
        if os.path.exists('CLAUDE.md'):
            doc_score += 5
        if os.path.exists('requirements.txt'):
            doc_score += 5
        
        scores['documentation'] = doc_score
        
        # 구성 점수 (10점)
        config_score = 0
        if os.path.exists('config.yaml'):
            config_score += 5
        if any(f.endswith('.json') for f in os.listdir('.')):
            config_score += 5
        
        scores['configuration'] = config_score
        
        # 총점
        total_score = sum(scores.values())
        
        return {
            'individual_scores': scores,
            'total_score': total_score,
            'max_score': 100,
            'grade': self._get_grade(total_score),
            'percentage': round(total_score, 1)
        }
    
    def _get_grade(self, score: float) -> str:
        """점수에 따른 등급 반환"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'C+'
        elif score >= 65:
            return 'C'
        elif score >= 60:
            return 'D+'
        elif score >= 55:
            return 'D'
        else:
            return 'F'
    
    def _generate_recommendations(self, code_analysis: Dict, coverage_analysis: Dict) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        # 테스트 관련 권장사항
        coverage = coverage_analysis.get('estimated_coverage', 0)
        if coverage < 60:
            recommendations.append("테스트 커버리지가 낮습니다. 단위 테스트를 추가하세요.")
        
        if coverage_analysis.get('test_files_count', 0) == 0:
            recommendations.append("테스트 파일이 없습니다. pytest 또는 unittest를 사용하여 테스트를 작성하세요.")
        
        # 복잡도 관련 권장사항
        complexity = code_analysis.get('complexity_analysis', {})
        high_complexity_files = complexity.get('high_complexity_files', [])
        
        if high_complexity_files:
            recommendations.append(f"복잡도가 높은 파일들을 리팩토링하세요: {', '.join(high_complexity_files[:3])}")
        
        if complexity.get('average_complexity', 0) > 20:
            recommendations.append("평균 복잡도가 높습니다. 함수를 더 작은 단위로 분리하세요.")
        
        # 문서화 권장사항
        if not os.path.exists('README.md'):
            recommendations.append("README.md 파일을 작성하여 프로젝트 설명을 추가하세요.")
        
        # 일반 권장사항
        recommendations.extend([
            "CI/CD 파이프라인에서 자동 테스트를 설정하세요.",
            "코드 품질 도구(예: pylint, black)를 사용하세요.",
            "정기적으로 테스트를 실행하여 회귀를 방지하세요."
        ])
        
        return recommendations[:8]  # 최대 8개 권장사항


def main():
    """메인 실행 함수"""
    print("G4K 자동화 시스템 테스트 커버리지 분석")
    print("=" * 50)
    
    analyzer = TestCoverageAnalyzer()
    results = analyzer.analyze_coverage()
    
    # 결과 출력
    print(f"분석 시간: {results['timestamp'][:19]}")
    print()
    
    # 코드 분석 결과
    code_analysis = results['code_analysis']
    print("코드 분석 결과:")
    print(f"  파일 수:        {code_analysis['files_analyzed']}")
    print(f"  함수 수:        {code_analysis['total_functions']}")
    print(f"  클래스 수:      {code_analysis['total_classes']}")
    
    complexity = code_analysis.get('complexity_analysis', {})
    if complexity:
        print(f"  평균 복잡도:    {complexity.get('average_complexity', 0)}")
        print(f"  고복잡도 파일: {len(complexity.get('high_complexity_files', []))}")
    
    print()
    
    # 테스트 커버리지 결과
    coverage = results['test_coverage']
    print("테스트 커버리지:")
    print(f"  테스트 파일:    {coverage['test_files_count']}")
    print(f"  테스트 함수:    {coverage['test_functions_count']}")
    print(f"  커버리지 추정:  {coverage['estimated_coverage']}%")
    print(f"  커버리지 레벨:  {coverage['coverage_level']}")
    print()
    
    # 품질 점수
    quality = results['quality_metrics']
    print("품질 점수:")
    scores = quality['individual_scores']
    print(f"  구조:          {scores.get('structure', 0)}/40")
    print(f"  테스트:        {scores.get('testing', 0)}/30")
    print(f"  문서화:        {scores.get('documentation', 0)}/20")
    print(f"  구성:          {scores.get('configuration', 0)}/10")
    print(f"  총점:          {quality['total_score']}/100 ({quality['grade']})")
    print()
    
    # 권장사항
    print("개선 권장사항:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # JSON 보고서 저장
    report_file = f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n상세 보고서 저장: {report_file}")
    except Exception as e:
        print(f"보고서 저장 실패: {e}")


if __name__ == "__main__":
    main()
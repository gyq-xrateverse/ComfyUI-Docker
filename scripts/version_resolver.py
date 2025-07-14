#!/usr/bin/env python3
"""
版本优先级规则系统
定义包版本优先级规则、实现语义版本比较、创建兼容性矩阵
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Set
from packaging import version
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from dataclasses import dataclass, field
from enum import Enum

class VersionPriority(Enum):
    """版本优先级枚举"""
    CRITICAL = 1      # 关键包，必须使用指定版本
    HIGH = 2          # 高优先级，优先使用指定版本
    MEDIUM = 3        # 中等优先级，可以协商版本
    LOW = 4           # 低优先级，可以忽略版本要求
    FLEXIBLE = 5      # 灵活版本，可以使用任何兼容版本

@dataclass
class PackageVersionRule:
    """包版本规则"""
    package_name: str
    priority: VersionPriority
    preferred_version: Optional[str] = None
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    excluded_versions: Set[str] = field(default_factory=set)
    reason: str = ""
    source_priority: Dict[str, int] = field(default_factory=dict)

class VersionResolver:
    """版本解析器"""
    
    def __init__(self):
        self.rules: Dict[str, PackageVersionRule] = {}
        self.compatibility_matrix: Dict[str, Dict[str, bool]] = {}
        self.version_cache: Dict[str, List[str]] = {}
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """设置默认规则"""
        # 关键包规则
        critical_packages = {
            'torch': PackageVersionRule(
                package_name='torch',
                priority=VersionPriority.CRITICAL,
                preferred_version='2.6.0',
                reason='CUDA兼容性要求'
            ),
            'torchvision': PackageVersionRule(
                package_name='torchvision',
                priority=VersionPriority.CRITICAL,
                reason='与torch版本匹配'
            ),
            'torchaudio': PackageVersionRule(
                package_name='torchaudio',
                priority=VersionPriority.CRITICAL,
                reason='与torch版本匹配'
            ),
            'xformers': PackageVersionRule(
                package_name='xformers',
                priority=VersionPriority.CRITICAL,
                preferred_version='0.0.29.post3',
                reason='与torch 2.6.0兼容'
            ),
            'cuda-python': PackageVersionRule(
                package_name='cuda-python',
                priority=VersionPriority.CRITICAL,
                reason='CUDA运行时要求'
            )
        }
        
        # 高优先级包规则
        high_priority_packages = {
            'numpy': PackageVersionRule(
                package_name='numpy',
                priority=VersionPriority.HIGH,
                preferred_version='1.26.4',
                min_version='1.25.0',
                max_version='1.26.4',
                reason='稳定性和兼容性平衡'
            ),
            'pillow': PackageVersionRule(
                package_name='pillow',
                priority=VersionPriority.HIGH,
                min_version='10.1.0',
                reason='安全性和功能要求'
            ),
            'opencv-python': PackageVersionRule(
                package_name='opencv-python',
                priority=VersionPriority.HIGH,
                preferred_version='4.8.0.76',
                min_version='4.7.0.68',
                reason='ComfyUI兼容性'
            ),
            'transformers': PackageVersionRule(
                package_name='transformers',
                priority=VersionPriority.HIGH,
                min_version='4.45.0',
                reason='最新功能支持'
            )
        }
        
        # 中等优先级包规则
        medium_priority_packages = {
            'diffusers': PackageVersionRule(
                package_name='diffusers',
                priority=VersionPriority.MEDIUM,
                min_version='0.29.0',
                reason='稳定性要求'
            ),
            'accelerate': PackageVersionRule(
                package_name='accelerate',
                priority=VersionPriority.MEDIUM,
                min_version='0.26.0',
                reason='性能优化'
            ),
            'safetensors': PackageVersionRule(
                package_name='safetensors',
                priority=VersionPriority.MEDIUM,
                min_version='0.4.2',
                reason='安全性要求'
            )
        }
        
        # 问题包规则
        problematic_packages = {
            'insightface': PackageVersionRule(
                package_name='insightface',
                priority=VersionPriority.HIGH,
                preferred_version='0.7.3',
                reason='编译问题，需要特定版本'
            ),
            'dlib': PackageVersionRule(
                package_name='dlib',
                priority=VersionPriority.HIGH,
                preferred_version='19.24.2',
                reason='编译复杂，使用稳定版本'
            ),
            'fairscale': PackageVersionRule(
                package_name='fairscale',
                priority=VersionPriority.HIGH,
                preferred_version='0.4.13',
                reason='与PyTorch版本兼容'
            ),
            'pytorch-lightning': PackageVersionRule(
                package_name='pytorch-lightning',
                priority=VersionPriority.MEDIUM,
                preferred_version='2.5.2',
                reason='稳定性要求'
            )
        }
        
        # 合并所有规则
        self.rules.update(critical_packages)
        self.rules.update(high_priority_packages)
        self.rules.update(medium_priority_packages)
        self.rules.update(problematic_packages)
        
        # 设置源优先级
        self.setup_source_priorities()
    
    def setup_source_priorities(self):
        """设置源优先级"""
        source_priorities = {
            'additional_packages': 10,  # 最高优先级
            'comfyanonymous': 9,        # ComfyUI主仓库
            'ltdrdata': 8,              # ComfyUI-Manager等核心插件
            'kijai': 7,                 # 知名开发者
            'cubiq': 7,                 # 知名开发者
            'Fannovel16': 6,            # 常用插件
            'default': 5                # 默认优先级
        }
        
        for rule in self.rules.values():
            rule.source_priority = source_priorities
    
    def add_rule(self, rule: PackageVersionRule):
        """添加版本规则"""
        self.rules[rule.package_name.lower()] = rule
    
    def get_rule(self, package_name: str) -> Optional[PackageVersionRule]:
        """获取包的版本规则"""
        return self.rules.get(package_name.lower())
    
    def compare_versions(self, version1: str, version2: str) -> int:
        """比较两个版本
        返回值：-1 (version1 < version2), 0 (相等), 1 (version1 > version2)
        """
        try:
            v1 = version.parse(version1)
            v2 = version.parse(version2)
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0
        except Exception:
            # 如果版本解析失败，按字符串比较
            if version1 < version2:
                return -1
            elif version1 > version2:
                return 1
            else:
                return 0
    
    def is_version_compatible(self, package_name: str, version_str: str) -> bool:
        """检查版本是否兼容"""
        rule = self.get_rule(package_name)
        if not rule:
            return True  # 没有规则的包默认兼容
        
        try:
            v = version.parse(version_str)
            
            # 检查排除版本
            if version_str in rule.excluded_versions:
                return False
            
            # 检查最小版本
            if rule.min_version:
                min_v = version.parse(rule.min_version)
                if v < min_v:
                    return False
            
            # 检查最大版本
            if rule.max_version:
                max_v = version.parse(rule.max_version)
                if v > max_v:
                    return False
            
            return True
        except Exception:
            return False
    
    def resolve_version_conflict(self, package_name: str, requirements: List[Dict]) -> Optional[str]:
        """解决版本冲突"""
        rule = self.get_rule(package_name)
        
        # 如果有首选版本且兼容，优先使用
        if rule and rule.preferred_version:
            if self.is_version_compatible(package_name, rule.preferred_version):
                # 检查是否满足所有requirements
                if self._check_version_satisfies_requirements(rule.preferred_version, requirements):
                    return rule.preferred_version
        
        # 收集所有可能的版本
        candidate_versions = set()
        
        for req_info in requirements:
            req = req_info['requirement']
            if req.specifier:
                # 这里简化处理，实际应该从PyPI获取版本列表
                # 目前基于specifier推断可能的版本
                if '==' in str(req.specifier):
                    # 精确版本
                    exact_version = str(req.specifier).replace('==', '').strip()
                    candidate_versions.add(exact_version)
        
        # 如果没有精确版本，尝试使用规则中的版本
        if not candidate_versions and rule:
            if rule.preferred_version:
                candidate_versions.add(rule.preferred_version)
            if rule.min_version:
                candidate_versions.add(rule.min_version)
        
        # 选择最佳版本
        if candidate_versions:
            # 按优先级和版本号排序
            sorted_versions = sorted(candidate_versions, key=lambda x: version.parse(x), reverse=True)
            for v in sorted_versions:
                if self.is_version_compatible(package_name, v):
                    if self._check_version_satisfies_requirements(v, requirements):
                        return v
        
        # 如果都不行，返回None让调用者处理
        return None
    
    def _check_version_satisfies_requirements(self, version_str: str, requirements: List[Dict]) -> bool:
        """检查版本是否满足所有requirements"""
        try:
            v = version.parse(version_str)
            for req_info in requirements:
                req = req_info['requirement']
                if req.specifier and not req.specifier.contains(version_str):
                    return False
            return True
        except Exception:
            return False
    
    def get_version_priority_score(self, package_name: str, version_str: str, source: str) -> int:
        """获取版本优先级分数（分数越高优先级越高）"""
        rule = self.get_rule(package_name)
        score = 0
        
        # 基于规则优先级
        if rule:
            priority_scores = {
                VersionPriority.CRITICAL: 1000,
                VersionPriority.HIGH: 800,
                VersionPriority.MEDIUM: 600,
                VersionPriority.LOW: 400,
                VersionPriority.FLEXIBLE: 200
            }
            score += priority_scores.get(rule.priority, 0)
            
            # 首选版本加分
            if rule.preferred_version == version_str:
                score += 100
            
            # 源优先级加分
            source_score = rule.source_priority.get(source, rule.source_priority.get('default', 5))
            score += source_score * 10
        
        return score
    
    def generate_compatibility_matrix(self, packages: List[str]) -> Dict[str, Dict[str, bool]]:
        """生成兼容性矩阵"""
        matrix = {}
        
        for pkg1 in packages:
            matrix[pkg1] = {}
            for pkg2 in packages:
                if pkg1 == pkg2:
                    matrix[pkg1][pkg2] = True
                else:
                    # 简化的兼容性检查
                    matrix[pkg1][pkg2] = self._check_package_compatibility(pkg1, pkg2)
        
        return matrix
    
    def _check_package_compatibility(self, pkg1: str, pkg2: str) -> bool:
        """检查两个包的兼容性"""
        # 已知不兼容的包组合
        incompatible_pairs = {
            ('torch', 'tensorflow'): 'GPU内存冲突',
            ('opencv-python', 'opencv-contrib-python'): '功能重复',
            ('pillow', 'pillow-simd'): '冲突实现',
        }
        
        pair = tuple(sorted([pkg1.lower(), pkg2.lower()]))
        return pair not in incompatible_pairs
    
    def save_rules(self, filename: str = "version_rules.json"):
        """保存规则到文件"""
        rules_data = {}
        for name, rule in self.rules.items():
            rules_data[name] = {
                'package_name': rule.package_name,
                'priority': rule.priority.name,
                'preferred_version': rule.preferred_version,
                'min_version': rule.min_version,
                'max_version': rule.max_version,
                'excluded_versions': list(rule.excluded_versions),
                'reason': rule.reason,
                'source_priority': rule.source_priority
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(rules_data, f, indent=2, ensure_ascii=False)
        
        print(f"版本规则已保存到: {filename}")
    
    def load_rules(self, filename: str):
        """从文件加载规则"""
        with open(filename, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
        
        for name, rule_data in rules_data.items():
            rule = PackageVersionRule(
                package_name=rule_data['package_name'],
                priority=VersionPriority[rule_data['priority']],
                preferred_version=rule_data.get('preferred_version'),
                min_version=rule_data.get('min_version'),
                max_version=rule_data.get('max_version'),
                excluded_versions=set(rule_data.get('excluded_versions', [])),
                reason=rule_data.get('reason', ''),
                source_priority=rule_data.get('source_priority', {})
            )
            self.rules[name] = rule
    
    def print_rules_summary(self):
        """打印规则摘要"""
        print("=" * 60)
        print("版本解析规则摘要")
        print("=" * 60)
        
        by_priority = {}
        for rule in self.rules.values():
            priority = rule.priority.name
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(rule)
        
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'FLEXIBLE']:
            if priority in by_priority:
                print(f"\n{priority} 优先级包:")
                for rule in by_priority[priority]:
                    version_info = ""
                    if rule.preferred_version:
                        version_info += f"首选: {rule.preferred_version}"
                    if rule.min_version:
                        version_info += f" 最小: {rule.min_version}"
                    if rule.max_version:
                        version_info += f" 最大: {rule.max_version}"
                    
                    print(f"  - {rule.package_name}: {version_info}")
                    if rule.reason:
                        print(f"    原因: {rule.reason}")
        
        print("=" * 60)

def main():
    """主函数"""
    resolver = VersionResolver()
    resolver.print_rules_summary()
    resolver.save_rules()
    
    # 测试版本解析
    print("\n测试版本解析:")
    test_requirements = [
        {
            'source': 'test1',
            'requirement': Requirement('numpy>=1.25.0'),
            'raw_string': 'numpy>=1.25.0'
        },
        {
            'source': 'test2',
            'requirement': Requirement('numpy==1.26.4'),
            'raw_string': 'numpy==1.26.4'
        }
    ]
    
    resolved_version = resolver.resolve_version_conflict('numpy', test_requirements)
    print(f"numpy冲突解析结果: {resolved_version}")

if __name__ == "__main__":
    main() 
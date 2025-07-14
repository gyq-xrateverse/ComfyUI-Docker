#!/usr/bin/env python3
"""
智能版本选择算法
基于冲突分析选择最优版本、处理依赖链冲突、生成统一的requirements.txt
"""

import json
import sys
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging import version

from dependency_analyzer import DependencyAnalyzer
from version_resolver import VersionResolver, VersionPriority

class SmartInstaller:
    """智能安装器"""
    
    def __init__(self):
        self.analyzer = DependencyAnalyzer()
        self.resolver = VersionResolver()
        self.resolved_packages = {}
        self.installation_order = []
        self.failed_packages = []
        self.excluded_packages = set()
        
    def analyze_dependencies(self):
        """分析依赖关系"""
        print("正在分析依赖关系...")
        
        # 从gather_requirements.py获取URL列表
        repo_requirements = [
            "https://github.com/comfyanonymous/ComfyUI/raw/master/requirements.txt",
            "https://github.com/crystian/ComfyUI-Crystools/raw/main/requirements.txt",
            "https://github.com/cubiq/ComfyUI_essentials/raw/main/requirements.txt",
            "https://github.com/cubiq/ComfyUI_FaceAnalysis/raw/main/requirements.txt",
            "https://github.com/cubiq/ComfyUI_InstantID/raw/main/requirements.txt",
            "https://github.com/cubiq/PuLID_ComfyUI/raw/main/requirements.txt",
            "https://github.com/Fannovel16/comfyui_controlnet_aux/raw/main/requirements.txt",
            "https://github.com/Fannovel16/ComfyUI-Frame-Interpolation/raw/main/requirements-no-cupy.txt",
            "https://github.com/FizzleDorf/ComfyUI_FizzNodes/raw/main/requirements.txt",
            "https://github.com/Gourieff/ComfyUI-ReActor/raw/main/requirements.txt",
            "https://github.com/huchenlei/ComfyUI-layerdiffuse/raw/main/requirements.txt",
            "https://github.com/jags111/efficiency-nodes-comfyui/raw/main/requirements.txt",
            "https://github.com/kijai/ComfyUI-KJNodes/raw/main/requirements.txt",
            "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite/raw/main/requirements.txt",
            "https://github.com/ltdrdata/ComfyUI-Impact-Pack/raw/Main/requirements.txt",
            "https://github.com/ltdrdata/ComfyUI-Impact-Subpack/raw/main/requirements.txt",
            "https://github.com/ltdrdata/ComfyUI-Inspire-Pack/raw/main/requirements.txt",
            "https://github.com/ltdrdata/ComfyUI-Manager/raw/main/requirements.txt",
            "https://github.com/melMass/comfy_mtb/raw/main/requirements.txt",
            "https://github.com/storyicon/comfyui_segment_anything/raw/main/requirements.txt",
            "https://github.com/WASasquatch/was-node-suite-comfyui/raw/main/requirements.txt",
            "https://github.com/kijai/ComfyUI-WanVideoWrapper/raw/main/requirements.txt",
            "https://github.com/chflame163/ComfyUI_LayerStyle/raw/main/requirements.txt",
            "https://github.com/chflame163/ComfyUI_LayerStyle_Advance/raw/main/requirements.txt",
            "https://github.com/shadowcz007/comfyui-mixlab-nodes/raw/main/requirements.txt",
            "https://github.com/yolain/ComfyUI-Easy-Use/raw/main/requirements.txt",
            "https://github.com/kijai/ComfyUI-IC-Light/raw/main/requirements.txt",
            "https://github.com/siliconflow/BizyAir/raw/master/requirements.txt",
            "https://github.com/lldacing/comfyui-easyapi-nodes/raw/master/requirements.txt",
            "https://github.com/kijai/ComfyUI-SUPIR/raw/main/requirements.txt",
            "https://github.com/kijai/ComfyUI-GIMM-VFI/raw/main/requirements.txt",
        ]
        
        # 获取并分析每个源的requirements
        for url in repo_requirements:
            source_name = url.split('/')[-3]  # 提取仓库名作为源名称
            requirements = self._fetch_requirements_from_url(url)
            if requirements:
                self.analyzer.add_requirements_source(source_name, requirements)
        
        # 添加额外的包
        additional_packages = [
            "torch==2.6.0",
            "torchvision",
            "torchaudio", 
            "xformers==0.0.29.post3",
            "opencv-python==4.8.0.76",
            "opencv-contrib-python==4.8.0.76",
            "sageattention==1.0.6",
            "bizyengine==1.2.4",
            "sortedcontainers==2.4.0",
            "pyhocon==0.3.59",
            "fal-client==0.6.0",
        ]
        self.analyzer.add_requirements_source("additional_packages", additional_packages)
        
        # 执行分析
        self.analyzer.detect_version_conflicts()
        self.analyzer.analyze_dependency_relationships()
        self.analyzer.identify_problematic_packages()
        
        # 设置排除的包
        self.excluded_packages = {
            'insightface', 'dlib', 'fairscale', 'pytorch-lightning',
            'voluptuous', 'gguf', 'nunchaku', 'imagesize', 'argostranslate',
            'litelama', 'evalidate', 'bizyengine', 'sortedcontainers',
            'pyhocon', 'fal-client'
        }
    
    def _fetch_requirements_from_url(self, url: str) -> List[str]:
        """从URL获取requirements"""
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=10) as response:
                content = response.read().decode('utf-8')
                return content.splitlines()
        except Exception as e:
            print(f"Warning: Failed to fetch {url}: {e}", file=sys.stderr)
            return []
    
    def resolve_conflicts(self):
        """解决版本冲突"""
        print("正在解决版本冲突...")
        
        # 按优先级处理包
        packages_by_priority = self._group_packages_by_priority()
        
        # 按优先级顺序处理
        for priority in [VersionPriority.CRITICAL, VersionPriority.HIGH, 
                        VersionPriority.MEDIUM, VersionPriority.LOW, VersionPriority.FLEXIBLE]:
            if priority in packages_by_priority:
                print(f"处理 {priority.name} 优先级包...")
                for package_name in packages_by_priority[priority]:
                    self._resolve_package_version(package_name)
        
        # 处理没有规则的包
        for package_name, requirements in self.analyzer.all_requirements.items():
            if package_name not in self.resolved_packages and package_name not in self.excluded_packages:
                self._resolve_package_version(package_name)
    
    def _group_packages_by_priority(self) -> Dict[VersionPriority, List[str]]:
        """按优先级分组包"""
        groups = defaultdict(list)
        
        for package_name in self.analyzer.all_requirements.keys():
            if package_name in self.excluded_packages:
                continue
                
            rule = self.resolver.get_rule(package_name)
            if rule:
                groups[rule.priority].append(package_name)
            else:
                groups[VersionPriority.FLEXIBLE].append(package_name)
        
        return groups
    
    def _resolve_package_version(self, package_name: str):
        """解析单个包的版本"""
        if package_name in self.resolved_packages or package_name in self.excluded_packages:
            return
        
        requirements = self.analyzer.all_requirements.get(package_name, [])
        if not requirements:
            return
        
        # 尝试使用版本解析器解决冲突
        resolved_version = self.resolver.resolve_version_conflict(package_name, requirements)
        
        if resolved_version:
            self.resolved_packages[package_name] = {
                'version': resolved_version,
                'source': 'resolved',
                'method': 'version_resolver'
            }
            print(f"  ✓ {package_name}: {resolved_version}")
        else:
            # 如果版本解析器无法解决，使用启发式方法
            version_result = self._heuristic_version_selection(package_name, requirements)
            if version_result:
                self.resolved_packages[package_name] = version_result
                print(f"  ✓ {package_name}: {version_result['version']} (启发式)")
            else:
                # 使用最高优先级源的版本
                fallback_result = self._fallback_version_selection(package_name, requirements)
                if fallback_result:
                    self.resolved_packages[package_name] = fallback_result
                    print(f"  ⚠ {package_name}: {fallback_result['version']} (回退)")
                else:
                    self.failed_packages.append(package_name)
                    print(f"  ✗ {package_name}: 无法解析版本")
    
    def _heuristic_version_selection(self, package_name: str, requirements: List[Dict]) -> Optional[Dict]:
        """启发式版本选择"""
        # 收集所有版本要求
        version_candidates = []
        
        for req_info in requirements:
            req = req_info['requirement']
            source = req_info['source']
            
            # 计算优先级分数
            if req.specifier:
                specifier_str = str(req.specifier)
                if '==' in specifier_str:
                    # 精确版本
                    exact_version = specifier_str.replace('==', '').strip()
                    score = self.resolver.get_version_priority_score(package_name, exact_version, source)
                    version_candidates.append({
                        'version': exact_version,
                        'score': score,
                        'source': source,
                        'type': 'exact'
                    })
                elif '>=' in specifier_str:
                    # 最小版本，使用推荐版本
                    min_version = specifier_str.replace('>=', '').strip()
                    rule = self.resolver.get_rule(package_name)
                    if rule and rule.preferred_version:
                        score = self.resolver.get_version_priority_score(package_name, rule.preferred_version, source)
                        version_candidates.append({
                            'version': rule.preferred_version,
                            'score': score,
                            'source': source,
                            'type': 'preferred'
                        })
        
        # 选择分数最高的版本
        if version_candidates:
            best_candidate = max(version_candidates, key=lambda x: x['score'])
            return {
                'version': best_candidate['version'],
                'source': best_candidate['source'],
                'method': 'heuristic',
                'score': best_candidate['score']
            }
        
        return None
    
    def _fallback_version_selection(self, package_name: str, requirements: List[Dict]) -> Optional[Dict]:
        """回退版本选择"""
        # 选择第一个有版本要求的requirement
        for req_info in requirements:
            req = req_info['requirement']
            if req.specifier:
                specifier_str = str(req.specifier)
                if '==' in specifier_str:
                    version_str = specifier_str.replace('==', '').strip()
                    return {
                        'version': version_str,
                        'source': req_info['source'],
                        'method': 'fallback'
                    }
        
        # 如果没有版本要求，使用最新版本（这里简化处理）
        return {
            'version': 'latest',
            'source': requirements[0]['source'],
            'method': 'fallback_latest'
        }
    
    def generate_installation_order(self):
        """生成安装顺序"""
        print("正在生成安装顺序...")
        
        # 按优先级排序
        priority_order = [
            VersionPriority.CRITICAL,
            VersionPriority.HIGH,
            VersionPriority.MEDIUM,
            VersionPriority.LOW,
            VersionPriority.FLEXIBLE
        ]
        
        ordered_packages = []
        
        for priority in priority_order:
            priority_packages = []
            for package_name, package_info in self.resolved_packages.items():
                rule = self.resolver.get_rule(package_name)
                if rule and rule.priority == priority:
                    priority_packages.append((package_name, package_info))
            
            # 在同一优先级内，按分数排序
            priority_packages.sort(key=lambda x: x[1].get('score', 0), reverse=True)
            ordered_packages.extend(priority_packages)
        
        # 添加没有规则的包
        for package_name, package_info in self.resolved_packages.items():
            rule = self.resolver.get_rule(package_name)
            if not rule:
                ordered_packages.append((package_name, package_info))
        
        self.installation_order = ordered_packages
    
    def generate_requirements_txt(self, filename: str = "optimized_requirements.txt"):
        """生成优化的requirements.txt"""
        print(f"正在生成 {filename}...")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 优化后的requirements.txt\n")
            f.write("# 由SmartInstaller生成\n\n")
            
            # 按优先级分组写入
            current_priority = None
            for package_name, package_info in self.installation_order:
                rule = self.resolver.get_rule(package_name)
                priority = rule.priority.name if rule else "FLEXIBLE"
                
                if priority != current_priority:
                    f.write(f"\n# {priority} 优先级包\n")
                    current_priority = priority
                
                version = package_info['version']
                if version == 'latest':
                    f.write(f"{package_name}\n")
                else:
                    f.write(f"{package_name}=={version}\n")
        
        print(f"requirements.txt已生成: {filename}")
    
    def generate_problematic_packages_list(self, filename: str = "problematic_packages.txt"):
        """生成问题包列表"""
        print(f"正在生成 {filename}...")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 问题包列表\n")
            f.write("# 这些包需要特殊安装策略\n\n")
            
            for package_name in sorted(self.excluded_packages):
                rule = self.resolver.get_rule(package_name)
                if rule and rule.preferred_version:
                    f.write(f"{package_name}=={rule.preferred_version}\n")
                else:
                    f.write(f"{package_name}\n")
        
        print(f"问题包列表已生成: {filename}")
    
    def generate_installation_script(self, filename: str = "smart_install.sh"):
        """生成安装脚本"""
        print(f"正在生成 {filename}...")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("#!/bin/bash\n")
            f.write("# 智能安装脚本\n")
            f.write("# 由SmartInstaller生成\n\n")
            f.write("set -e\n\n")
            
            f.write("echo \"开始智能安装...\"\n\n")
            
            # 升级pip
            f.write("echo \"升级pip...\"\n")
            f.write("python3.11 -m pip install --no-cache-dir --upgrade pip\n")
            f.write("python3.11 -m pip install --no-cache-dir wheel setuptools\n\n")
            
            # 安装关键包
            f.write("echo \"安装关键包...\"\n")
            critical_packages = [
                (name, info) for name, info in self.installation_order
                if self.resolver.get_rule(name) and self.resolver.get_rule(name).priority == VersionPriority.CRITICAL
            ]
            
            for package_name, package_info in critical_packages:
                version = package_info['version']
                if version == 'latest':
                    f.write(f"python3.11 -m pip install --no-cache-dir {package_name}\n")
                else:
                    f.write(f"python3.11 -m pip install --no-cache-dir {package_name}=={version}\n")
            
            f.write("\n")
            
            # 安装主要requirements
            f.write("echo \"安装主要requirements...\"\n")
            f.write("python3.11 -m pip install --no-cache-dir -r optimized_requirements.txt\n\n")
            
            # 安装问题包
            f.write("echo \"安装问题包...\"\n")
            f.write("python3.11 -m pip install --no-cache-dir -r problematic_packages.txt || echo \"部分问题包安装失败\"\n\n")
            
            f.write("echo \"智能安装完成!\"\n")
        
        # 设置执行权限
        import os
        os.chmod(filename, 0o755)
        print(f"安装脚本已生成: {filename}")
    
    def generate_summary_report(self, filename: str = "installation_summary.json"):
        """生成安装摘要报告"""
        print(f"正在生成 {filename}...")
        
        report = {
            'summary': {
                'total_packages_analyzed': len(self.analyzer.all_requirements),
                'resolved_packages': len(self.resolved_packages),
                'excluded_packages': len(self.excluded_packages),
                'failed_packages': len(self.failed_packages),
                'conflicts_detected': len(self.analyzer.conflicts)
            },
            'resolved_packages': self.resolved_packages,
            'excluded_packages': list(self.excluded_packages),
            'failed_packages': self.failed_packages,
            'installation_order': [
                {'package': name, 'version': info['version'], 'method': info['method']}
                for name, info in self.installation_order
            ],
            'conflicts': [
                {
                    'package': conflict['package'],
                    'conflict_type': conflict['conflict_type'],
                    'requirements': [
                        {
                            'source': req['source'],
                            'raw_string': req['raw_string']
                        } for req in conflict['requirements']
                    ]
                } for conflict in self.analyzer.conflicts
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"安装摘要报告已生成: {filename}")
    
    def print_summary(self):
        """打印摘要"""
        print("=" * 60)
        print("智能安装器摘要")
        print("=" * 60)
        print(f"总包数: {len(self.analyzer.all_requirements)}")
        print(f"已解析: {len(self.resolved_packages)}")
        print(f"已排除: {len(self.excluded_packages)}")
        print(f"失败: {len(self.failed_packages)}")
        print(f"冲突数: {len(self.analyzer.conflicts)}")
        
        if self.failed_packages:
            print(f"\n失败的包: {', '.join(self.failed_packages)}")
        
        print("=" * 60)
    
    def run(self):
        """运行智能安装器"""
        print("启动智能安装器...")
        
        # 步骤1：分析依赖
        self.analyze_dependencies()
        
        # 步骤2：解决冲突
        self.resolve_conflicts()
        
        # 步骤3：生成安装顺序
        self.generate_installation_order()
        
        # 步骤4：生成文件
        self.generate_requirements_txt()
        self.generate_problematic_packages_list()
        self.generate_installation_script()
        self.generate_summary_report()
        
        # 步骤5：打印摘要
        self.print_summary()
        
        print("智能安装器运行完成!")

def main():
    """主函数"""
    installer = SmartInstaller()
    installer.run()

if __name__ == "__main__":
    main() 
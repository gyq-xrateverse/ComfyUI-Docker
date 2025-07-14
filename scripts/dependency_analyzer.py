#!/usr/bin/env python3
"""
依赖冲突检测脚本
解析所有requirements.txt文件，检测版本冲突，分析依赖关系图，生成冲突报告
"""

import os
import re
import sys
import json
import urllib.request
import urllib.error
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional
import pkg_resources
from packaging import version
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet

class DependencyAnalyzer:
    def __init__(self):
        self.requirements_sources = []
        self.all_requirements = defaultdict(list)  # package_name -> list of requirements
        self.conflicts = []
        self.dependency_graph = defaultdict(set)
        self.problematic_packages = set()
        
    def add_requirements_source(self, source_name: str, requirements: List[str]):
        """添加requirements源"""
        self.requirements_sources.append(source_name)
        for req_str in requirements:
            req = self.parse_requirement(req_str)
            if req:
                package_name = req.name.lower()
                self.all_requirements[package_name].append({
                    'source': source_name,
                    'requirement': req,
                    'raw_string': req_str
                })
    
    def parse_requirement(self, req_str: str) -> Optional[Requirement]:
        """解析requirement字符串"""
        req_str = req_str.strip()
        if not req_str or req_str.startswith('#'):
            return None
        
        try:
            return Requirement(req_str)
        except Exception as e:
            print(f"Warning: Could not parse requirement: {req_str} - {e}", file=sys.stderr)
            return None
    
    def detect_version_conflicts(self):
        """检测版本冲突"""
        self.conflicts = []
        
        for package_name, requirements in self.all_requirements.items():
            if len(requirements) <= 1:
                continue
                
            # 检查是否存在冲突的版本要求
            conflict_found = False
            specifiers = []
            
            for req_info in requirements:
                req = req_info['requirement']
                if req.specifier:
                    specifiers.append((req.specifier, req_info['source']))
            
            # 检查specifiers是否互相冲突
            if len(specifiers) > 1:
                # 尝试找到一个版本同时满足所有specifiers
                try:
                    # 合并所有specifiers
                    combined_specifier = SpecifierSet()
                    for spec, source in specifiers:
                        combined_specifier = combined_specifier & spec
                    
                    # 如果合并后的specifier为空，说明存在冲突
                    if not combined_specifier:
                        conflict_found = True
                except Exception:
                    # 如果合并过程中出现异常，也认为存在冲突
                    conflict_found = True
            
            if conflict_found or len(set(str(req['requirement'].specifier) for req in requirements if req['requirement'].specifier)) > 1:
                self.conflicts.append({
                    'package': package_name,
                    'requirements': requirements,
                    'conflict_type': 'version_conflict'
                })
    
    def analyze_dependency_relationships(self):
        """分析依赖关系（简化版本，主要关注直接冲突）"""
        # 这里实现简化的依赖关系分析
        # 在实际应用中，可以使用更复杂的算法来分析传递依赖
        pass
    
    def identify_problematic_packages(self):
        """识别问题包"""
        # 基于历史经验和冲突分析识别问题包
        known_problematic = {
            'insightface', 'dlib', 'fairscale', 'pytorch-lightning',
            'voluptuous', 'gguf', 'nunchaku', 'imagesize', 'argostranslate',
            'litelama', 'evalidate', 'bizyengine', 'sortedcontainers',
            'pyhocon', 'fal-client'
        }
        
        # 添加已知问题包
        self.problematic_packages.update(known_problematic)
        
        # 添加有冲突的包
        for conflict in self.conflicts:
            self.problematic_packages.add(conflict['package'])
    
    def generate_conflict_report(self) -> Dict:
        """生成冲突报告"""
        report = {
            'summary': {
                'total_packages': len(self.all_requirements),
                'conflicted_packages': len(self.conflicts),
                'problematic_packages': len(self.problematic_packages),
                'sources_analyzed': len(self.requirements_sources)
            },
            'conflicts': [],
            'problematic_packages': list(self.problematic_packages),
            'package_sources': {},
            'recommendations': []
        }
        
        # 详细冲突信息
        for conflict in self.conflicts:
            conflict_detail = {
                'package': conflict['package'],
                'conflict_type': conflict['conflict_type'],
                'requirements': []
            }
            
            for req_info in conflict['requirements']:
                req = req_info['requirement']
                conflict_detail['requirements'].append({
                    'source': req_info['source'],
                    'specifier': str(req.specifier) if req.specifier else 'any',
                    'raw_string': req_info['raw_string']
                })
            
            report['conflicts'].append(conflict_detail)
        
        # 包来源统计
        for package_name, requirements in self.all_requirements.items():
            report['package_sources'][package_name] = [
                req['source'] for req in requirements
            ]
        
        # 生成建议
        report['recommendations'] = self.generate_recommendations()
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """生成解决建议"""
        recommendations = []
        
        if self.conflicts:
            recommendations.append(f"发现 {len(self.conflicts)} 个包版本冲突，建议使用版本解析器统一版本")
        
        if self.problematic_packages:
            recommendations.append(f"识别出 {len(self.problematic_packages)} 个问题包，建议使用特殊安装策略")
        
        # 针对具体冲突的建议
        for conflict in self.conflicts:
            package = conflict['package']
            sources = [req['source'] for req in conflict['requirements']]
            recommendations.append(f"包 '{package}' 在以下源中存在冲突: {', '.join(sources)}")
        
        return recommendations
    
    def save_report(self, filename: str = "dependency_analysis_report.json"):
        """保存报告到文件"""
        report = self.generate_conflict_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"依赖分析报告已保存到: {filename}")
        return report
    
    def print_summary(self):
        """打印分析摘要"""
        report = self.generate_conflict_report()
        
        print("=" * 60)
        print("依赖冲突分析摘要")
        print("=" * 60)
        print(f"总包数: {report['summary']['total_packages']}")
        print(f"冲突包数: {report['summary']['conflicted_packages']}")
        print(f"问题包数: {report['summary']['problematic_packages']}")
        print(f"分析源数: {report['summary']['sources_analyzed']}")
        print()
        
        if report['conflicts']:
            print("版本冲突详情:")
            for conflict in report['conflicts']:
                print(f"  - {conflict['package']}:")
                for req in conflict['requirements']:
                    print(f"    {req['source']}: {req['specifier']}")
            print()
        
        if report['recommendations']:
            print("建议:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("=" * 60)

def fetch_requirements_from_url(url: str) -> List[str]:
    """从URL获取requirements"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
            return content.splitlines()
    except Exception as e:
        print(f"Warning: Failed to fetch {url}: {e}", file=sys.stderr)
        return []

def main():
    """主函数"""
    # 创建分析器实例
    analyzer = DependencyAnalyzer()
    
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
        "https://github.com/aptx4869ntu/ComfyUI-Apt_Preset/raw/main/requirements.txt",
        "https://github.com/MinusZoneAI/ComfyUI-MingNodes/raw/main/requirements.txt",
        "https://github.com/kijai/ComfyUI-FluxTrainer/raw/main/requirements.txt",
        "https://github.com/Phando/ComfyUI-nunchaku/raw/main/requirements.txt",
        "https://github.com/AlexanderDzhoganov/comfyui-dream-video-batches/raw/main/requirements.txt",
        "https://github.com/kijai/ComfyUI-3D-Pack/raw/main/requirements.txt",
        "https://github.com/kijai/ComfyUI-SUPIR/raw/main/requirements.txt",
        "https://github.com/kijai/ComfyUI-GIMM-VFI/raw/main/requirements.txt",
    ]
    
    # 获取并分析每个源的requirements
    print("正在分析依赖关系...")
    for url in repo_requirements:
        source_name = url.split('/')[-3]  # 提取仓库名作为源名称
        requirements = fetch_requirements_from_url(url)
        if requirements:
            analyzer.add_requirements_source(source_name, requirements)
    
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
    analyzer.add_requirements_source("additional_packages", additional_packages)
    
    # 执行分析
    analyzer.detect_version_conflicts()
    analyzer.analyze_dependency_relationships()
    analyzer.identify_problematic_packages()
    
    # 输出结果
    analyzer.print_summary()
    report = analyzer.save_report()
    
    return analyzer, report

if __name__ == "__main__":
    analyzer, report = main() 
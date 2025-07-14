#!/usr/bin/env python3
"""
依赖关系验证机制
安装后验证包兼容性、检测运行时导入错误、生成验证报告
"""

import json
import sys
import subprocess
import importlib
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import traceback
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DependencyValidator:
    """依赖验证器"""
    
    def __init__(self):
        self.validation_results = {}
        self.import_errors = []
        self.compatibility_issues = []
        self.critical_packages = []
        self.optional_packages = []
        
        # 关键包列表（必须能够导入）
        self.critical_packages = [
            'torch', 'torchvision', 'torchaudio', 'xformers',
            'numpy', 'pillow', 'opencv-python', 'transformers',
            'diffusers', 'accelerate', 'safetensors'
        ]
        
        # 可选包列表（导入失败不影响主要功能）
        self.optional_packages = [
            'insightface', 'dlib', 'fairscale', 'pytorch-lightning',
            'voluptuous', 'gguf', 'nunchaku', 'imagesize', 'argostranslate',
            'litelama', 'evalidate', 'bizyengine', 'sortedcontainers',
            'pyhocon', 'fal-client'
        ]
    
    def validate_package_installation(self, package_name: str) -> Dict:
        """验证单个包的安装情况"""
        result = {
            'package': package_name,
            'installed': False,
            'version': None,
            'import_success': False,
            'import_error': None,
            'validation_time': None
        }
        
        start_time = time.time()
        
        try:
            # 检查包是否已安装
            result_pip = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result_pip.returncode == 0:
                result['installed'] = True
                # 解析版本信息
                for line in result_pip.stdout.split('\n'):
                    if line.startswith('Version:'):
                        result['version'] = line.split(':', 1)[1].strip()
                        break
            
            # 尝试导入包
            if result['installed']:
                try:
                    # 处理特殊包名映射
                    import_name = self._get_import_name(package_name)
                    module = importlib.import_module(import_name)
                    result['import_success'] = True
                    
                    # 获取版本信息（如果可用）
                    if hasattr(module, '__version__'):
                        result['module_version'] = module.__version__
                    
                except Exception as e:
                    result['import_error'] = str(e)
                    result['import_success'] = False
        
        except subprocess.TimeoutExpired:
            result['import_error'] = 'pip show timeout'
        except Exception as e:
            result['import_error'] = f'Validation error: {str(e)}'
        
        result['validation_time'] = time.time() - start_time
        return result
    
    def _get_import_name(self, package_name: str) -> str:
        """获取包的导入名称"""
        # 包名到导入名的映射
        import_mapping = {
            'opencv-python': 'cv2',
            'opencv-contrib-python': 'cv2',
            'opencv-python-headless': 'cv2',
            'pillow': 'PIL',
            'pyyaml': 'yaml',
            'scikit-learn': 'sklearn',
            'scikit-image': 'skimage',
            'pytorch-lightning': 'pytorch_lightning',
            'huggingface-hub': 'huggingface_hub',
            'google-generativeai': 'google.generativeai',
            'open-clip-torch': 'open_clip',
            'fal-client': 'fal_client',
            'colour-science': 'colour',
            'python-dateutil': 'dateutil',
            'matrix-client': 'matrix_client',
            'clip-interrogator': 'clip_interrogator',
            'requirements-parser': 'requirements',
            'psd-tools': 'psd_tools',
            'json-repair': 'json_repair',
            'blind-watermark': 'blind_watermark',
            'simple-lama-inpainting': 'simple_lama_inpainting',
            'transparent-background': 'transparent_background',
            'faster-whisper': 'faster_whisper',
            'cupy-cuda12x': 'cupy'
        }
        
        return import_mapping.get(package_name, package_name.replace('-', '_'))
    
    def validate_critical_packages(self) -> bool:
        """验证关键包"""
        logger.info("验证关键包...")
        
        critical_failures = []
        
        for package in self.critical_packages:
            result = self.validate_package_installation(package)
            self.validation_results[package] = result
            
            if not result['installed']:
                critical_failures.append(f"{package}: 未安装")
            elif not result['import_success']:
                critical_failures.append(f"{package}: 导入失败 - {result['import_error']}")
            else:
                logger.info(f"✓ {package}: 验证通过")
        
        if critical_failures:
            logger.error("关键包验证失败:")
            for failure in critical_failures:
                logger.error(f"  - {failure}")
            return False
        
        logger.info("所有关键包验证通过")
        return True
    
    def validate_optional_packages(self):
        """验证可选包"""
        logger.info("验证可选包...")
        
        optional_failures = []
        
        for package in self.optional_packages:
            result = self.validate_package_installation(package)
            self.validation_results[package] = result
            
            if not result['installed']:
                optional_failures.append(f"{package}: 未安装")
            elif not result['import_success']:
                optional_failures.append(f"{package}: 导入失败 - {result['import_error']}")
            else:
                logger.info(f"✓ {package}: 验证通过")
        
        if optional_failures:
            logger.warning("可选包验证问题:")
            for failure in optional_failures:
                logger.warning(f"  - {failure}")
        
        logger.info(f"可选包验证完成，{len(self.optional_packages) - len(optional_failures)}/{len(self.optional_packages)} 通过")
    
    def validate_from_requirements(self, requirements_file: str = "requirements.txt"):
        """从requirements.txt验证所有包"""
        logger.info(f"从 {requirements_file} 验证包...")
        
        if not Path(requirements_file).exists():
            logger.error(f"Requirements文件不存在: {requirements_file}")
            return False
        
        packages = []
        with open(requirements_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 提取包名（去掉版本要求）
                    package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0]
                    packages.append(package_name)
        
        logger.info(f"发现 {len(packages)} 个包需要验证")
        
        failed_packages = []
        for package in packages:
            result = self.validate_package_installation(package)
            self.validation_results[package] = result
            
            if not result['installed'] or not result['import_success']:
                failed_packages.append(package)
        
        success_rate = ((len(packages) - len(failed_packages)) / len(packages)) * 100
        logger.info(f"验证完成: {success_rate:.1f}% 成功率")
        
        return len(failed_packages) == 0
    
    def check_version_compatibility(self):
        """检查版本兼容性"""
        logger.info("检查版本兼容性...")
        
        compatibility_checks = [
            self._check_torch_compatibility,
            self._check_numpy_compatibility,
            self._check_opencv_compatibility,
            self._check_transformers_compatibility
        ]
        
        for check in compatibility_checks:
            try:
                check()
            except Exception as e:
                logger.error(f"兼容性检查失败: {e}")
                self.compatibility_issues.append(str(e))
    
    def _check_torch_compatibility(self):
        """检查PyTorch兼容性"""
        torch_result = self.validation_results.get('torch')
        if not torch_result or not torch_result['import_success']:
            return
        
        try:
            import torch
            
            # 检查CUDA支持
            cuda_available = torch.cuda.is_available()
            if not cuda_available:
                self.compatibility_issues.append("PyTorch: CUDA不可用")
            
            # 检查版本
            torch_version = torch.__version__
            if not torch_version.startswith('2.6'):
                self.compatibility_issues.append(f"PyTorch版本不匹配: 期望2.6.x, 实际{torch_version}")
            
            logger.info(f"PyTorch {torch_version}, CUDA: {cuda_available}")
            
        except Exception as e:
            self.compatibility_issues.append(f"PyTorch兼容性检查失败: {e}")
    
    def _check_numpy_compatibility(self):
        """检查NumPy兼容性"""
        numpy_result = self.validation_results.get('numpy')
        if not numpy_result or not numpy_result['import_success']:
            return
        
        try:
            import numpy as np
            
            numpy_version = np.__version__
            if not numpy_version.startswith('1.26'):
                self.compatibility_issues.append(f"NumPy版本不匹配: 期望1.26.x, 实际{numpy_version}")
            
            logger.info(f"NumPy {numpy_version}")
            
        except Exception as e:
            self.compatibility_issues.append(f"NumPy兼容性检查失败: {e}")
    
    def _check_opencv_compatibility(self):
        """检查OpenCV兼容性"""
        opencv_result = self.validation_results.get('opencv-python')
        if not opencv_result or not opencv_result['import_success']:
            return
        
        try:
            import cv2
            
            opencv_version = cv2.__version__
            if not opencv_version.startswith('4.8'):
                self.compatibility_issues.append(f"OpenCV版本不匹配: 期望4.8.x, 实际{opencv_version}")
            
            logger.info(f"OpenCV {opencv_version}")
            
        except Exception as e:
            self.compatibility_issues.append(f"OpenCV兼容性检查失败: {e}")
    
    def _check_transformers_compatibility(self):
        """检查Transformers兼容性"""
        transformers_result = self.validation_results.get('transformers')
        if not transformers_result or not transformers_result['import_success']:
            return
        
        try:
            import transformers
            
            transformers_version = transformers.__version__
            if not transformers_version.startswith('4.45'):
                self.compatibility_issues.append(f"Transformers版本不匹配: 期望4.45.x, 实际{transformers_version}")
            
            logger.info(f"Transformers {transformers_version}")
            
        except Exception as e:
            self.compatibility_issues.append(f"Transformers兼容性检查失败: {e}")
    
    def generate_validation_report(self, filename: str = "validation_report.json"):
        """生成验证报告"""
        logger.info(f"生成验证报告: {filename}")
        
        # 统计信息
        total_packages = len(self.validation_results)
        installed_packages = sum(1 for r in self.validation_results.values() if r['installed'])
        import_success_packages = sum(1 for r in self.validation_results.values() if r['import_success'])
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_packages': total_packages,
                'installed_packages': installed_packages,
                'import_success_packages': import_success_packages,
                'installation_rate': f"{(installed_packages / total_packages * 100):.1f}%" if total_packages > 0 else "0%",
                'import_success_rate': f"{(import_success_packages / total_packages * 100):.1f}%" if total_packages > 0 else "0%"
            },
            'critical_packages': {
                'total': len(self.critical_packages),
                'passed': sum(1 for pkg in self.critical_packages 
                             if self.validation_results.get(pkg, {}).get('import_success', False))
            },
            'optional_packages': {
                'total': len(self.optional_packages),
                'passed': sum(1 for pkg in self.optional_packages 
                             if self.validation_results.get(pkg, {}).get('import_success', False))
            },
            'compatibility_issues': self.compatibility_issues,
            'detailed_results': self.validation_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"验证报告已保存: {filename}")
        return report
    
    def print_summary(self):
        """打印验证摘要"""
        total_packages = len(self.validation_results)
        installed_packages = sum(1 for r in self.validation_results.values() if r['installed'])
        import_success_packages = sum(1 for r in self.validation_results.values() if r['import_success'])
        
        print("=" * 60)
        print("依赖验证摘要")
        print("=" * 60)
        print(f"总包数: {total_packages}")
        print(f"已安装: {installed_packages} ({(installed_packages / total_packages * 100):.1f}%)")
        print(f"导入成功: {import_success_packages} ({(import_success_packages / total_packages * 100):.1f}%)")
        
        critical_passed = sum(1 for pkg in self.critical_packages 
                             if self.validation_results.get(pkg, {}).get('import_success', False))
        print(f"关键包: {critical_passed}/{len(self.critical_packages)} 通过")
        
        optional_passed = sum(1 for pkg in self.optional_packages 
                             if self.validation_results.get(pkg, {}).get('import_success', False))
        print(f"可选包: {optional_passed}/{len(self.optional_packages)} 通过")
        
        if self.compatibility_issues:
            print(f"兼容性问题: {len(self.compatibility_issues)} 个")
            for issue in self.compatibility_issues:
                print(f"  - {issue}")
        
        print("=" * 60)
    
    def run_full_validation(self):
        """运行完整验证流程"""
        logger.info("开始完整的依赖验证...")
        
        # 验证关键包
        critical_success = self.validate_critical_packages()
        
        # 验证可选包
        self.validate_optional_packages()
        
        # 从requirements.txt验证所有包
        self.validate_from_requirements()
        
        # 检查版本兼容性
        self.check_version_compatibility()
        
        # 生成报告
        report = self.generate_validation_report()
        
        # 打印摘要
        self.print_summary()
        
        logger.info("依赖验证完成")
        return critical_success and len(self.compatibility_issues) == 0

def main():
    """主函数"""
    validator = DependencyValidator()
    success = validator.run_full_validation()
    
    if success:
        print("✅ 依赖验证成功!")
        sys.exit(0)
    else:
        print("❌ 依赖验证失败!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
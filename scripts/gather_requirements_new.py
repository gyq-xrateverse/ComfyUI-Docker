#!/usr/bin/env python3
"""
重构后的依赖收集脚本
集成新的依赖分析工具，简化安装逻辑，添加详细的日志输出
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加scripts目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_installer import SmartInstaller

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('dependency_gathering.log')
    ]
)

logger = logging.getLogger(__name__)

class EnhancedRequirementsGatherer:
    """增强的依赖收集器"""
    
    def __init__(self):
        self.installer = SmartInstaller()
        self.output_dir = Path(".")
        self.backup_dir = Path("backup")
        
    def backup_existing_files(self):
        """备份现有文件"""
        logger.info("备份现有文件...")
        
        self.backup_dir.mkdir(exist_ok=True)
        
        files_to_backup = [
            "requirements.txt",
            "scripts/problematic_requirements.txt"
        ]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                backup_path = self.backup_dir / f"{Path(file_path).name}.backup"
                os.rename(file_path, backup_path)
                logger.info(f"备份 {file_path} -> {backup_path}")
    
    def run_smart_installer(self):
        """运行智能安装器"""
        logger.info("运行智能安装器...")
        
        try:
            self.installer.run()
            logger.info("智能安装器运行成功")
            return True
        except Exception as e:
            logger.error(f"智能安装器运行失败: {e}")
            return False
    
    def integrate_results(self):
        """整合结果到现有文件结构"""
        logger.info("整合结果...")
        
        # 复制优化的requirements.txt
        if os.path.exists("optimized_requirements.txt"):
            os.rename("optimized_requirements.txt", "requirements.txt")
            logger.info("生成新的 requirements.txt")
        
        # 更新problematic_requirements.txt
        if os.path.exists("problematic_packages.txt"):
            target_path = "scripts/problematic_requirements.txt"
            os.rename("problematic_packages.txt", target_path)
            logger.info("更新 scripts/problematic_requirements.txt")
        
        # 生成安装统计报告
        self.generate_installation_stats()
    
    def generate_installation_stats(self):
        """生成安装统计报告"""
        logger.info("生成安装统计报告...")
        
        if not os.path.exists("installation_summary.json"):
            logger.warning("安装摘要文件不存在")
            return
        
        with open("installation_summary.json", 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        stats = {
            "timestamp": "2025-01-08",
            "total_packages": summary['summary']['total_packages_analyzed'],
            "resolved_packages": summary['summary']['resolved_packages'],
            "excluded_packages": summary['summary']['excluded_packages'],
            "failed_packages": summary['summary']['failed_packages'],
            "conflicts_resolved": summary['summary']['conflicts_detected'],
            "success_rate": f"{(summary['summary']['resolved_packages'] / summary['summary']['total_packages_analyzed'] * 100):.1f}%"
        }
        
        with open("dependency_stats.json", 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"统计报告: {stats['success_rate']} 成功率")
        logger.info(f"解决了 {stats['conflicts_resolved']} 个冲突")
    
    def validate_results(self):
        """验证结果"""
        logger.info("验证结果...")
        
        required_files = [
            "requirements.txt",
            "scripts/problematic_requirements.txt",
            "smart_install.sh"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"缺少文件: {missing_files}")
            return False
        
        # 验证requirements.txt格式
        try:
            with open("requirements.txt", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                package_count = len([line for line in lines if line.strip() and not line.startswith('#')])
                logger.info(f"requirements.txt 包含 {package_count} 个包")
        except Exception as e:
            logger.error(f"验证requirements.txt失败: {e}")
            return False
        
        logger.info("验证通过")
        return True
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        logger.info("清理临时文件...")
        
        temp_files = [
            "dependency_analysis_report.json",
            "version_rules.json",
            "installation_summary.json"
        ]
        
        for file_path in temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"删除临时文件: {file_path}")
    
    def run(self):
        """运行完整的依赖收集流程"""
        logger.info("开始增强的依赖收集流程...")
        
        try:
            # 步骤1: 备份现有文件
            self.backup_existing_files()
            
            # 步骤2: 运行智能安装器
            if not self.run_smart_installer():
                logger.error("智能安装器运行失败，流程终止")
                return False
            
            # 步骤3: 整合结果
            self.integrate_results()
            
            # 步骤4: 验证结果
            if not self.validate_results():
                logger.error("结果验证失败")
                return False
            
            # 步骤5: 清理临时文件
            self.cleanup_temp_files()
            
            logger.info("增强的依赖收集流程完成!")
            return True
            
        except Exception as e:
            logger.error(f"流程执行失败: {e}")
            return False

def main():
    """主函数"""
    gatherer = EnhancedRequirementsGatherer()
    success = gatherer.run()
    
    if success:
        print("✅ 依赖收集成功完成!")
        print("📁 生成的文件:")
        print("   - requirements.txt (优化后的依赖列表)")
        print("   - scripts/problematic_requirements.txt (问题包列表)")
        print("   - smart_install.sh (智能安装脚本)")
        print("   - dependency_stats.json (统计报告)")
        print("   - dependency_gathering.log (详细日志)")
        sys.exit(0)
    else:
        print("❌ 依赖收集失败!")
        print("📋 请查看 dependency_gathering.log 获取详细信息")
        sys.exit(1)

if __name__ == "__main__":
    main() 
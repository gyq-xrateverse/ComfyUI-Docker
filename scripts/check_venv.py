#!/usr/bin/env python3
"""
虚拟环境状态检查脚本
用于验证虚拟环境是否正确配置和可用
"""

import os
import sys
import subprocess
import json

def check_venv_status():
    """检查虚拟环境状态"""
    status = {
        "venv_exists": False,
        "venv_functional": False,
        "python_path": None,
        "pip_path": None,
        "setuptools_version": None,
        "packages_count": 0,
        "errors": []
    }
    
    # 检查虚拟环境目录
    venv_path = "/venv"
    if os.path.exists(venv_path):
        status["venv_exists"] = True
        print(f"✅ 虚拟环境目录存在: {venv_path}")
        
        # 检查关键文件
        python_bin = os.path.join(venv_path, "bin", "python")
        pip_bin = os.path.join(venv_path, "bin", "pip")
        
        if os.path.exists(python_bin) and os.path.exists(pip_bin):
            status["python_path"] = python_bin
            status["pip_path"] = pip_bin
            print(f"✅ Python可执行文件: {python_bin}")
            print(f"✅ Pip可执行文件: {pip_bin}")
            
            # 测试Python功能
            try:
                result = subprocess.run([python_bin, "--version"], 
                                      capture_output=True, text=True, check=True)
                print(f"✅ Python版本: {result.stdout.strip()}")
                
                # 测试虚拟环境激活
                result = subprocess.run([python_bin, "-c", "import sys; print(sys.prefix)"], 
                                      capture_output=True, text=True, check=True)
                if venv_path in result.stdout:
                    status["venv_functional"] = True
                    print(f"✅ 虚拟环境功能正常: {result.stdout.strip()}")
                else:
                    status["errors"].append("虚拟环境未正确激活")
                    print(f"❌ 虚拟环境未正确激活: {result.stdout.strip()}")
                    
            except subprocess.CalledProcessError as e:
                status["errors"].append(f"Python执行失败: {e}")
                print(f"❌ Python执行失败: {e}")
            
            # 检查pip和setuptools
            try:
                result = subprocess.run([pip_bin, "--version"], 
                                      capture_output=True, text=True, check=True)
                print(f"✅ Pip版本: {result.stdout.strip()}")
                
                # 检查setuptools版本
                result = subprocess.run([pip_bin, "show", "setuptools"], 
                                      capture_output=True, text=True, check=True)
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        status["setuptools_version"] = line.split(':', 1)[1].strip()
                        print(f"✅ Setuptools版本: {status['setuptools_version']}")
                        break
                
                # 统计已安装包数量
                result = subprocess.run([pip_bin, "list", "--format=json"], 
                                      capture_output=True, text=True, check=True)
                packages = json.loads(result.stdout)
                status["packages_count"] = len(packages)
                print(f"✅ 已安装包数量: {status['packages_count']}")
                
            except subprocess.CalledProcessError as e:
                status["errors"].append(f"Pip检查失败: {e}")
                print(f"❌ Pip检查失败: {e}")
        else:
            status["errors"].append("Python或pip可执行文件不存在")
            print("❌ Python或pip可执行文件不存在")
    else:
        status["errors"].append("虚拟环境目录不存在")
        print(f"❌ 虚拟环境目录不存在: {venv_path}")
    
    return status

def main():
    """主函数"""
    print("🔍 检查虚拟环境状态...")
    print("=" * 50)
    
    status = check_venv_status()
    
    print("\n" + "=" * 50)
    print("📊 检查结果摘要:")
    print(f"  虚拟环境存在: {'✅' if status['venv_exists'] else '❌'}")
    print(f"  虚拟环境功能: {'✅' if status['venv_functional'] else '❌'}")
    print(f"  已安装包数量: {status['packages_count']}")
    
    if status["errors"]:
        print(f"  错误数量: {len(status['errors'])}")
        for i, error in enumerate(status['errors'], 1):
            print(f"    {i}. {error}")
    
    # 返回适当的退出码
    if status["venv_functional"]:
        print("\n🎉 虚拟环境状态良好！")
        return 0
    else:
        print("\n❌ 虚拟环境存在问题！")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
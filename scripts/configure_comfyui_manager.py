#!/usr/bin/env python3
"""
ComfyUI-Manager配置脚本
用于解决国内服务器网络超时问题
"""

import os
import json
import sys

def configure_manager():
    """配置ComfyUI-Manager"""
    manager_path = "/app/custom_nodes/ComfyUI-Manager"
    
    if not os.path.exists(manager_path):
        print("⚠️ ComfyUI-Manager未找到，跳过配置")
        return
    
    print("🔧 配置ComfyUI-Manager...")
    
    # 创建配置文件
    config_path = os.path.join(manager_path, "config.ini")
    
    config_content = """
[DEFAULT]
# 增加超时时间
timeout = 120

# 禁用自动获取
auto_fetch = false

# 使用本地缓存
use_local_cache = true

[network]
# 连接超时
connect_timeout = 60
read_timeout = 120

# 重试次数
max_retries = 3
"""
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"✅ 配置文件已创建: {config_path}")
    except Exception as e:
        print(f"❌ 配置文件创建失败: {e}")
    
    # 修改manager_util.py增加超时时间
    util_path = os.path.join(manager_path, "glob", "manager_util.py")
    if os.path.exists(util_path):
        try:
            with open(util_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 增加超时时间
            content = content.replace(
                "timeout=aiohttp.ClientTimeout(total=10)",
                "timeout=aiohttp.ClientTimeout(total=120)"
            )
            content = content.replace(
                "timeout=10",
                "timeout=120"
            )
            
            with open(util_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ manager_util.py超时时间已增加")
        except Exception as e:
            print(f"⚠️ 修改manager_util.py失败: {e}")
    
    # 创建禁用网络获取的标记文件
    disable_fetch_file = os.path.join(manager_path, ".disable_fetch")
    try:
        with open(disable_fetch_file, 'w') as f:
            f.write("# 禁用网络获取以避免超时\n")
        print("✅ 已创建禁用网络获取标记")
    except Exception as e:
        print(f"⚠️ 创建禁用标记失败: {e}")

def main():
    """主函数"""
    print("🔧 配置ComfyUI-Manager网络设置...")
    configure_manager()
    print("🎉 ComfyUI-Manager配置完成！")

if __name__ == "__main__":
    main() 
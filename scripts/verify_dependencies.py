#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
一个在容器启动时运行的脚本，用于验证并强制安装核心Python依赖项。

该脚本确保无论自定义节点如何修改环境，
项目的核心依赖（如torch, torchvision）始终保持在预期的固定版本，
从而防止因版本冲突导致的运行时错误。
"""

import sys
import subprocess
import logging
import os
try:
    from importlib import metadata as importlib_metadata
except ImportError:
    # 兼容 Python < 3.8
    import importlib_metadata

# --- 基本设置 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    stream=sys.stdout
)
LOGGER = logging.getLogger(__name__)

# --- 配置 ---
# 这些是项目的核心依赖，必须固定到特定版本。
# 此脚本将在每次容器启动时强制安装这些版本，以覆盖任何由自定义节点引起的不兼容更改。

# "numpy": "1.26.4"

# PINNED_PACKAGES = {
#     "torch": "2.5.1",
#     "torchvision": "0.20.1",
#     "torchaudio": "2.5.1",
#     "xformers": "0.0.29.post1"
# }

PINNED_PACKAGES = {
    "torch": "2.6.0",
    "torchvision": "0.21.0",
    "torchaudio": "2.6.0",
    "xformers": "0.0.29.post3",
    "numpy": "1.26.4"
}

# PyPI 镜像源
PIP_INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"

# PyTorch专用下载源
TORCH_INDEX_URL = "https://download.pytorch.org/whl/cu121"

def run_pip(args):
    """运行pip命令并处理输出。"""
    command = [sys.executable, "-m", "pip"] + args
    try:
        # 使用subprocess.run而不是直接打印，以更好地控制日志记录
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        LOGGER.info(result.stdout)
        if result.stderr:
            LOGGER.warning(result.stderr)
    except subprocess.CalledProcessError as e:
        LOGGER.error(f"执行失败: {' '.join(command)}")
        LOGGER.error(f"Pip stdout:\n{e.stdout}")
        LOGGER.error(f"Pip stderr:\n{e.stderr}")
        raise

def verify_and_install():
    """验证并强制安装所有固定版本的包。"""
    LOGGER.info("开始核心依赖验证和安装...")

    force_reinstall = os.environ.get('FORCE_REINSTALL_CORE_DEPS', 'false').lower() in ('true', '1', 'yes')
    if force_reinstall:
        LOGGER.warning("环境变量 FORCE_REINSTALL_CORE_DEPS 已设置，将强制重新安装所有核心依赖。")

    for name, version in PINNED_PACKAGES.items():
        should_install = False
        reason = ""

        if force_reinstall:
            should_install = True
            reason = "接收到强制重新安装指令。"
        else:
            try:
                installed_version = importlib_metadata.version(name)
                if installed_version != version:
                    should_install = True
                    reason = f"版本不匹配 (已安装: {installed_version}, 需要: {version})。"
                else:
                    LOGGER.info(f"✓ {name}=={version} 版本正确，无需操作。")
            except importlib_metadata.PackageNotFoundError:
                should_install = True
                reason = "包未找到。"
        
        if should_install:
            package_spec = f"{name}=={version}"
            LOGGER.info(f"正在安装/更新 {package_spec} 因为: {reason}")
            # 使用--force-reinstall确保即使已安装正确版本也会重新链接，以修复潜在的损坏
            # 使用--no-deps防止在重新安装核心包时牵连到其他包
            install_args = ["install", "--force-reinstall", "--no-dependencies", package_spec]

            # 对torch相关包使用专用源，其他包使用配置的镜像源
            if name.lower() in ["torch", "torchvision", "torchaudio"]:
                install_args.extend(["--index-url", TORCH_INDEX_URL, "--extra-index-url", PIP_INDEX_URL])
            else:
                install_args.extend(["--index-url", PIP_INDEX_URL])

            try:
                run_pip(install_args)
                LOGGER.info(f"✓ {package_spec} 已成功安装/验证。")
            except Exception as e:
                LOGGER.error(f"✗ 安装 {package_spec} 失败。错误: {e}")
                # 即使有一个失败，也继续尝试安装其他的
                continue

    LOGGER.info("核心依赖验证和安装完成。")

if __name__ == "__main__":
    verify_and_install() 
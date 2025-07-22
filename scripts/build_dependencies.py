#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
一个统一的脚本，用于管理和安装ComfyUI项目的所有Python依赖项。

该脚本整合了以下逻辑：
1. 从所有源获取依赖需求。
2. 使用直接的、基于优先级的策略解决版本冲突。
3. 在一个统一的过程中安装所有软件包。

这种方法简化了Dockerfile并集中了依赖项管理，
使构建过程更加透明和可维护。
"""

import sys
import subprocess
import logging
import urllib.request
from collections import defaultdict
from packaging.requirements import Requirement
from packaging.version import parse as parse_version
import time

# --- 基本设置 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    stream=sys.stdout
)
LOGGER = logging.getLogger(__name__)

# --- 配置 ---

# 将从这些源收集所有需求
REQUIREMENTS_SOURCES = [
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
    # 新增的自定义节点 requirements
    "https://github.com/cardenluo/ComfyUI-Apt_Preset/raw/main/requirements.txt",
    "https://github.com/MinusZoneAI/ComfyUI-MingNodes/raw/main/requirements.txt",
    "https://github.com/kijai/ComfyUI-FluxTrainer/raw/main/requirements.txt",
    "https://github.com/Phando/ComfyUI-nunchaku/raw/main/requirements.txt",
    "https://github.com/AlexanderDzhoganov/comfyui-dream-video-batches/raw/main/requirements.txt",
    "https://github.com/kijai/ComfyUI-3D-Pack/raw/main/requirements.txt",
    "https://github.com/kijai/ComfyUI-SUPIR/raw/main/requirements.txt",
    "https://github.com/kijai/ComfyUI-GIMM-VFI/raw/main/requirements.txt",
    "https://github.com/EvilBT/ComfyUI_SLK_joy_caption_two/raw/main/requirements.txt",
    "https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper/raw/main/requirements.txt"
]

# 基础软件包，必须固定到特定版本。
# 它们在解决阶段被注入。
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
    "xformers": "0.0.29.post3"
}

# PyTorch专用下载源
TORCH_INDEX_URL = "https://download.pytorch.org/whl/cu121"

class DependencyInstaller:
    """协调依赖项的获取、解决和安装。"""

    def __init__(self):
        """初始化依赖安装器。"""
        self.requirements = defaultdict(list)
        self.resolved_versions = {}

    def run(self):
        """执行整个安装流程。"""
        LOGGER.info("开始统一的依赖安装流程...")
        self._install_build_tools()
        self._gather_requirements()
        self._resolve_versions()
        self._install_packages()
        LOGGER.info("统一的依赖安装流程完成。")

    def _install_build_tools(self):
        """升级pip并安装必要的构建工具。"""
        LOGGER.info("正在升级pip并安装setuptools/wheel...")
        self._run_pip(["install", "--upgrade", "pip"])
        self._run_pip(["install", "setuptools<68", "wheel<0.41"])

    def _gather_requirements(self):
        """从配置的源获取所有依赖需求。"""
        LOGGER.info(f"从 {len(REQUIREMENTS_SOURCES)} 个源收集依赖...")
        for url in REQUIREMENTS_SOURCES:
            try:
                with urllib.request.urlopen(url, timeout=20) as response:
                    content = response.read().decode('utf-8')
                    for line in content.splitlines():
                        req_str = line.strip()
                        if not req_str or req_str.startswith('#') or req_str.startswith('-'):
                            continue
                        try:
                            req = Requirement(req_str)
                            self.requirements[req.name.lower()].append(req)
                        except Exception as e:
                            LOGGER.warning(f"无法解析依赖: '{req_str}'. 错误: {e}")
            except Exception as e:
                LOGGER.error(f"获取失败 {url}. 错误: {e}")
        
        LOGGER.info(f"共收集到 {len(self.requirements)} 个唯一的软件包。")

    def _resolve_versions(self):
        """解决版本冲突，并为每个包确定最终版本。"""
        LOGGER.info("正在解决软件包版本...")

        # 将固定版本的包注入到需求列表中
        for name, version in PINNED_PACKAGES.items():
            self.requirements[name.lower()].append(Requirement(f"{name}=={version}"))
            
        for name, reqs in self.requirements.items():
            pinned_versions = set()
            for req in reqs:
                # 寻找'=='指定的版本，因为它们是不可协商的
                for spec in req.specifier:
                    if spec.operator == '==':
                        pinned_versions.add(spec.version)
            
            if len(pinned_versions) > 1:
                # 硬性冲突：请求了多个不同的'=='版本。
                # 策略：选择最高的版本并警告用户。
                highest_version = sorted(list(pinned_versions), key=parse_version, reverse=True)[0]
                LOGGER.warning(
                    f"'{name}'存在冲突: 请求了多个固定版本 {pinned_versions}。 "
                    f"已解决为最高版本: {highest_version}。"
                )
                self.resolved_versions[name] = highest_version
            elif len(pinned_versions) == 1:
                # 简单情况：只固定了一个版本。
                self.resolved_versions[name] = pinned_versions.pop()
            else:
                # 未找到固定版本。让pip自行决定版本。
                # 将来可以在这里添加更复杂的逻辑（例如，尊重'>='）。
                self.resolved_versions[name] = None
        
        LOGGER.info(f"已为 {len(self.resolved_versions)} 个软件包解决版本。")

    def _install_packages(self):
        """使用解析后的版本安装所有软件包。"""
        LOGGER.info(f"正在安装所有 {len(self.resolved_versions)} 个解析后的软件包...")
        
        # 排序以确保torch相关的包被正确处理（如果需要），
        # 尽管在版本固定的情况下安装顺序不应有影响。
        sorted_packages = sorted(self.resolved_versions.keys())

        for name in sorted_packages:
            version = self.resolved_versions[name]
            install_args = []

            # 构建软件包字符串（例如，'numpy==1.26.4'或'requests'）
            package_spec = f"{name}=={version}" if version else name
            
            # 对torch的下载源进行特殊处理
            if name.lower() in ["torch", "torchvision", "torchaudio"]:
                install_args.extend(["--index-url", TORCH_INDEX_URL, "--extra-index-url", "https://pypi.org/simple"])
            
            try:
                self._run_pip(["install", package_spec] + install_args)
            except subprocess.CalledProcessError:
                LOGGER.error(f"安装 {package_spec} 失败。构建可能会失败。")

    def _run_pip(self, args, retries=3, backoff_factor=2):
        """使用通用选项、重试和错误处理来运行pip命令。"""
        command = [sys.executable, "-m", "pip", "--no-cache-dir"] + args
        LOGGER.info(f"执行: {' '.join(command)}")
        
        for attempt in range(retries):
            try:
                subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr)
                return  # 成功，退出函数
            except subprocess.CalledProcessError as e:
                if attempt + 1 == retries:
                    LOGGER.error(f"命令在 {retries} 次尝试后最终失败。")
                    raise e
                
                sleep_time = backoff_factor * (2 ** attempt)
                LOGGER.warning(
                    f"命令失败 (尝试 {attempt + 1}/{retries})。将在 {sleep_time} 秒后重试..."
                )
                time.sleep(sleep_time)


if __name__ == "__main__":
    installer = DependencyInstaller()
    installer.run() 
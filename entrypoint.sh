#!/bin/bash
set -e

# 确保scripts目录存在
mkdir -p /app/scripts

# 设置外部数据目录
if [ -f "/app/scripts/setup_external_data.sh" ]; then
    chmod +x /app/scripts/setup_external_data.sh
    /app/scripts/setup_external_data.sh
else
    echo "警告: 外部数据目录设置脚本不存在，跳过外部数据目录设置"
fi

# 设置关键目录权限
if [ -f "/app/scripts/set_permissions.sh" ]; then
    /app/scripts/set_permissions.sh
else
    echo "警告: 权限设置脚本不存在，跳过权限设置"
fi

# 如果请求，更新ComfyUI和自定义节点
if [ "${UPDATE_REPOSITORIES:-false}" = "true" ]; then
    echo "更新ComfyUI..."
    cd /app
    git pull

    echo "更新自定义节点..."
    for dir in /app/custom_nodes/*; do
        if [ -d "$dir/.git" ]; then
            echo "更新 $(basename $dir)..."
            cd "$dir"
            git pull
        fi
    done
fi

# 如果模型不存在或强制下载，则下载模型
download_model() {
    local model_url="$1"
    local output_dir="$2"
    local filename=$(basename "$model_url")
    
    if [ ! -f "$output_dir/$filename" ] || [ "${FORCE_DOWNLOAD_MODELS:-false}" = "true" ]; then
        echo "下载 $filename 到 $output_dir..."
        mkdir -p "$output_dir"
        wget -q --show-progress -O "$output_dir/$filename" "$model_url"
    else
        echo "模型 $filename 已存在，跳过下载。"
    fi
}

# 如果请求，下载示例模型
if [ "${DOWNLOAD_EXAMPLE_MODELS:-false}" = "true" ]; then
    # SD 1.5 模型
    download_model "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" "/app/models/checkpoints"
    
    # 超分辨率模型
    download_model "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth" "/app/models/upscale_models"
    
    # ControlNet 模型
    download_model "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth" "/app/models/controlnet"
    download_model "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth" "/app/models/controlnet"
fi

# 在运行时检查并安装缺失的关键包
echo "检查缺失的关键包..."
missing_packages=""

# 检查每个关键包
python3.11 -c "import yaml" 2>/dev/null || missing_packages="$missing_packages PyYAML"
python3.11 -c "import sortedcontainers" 2>/dev/null || missing_packages="$missing_packages sortedcontainers==2.4.0"
python3.11 -c "import pyhocon" 2>/dev/null || missing_packages="$missing_packages pyhocon==0.3.59"
python3.11 -c "import imagesize" 2>/dev/null || missing_packages="$missing_packages imagesize==1.4.1"
python3.11 -c "import evalidate" 2>/dev/null || missing_packages="$missing_packages evalidate==2.0.5"
python3.11 -c "import litelama" 2>/dev/null || missing_packages="$missing_packages litelama==0.1.7"
python3.11 -c "import pytorch_lightning" 2>/dev/null || missing_packages="$missing_packages pytorch-lightning==2.5.2"
python3.11 -c "import nunchaku" 2>/dev/null || missing_packages="$missing_packages nunchaku==0.15.4"

# 如果有缺失的包，则安装
if [ -n "$missing_packages" ]; then
    echo "安装缺失的包: $missing_packages"
    for package in $missing_packages; do
        echo "安装 $package..."
        python3.11 -m pip install --no-cache-dir "$package" || echo "安装 $package 失败"
    done
else
    echo "所有关键包已安装。"
fi

# 如果requirements文件不存在，则生成
if [ ! -f "/app/requirements.txt" ] || [ "${REGENERATE_REQUIREMENTS:-false}" = "true" ]; then
    echo "生成requirements.txt..."
    python3.11 /app/scripts/gather_requirements.py
    python3.11 -m pip install -r /app/requirements.txt
fi

# 如果存在用户提供的初始化脚本，则运行
if [ -f "/app/custom_init.sh" ]; then
    echo "运行自定义初始化脚本..."
    chmod +x /app/custom_init.sh
    /app/custom_init.sh
fi

# 设置所有文件的所有权为运行用户
if [ "${FIX_PERMISSIONS:-true}" = "true" ]; then
    echo "设置正确的权限..."
    find /app -not -user $(id -u) -exec chown -R $(id -u):$(id -g) {} \; 2>/dev/null || true
fi

echo "==================================================="
echo "ComfyUI正在启动。服务器将在以下地址可用:"
echo "http://localhost:8188 (如果端口8188已暴露)"
echo "==================================================="

# 执行CMD
exec "$@" 
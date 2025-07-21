#!/bin/bash
set -e

# 确保scripts目录存在
mkdir -p /app/scripts

# 设置外部数据目录
if [ -f "/app/scripts/setup_external_data.sh" ]; then
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
# if [ "${DOWNLOAD_EXAMPLE_MODELS:-false}" = "true" ]; then
#     # SD 1.5 模型
#     download_model "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" "/app/models/checkpoints"
    
#     # 超分辨率模型
#     download_model "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth" "/app/models/upscale_models"
    
#     # ControlNet 模型
#     download_model "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth" "/app/models/controlnet"
#     download_model "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth" "/app/models/controlnet"
# fi

# 如果存在用户提供的初始化脚本，则运行
if [ -f "/app/custom_init.sh" ]; then
    echo "运行自定义初始化脚本..."
    chmod +x /app/custom_init.sh
    /app/custom_init.sh
fi

# 确保关键目录存在
echo "============================================"
echo "确保关键目录存在..."
echo "当前用户: $(whoami), UID: $(id -u), GID: $(id -g)"

# 确保关键目录存在
mkdir -p /app/user /app/output /app/temp
echo "关键目录已确保存在"

# 设置custom_nodes中可执行文件的权限
echo "设置custom_nodes中可执行文件的执行权限..."
# 设置所有shell脚本权限
find /app/custom_nodes -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
# 设置go二进制文件权限
find /app/custom_nodes -type f -name "go" -exec chmod +x {} \; 2>/dev/null || true
# 设置Windows可执行文件权限
find /app/custom_nodes -type f -name "*.exe" -exec chmod +x {} \; 2>/dev/null || true
# 设置binary文件权限
find /app/custom_nodes -type f -name "*.bin" -exec chmod +x {} \; 2>/dev/null || true
# 设置bin目录下所有文件权限
find /app/custom_nodes -path "*/bin/*" -type f -exec chmod +x {} \; 2>/dev/null || true
# 设置go目录下所有文件权限
find /app/custom_nodes -path "*/go/*" -type f -exec chmod +x {} \; 2>/dev/null || true
# 设置可能的其他可执行文件
find /app/custom_nodes -type f \( -name "*server*" -o -name "*daemon*" -o -name "*Service*" \) -exec chmod +x {} \; 2>/dev/null || true
# 为所有custom_nodes子目录设置递归权限（确保目录权限正确）
find /app/custom_nodes -type d -exec chmod 755 {} \; 2>/dev/null || true

echo "============================================"
echo "ComfyUI启动前检查..."

# 测试能否在 /app/user 中创建目录
echo "测试用户目录写权限..."
test_dir="/app/user/test_$(date +%s)"
if mkdir -p "$test_dir" 2>/dev/null; then
    echo "✓ 用户目录写权限正常"
    rmdir "$test_dir" 2>/dev/null || true
else
    echo "✗ 用户目录写权限异常"
fi

echo "==================================================="
echo "ComfyUI正在启动。服务器将在以下地址可用:"
echo "http://localhost:10001 (如果端口10001已暴露)"
echo "==================================================="

# 验证并强制安装核心依赖项
if [ -f "/app/scripts/verify_dependencies.py" ]; then
    echo "==================================================="
    echo "正在验证核心依赖项... 这可能需要一些时间。"
    echo "此步骤可确保关键软件包（如 PyTorch）的版本正确，"
    echo "以防止与自定义节点的依赖项发生冲突。"
    echo "==================================================="
    python /app/scripts/verify_dependencies.py
    echo "==================================================="
    echo "核心依赖项验证完成。"
    echo "==================================================="
else
    echo "警告: 核心依赖项验证脚本 'verify_dependencies.py' 未找到。跳过验证。"
fi

# 执行CMD
exec "$@" 
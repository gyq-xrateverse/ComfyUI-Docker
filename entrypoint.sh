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
if [ "${DOWNLOAD_EXAMPLE_MODELS:-false}" = "true" ]; then
    # SD 1.5 模型
    download_model "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" "/app/models/checkpoints"
    
    # 超分辨率模型
    download_model "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth" "/app/models/upscale_models"
    
    # ControlNet 模型
    download_model "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth" "/app/models/controlnet"
    download_model "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth" "/app/models/controlnet"
fi

# 检查缺失的关键包
echo "检查缺失的关键包..."
missing_packages=()

# 检查关键包
packages=("insightface" "toolz" "plyfile" "deep_translator")
for package in "${packages[@]}"; do
    if ! python3.11 -c "import $package" 2>/dev/null; then
        missing_packages+=("$package")
    fi
done

# 安装缺失的包
if [ ${#missing_packages[@]} -gt 0 ]; then
    echo "发现缺失的包: ${missing_packages[*]}"
    echo "配置pip使用清华源..."
    python3.11 -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
    python3.11 -m pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
    
    for package in "${missing_packages[@]}"; do
        echo "正在安装 $package..."
        case $package in
            "insightface")
                python3.11 -m pip install --no-cache-dir insightface==0.7.3 -i https://pypi.tuna.tsinghua.edu.cn/simple || echo "安装 $package 失败，将继续运行"
                ;;
            "toolz")
                python3.11 -m pip install --no-cache-dir toolz -i https://pypi.tuna.tsinghua.edu.cn/simple || echo "安装 $package 失败，将继续运行"
                ;;
            "plyfile")
                python3.11 -m pip install --no-cache-dir plyfile -i https://pypi.tuna.tsinghua.edu.cn/simple || echo "安装 $package 失败，将继续运行"
                ;;
            "deep_translator")
                python3.11 -m pip install --no-cache-dir deep_translator -i https://pypi.tuna.tsinghua.edu.cn/simple || echo "安装 $package 失败，将继续运行"
                ;;
            *)
                python3.11 -m pip install --no-cache-dir "$package" -i https://pypi.tuna.tsinghua.edu.cn/simple || echo "安装 $package 失败，将继续运行"
                ;;
        esac
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

# 设置正确的权限
echo "============================================"
echo "开始权限诊断和修复..."
echo "当前用户: $(whoami), UID: $(id -u), GID: $(id -g)"

# 检查当前/app目录权限
echo "检查 /app 目录权限:"
ls -la /app/ | head -10

# 检查 /app/user 目录状态
echo "检查 /app/user 目录状态:"
if [ -d "/app/user" ]; then
    ls -la /app/user/ 2>/dev/null || echo "/app/user 目录无法访问"
else
    echo "/app/user 目录不存在，将创建"
fi

# 强制设置整个/app目录权限
echo "强制设置 /app 目录权限..."
sudo chown -R $(id -u):$(id -g) /app 2>/dev/null || echo "警告: 无法设置 /app 权限"

# 特别确保关键目录权限和存在性
echo "确保关键目录存在且权限正确..."
sudo mkdir -p /app/user /app/output /app/temp 2>/dev/null || echo "警告: 无法创建目录"
sudo chown -R $(id -u):$(id -g) /app/user /app/output /app/temp 2>/dev/null || echo "警告: 无法设置目录权限"
sudo chmod -R 755 /app/user /app/output /app/temp 2>/dev/null || echo "警告: 无法设置目录权限"

# 验证权限设置结果
echo "验证权限设置结果:"
echo "/app 目录权限: $(ls -ld /app 2>/dev/null || echo '无法检查')"
echo "/app/user 目录权限: $(ls -ld /app/user 2>/dev/null || echo '无法检查')"
echo "/app/output 目录权限: $(ls -ld /app/output 2>/dev/null || echo '无法检查')"
echo "/app/temp 目录权限: $(ls -ld /app/temp 2>/dev/null || echo '无法检查')"

# 设置custom_nodes中可执行文件的权限
echo "设置custom_nodes中可执行文件的执行权限..."
# 设置所有shell脚本权限
sudo find /app/custom_nodes -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
# 设置go二进制文件权限
sudo find /app/custom_nodes -type f -name "go" -exec chmod +x {} \; 2>/dev/null || true
# 设置Windows可执行文件权限
sudo find /app/custom_nodes -type f -name "*.exe" -exec chmod +x {} \; 2>/dev/null || true
# 设置binary文件权限
sudo find /app/custom_nodes -type f -name "*.bin" -exec chmod +x {} \; 2>/dev/null || true
# 设置bin目录下所有文件权限
sudo find /app/custom_nodes -path "*/bin/*" -type f -exec chmod +x {} \; 2>/dev/null || true
# 设置go目录下所有文件权限
sudo find /app/custom_nodes -path "*/go/*" -type f -exec chmod +x {} \; 2>/dev/null || true
# 设置可能的其他可执行文件
sudo find /app/custom_nodes -type f \( -name "*server*" -o -name "*daemon*" -o -name "*Service*" \) -exec chmod +x {} \; 2>/dev/null || true
# 为所有custom_nodes子目录设置递归权限（确保目录权限正确）
sudo find /app/custom_nodes -type d -exec chmod 755 {} \; 2>/dev/null || true

# 特别处理已知的问题文件
echo "检查并修复已知问题文件..."
if [ -f "/app/custom_nodes/comfyui_custom_nodes_alekpet/DeepLXTranslateNode/go/bin/go" ]; then
    echo "发现DeepLXTranslateNode的go二进制文件，设置执行权限..."
    sudo chmod +x "/app/custom_nodes/comfyui_custom_nodes_alekpet/DeepLXTranslateNode/go/bin/go" 2>/dev/null || true
    ls -la "/app/custom_nodes/comfyui_custom_nodes_alekpet/DeepLXTranslateNode/go/bin/go" 2>/dev/null || echo "文件不存在或无权限查看"
fi

echo "============================================"
echo "ComfyUI启动前最终权限检查..."

# 最后一次权限确认和修复
if [ ! -w "/app/user" ]; then
    echo "警告: /app/user 目录不可写，尝试修复..."
    sudo chown -R $(id -u):$(id -g) /app/user 2>/dev/null || echo "修复失败"
    sudo chmod -R 755 /app/user 2>/dev/null || echo "权限设置失败"
fi

# 测试能否在 /app/user 中创建目录
echo "测试用户目录写权限..."
test_dir="/app/user/test_$(date +%s)"
if mkdir -p "$test_dir" 2>/dev/null; then
    echo "✓ 用户目录写权限正常"
    rmdir "$test_dir" 2>/dev/null || true
else
    echo "✗ 用户目录写权限异常，尝试最后修复..."
    sudo chown -R $(id -u):$(id -g) /app 2>/dev/null || true
    sudo chmod -R 755 /app/user 2>/dev/null || true
fi

echo "==================================================="
echo "ComfyUI正在启动。服务器将在以下地址可用:"
echo "http://localhost:8188 (如果端口8188已暴露)"
echo "==================================================="

# 执行CMD
exec "$@" 
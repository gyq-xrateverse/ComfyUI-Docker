#!/bin/bash
set -e

# 检查是否存在JSON配置文件
JSON_CONFIG="/app/custom_nodes.json"
if [ -f "$JSON_CONFIG" ]; then
    echo "使用JSON配置文件: $JSON_CONFIG"
    
    # 从JSON配置读取设置
    TARGET_DIR=$(jq -r '.target_directory // "/app/custom_nodes"' "$JSON_CONFIG")
    MAX_RETRIES=$(jq -r '.installation_settings.max_retries // 3' "$JSON_CONFIG")
    RETRY_DELAY=$(jq -r '.installation_settings.retry_delay // 5' "$JSON_CONFIG")
    
    # 提取启用的节点URL到数组
    mapfile -t REPOS < <(jq -r '.nodes[] | select(.enabled == true) | .url' "$JSON_CONFIG" | sort -k1,1)
    
else
    echo "未找到JSON配置文件，使用默认配置"
    
    # 默认配置（向后兼容）
    TARGET_DIR="/app/custom_nodes"
    MAX_RETRIES=3
    RETRY_DELAY=5 # in seconds
    
    # List of custom node git repositories（保持原有节点列表作为后备）
    REPOS=(
        "https://github.com/Comfy-Org/ComfyUI-Manager.git"
    )
fi

echo "将在目录中安装 ${#REPOS[@]} 个自定义节点: $TARGET_DIR"
echo "配置: MAX_RETRIES=$MAX_RETRIES, RETRY_DELAY=${RETRY_DELAY}s"

# Ensure the target directory exists
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

clone_success=0
clone_total=${#REPOS[@]}

for repo in "${REPOS[@]}"; do
    repo_name=$(basename "$repo" .git)
    echo "正在克隆 $repo_name..."
    
    retries=0
    until git clone --depth=1 "$repo"; do
        retries=$((retries+1))
        if [ $retries -ge $MAX_RETRIES ]; then
            echo "克隆 $repo 失败，已重试 $MAX_RETRIES 次。" >&2
            break
        fi
        echo "克隆 $repo 失败。${RETRY_DELAY}秒后重试... (第 $((retries+1))/$MAX_RETRIES 次尝试)"
        sleep $RETRY_DELAY
    done
    
    if [ $retries -lt $MAX_RETRIES ]; then
        ((clone_success++))
        echo "✓ $repo_name 克隆成功"
    else
        echo "✗ $repo_name 克隆失败"
    fi
done

echo "================================================================"
echo "自定义节点安装完成"
echo "成功: $clone_success/$clone_total"
if [ $clone_success -lt $clone_total ]; then
    echo "部分节点安装失败，请检查网络连接或仓库地址"
    exit 1
fi
echo "所有自定义节点已成功克隆。" 
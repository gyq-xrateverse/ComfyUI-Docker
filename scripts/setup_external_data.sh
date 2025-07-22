#!/bin/bash

# 外部数据目录设置脚本
# 检查并设置外部数据目录的软连接

echo "检查外部数据目录..."

# 检查目录是否存在且不为空的函数
is_dir_not_empty() {
    [ -d "$1" ] && [ "$(ls -A "$1" 2>/dev/null)" ]
}

# 为目录设置软连接的函数
setup_symlink() {
    local source_dir="$1"
    local target_dir="$2"
    local backup_dir="${target_dir}-bak"
    
    echo "设置软连接: $source_dir -> $target_dir"
    
    # 检查目标是否已经是指向源的软连接
    if [ -L "$target_dir" ] && [ "$(readlink "$target_dir")" = "$source_dir" ]; then
        echo "软连接已存在且正确: $target_dir -> $source_dir"
        return 0
    fi
    
    # 如果现有目录存在且不是软连接，则备份
    if [ -e "$target_dir" ] && [ ! -L "$target_dir" ]; then
        echo "备份现有目录: $target_dir -> $backup_dir"
        mv "$target_dir" "$backup_dir"
    elif [ -L "$target_dir" ]; then
        echo "移除现有软连接: $target_dir"
        rm "$target_dir"
    fi
    
    # 创建软连接
    ln -s "$source_dir" "$target_dir"
    echo "软连接已创建: $target_dir -> $source_dir"
}

# --- 默认值设置 ---
# 如果环境变量未设置，将使用以下值。您可以在此更改默认行为。
# 要覆盖这些设置，请在 `docker run` 中使用 `-e` 标志或在 `docker-compose.yml` 中设置 environment。
SKIP_MODELS_SYMLINK=${SKIP_MODELS_SYMLINK:-false}
SKIP_CUSTOM_NODES_SYMLINK=${SKIP_CUSTOM_NODES_SYMLINK:-true}

# 检查并设置models目录
if [ "$SKIP_MODELS_SYMLINK" = "true" ]; then
    echo "通过环境变量SKIP_MODELS_SYMLINK跳过models目录的软连接设置。"
    echo "将使用默认目录: /app/models"
else
    if is_dir_not_empty "/root/data/models"; then
        echo "发现外部models目录且不为空: /root/data/models"
        setup_symlink "/root/data/models" "/app/models"
    else
        echo "外部models目录未找到或为空，使用默认目录: /app/models"
    fi
fi

# 检查并设置custom_nodes目录
if [ "$SKIP_CUSTOM_NODES_SYMLINK" = "true" ]; then
    echo "通过环境变量SKIP_CUSTOM_NODES_SYMLINK跳过custom_nodes目录的软连接设置。"
    echo "将使用默认目录: /app/custom_nodes"
else
    if is_dir_not_empty "/root/data/custom_nodes"; then
        echo "发现外部custom_nodes目录且不为空: /root/data/custom_nodes"
        setup_symlink "/root/data/custom_nodes" "/app/custom_nodes"
    else
        echo "外部custom_nodes目录未找到或为空，使用默认目录: /app/custom_nodes"
    fi
fi

echo "外部数据目录设置完成。" 
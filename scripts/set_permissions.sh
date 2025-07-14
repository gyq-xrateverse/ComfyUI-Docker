#!/bin/bash

# 设置关键目录权限为1001:1001
echo "设置目录权限为1001:1001..."

# 设置models目录权限
if [ -d "/app/models" ]; then
    # 如果是软链接，设置目标目录权限
    if [ -L "/app/models" ]; then
        target_dir=$(readlink "/app/models")
        if [ -d "$target_dir" ]; then
            echo "设置软链接目标目录权限: $target_dir"
            chown -R 1001:1001 "$target_dir" 2>/dev/null || echo "无法设置 $target_dir 权限，可能需要sudo权限"
        fi
    else
        echo "设置/app/models权限"
        chown -R 1001:1001 "/app/models" 2>/dev/null || echo "无法设置/app/models权限，可能需要sudo权限"
    fi
fi

# 设置custom_nodes目录权限
if [ -d "/app/custom_nodes" ]; then
    # 如果是软链接，设置目标目录权限
    if [ -L "/app/custom_nodes" ]; then
        target_dir=$(readlink "/app/custom_nodes")
        if [ -d "$target_dir" ]; then
            echo "设置软链接目标目录权限: $target_dir"
            chown -R 1001:1001 "$target_dir" 2>/dev/null || echo "无法设置 $target_dir 权限，可能需要sudo权限"
        fi
    else
        echo "设置/app/custom_nodes权限"
        chown -R 1001:1001 "/app/custom_nodes" 2>/dev/null || echo "无法设置/app/custom_nodes权限，可能需要sudo权限"
    fi
fi

# 设置其他重要目录权限
echo "设置其他重要目录权限..."
for dir in "/app/output" "/app/user" "/app/temp"; do
    if [ -d "$dir" ]; then
        echo "设置 $dir 权限"
        chown -R 1001:1001 "$dir" 2>/dev/null || echo "无法设置 $dir 权限，可能需要sudo权限"
    fi
done

# 确保custom_nodes下的所有文件都有写权限
if [ -d "/app/custom_nodes" ]; then
    echo "确保custom_nodes下文件的写权限..."
    find /app/custom_nodes -type f -exec chmod 664 {} \; 2>/dev/null || echo "部分文件权限设置失败"
    find /app/custom_nodes -type d -exec chmod 775 {} \; 2>/dev/null || echo "部分目录权限设置失败"
fi

echo "权限设置完成" 
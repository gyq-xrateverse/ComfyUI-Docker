#!/bin/bash
# 网络超时问题修复脚本
# 针对国内服务器访问海外资源的网络问题

set -e

echo "🌐 配置网络代理和镜像源..."

# 配置Go代理（国内镜像）
export GOPROXY=https://goproxy.cn,https://goproxy.io,direct
export GOSUMDB=sum.golang.google.cn
export GO111MODULE=on

echo "✅ Go代理配置:"
echo "  GOPROXY=$GOPROXY"
echo "  GOSUMDB=$GOSUMDB"

# 配置pip镜像源（如果需要）
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 60
EOF

echo "✅ Pip镜像源已配置"

# 配置npm镜像源（如果有Node.js依赖）
if command -v npm &> /dev/null; then
    npm config set registry https://registry.npmmirror.com
    echo "✅ NPM镜像源已配置"
fi

# 配置环境变量持久化
cat >> /etc/environment << EOF
GOPROXY=https://goproxy.cn,https://goproxy.io,direct
GOSUMDB=sum.golang.google.cn
GO111MODULE=on
EOF

echo "✅ 环境变量已持久化"

# 增加网络超时时间
export HTTP_TIMEOUT=120
export HTTPS_TIMEOUT=120

echo "✅ 网络超时时间已增加到120秒"

echo "🎉 网络配置优化完成！" 
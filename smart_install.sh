#!/bin/bash
# 智能安装脚本
# 由SmartInstaller生成

set -e

echo "开始智能安装..."

echo "升级pip..."
python3.11 -m pip install --no-cache-dir --upgrade pip
python3.11 -m pip install --no-cache-dir wheel setuptools

echo "安装关键包..."
python3.11 -m pip install --no-cache-dir torch==2.6.0
python3.11 -m pip install --no-cache-dir torchvision
python3.11 -m pip install --no-cache-dir torchaudio
python3.11 -m pip install --no-cache-dir xformers==0.0.29.post3

echo "安装主要requirements..."
python3.11 -m pip install --no-cache-dir -r optimized_requirements.txt

echo "安装问题包..."
python3.11 -m pip install --no-cache-dir -r problematic_packages.txt || echo "部分问题包安装失败"

echo "智能安装完成!"

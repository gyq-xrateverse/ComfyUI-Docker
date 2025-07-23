#!/bin/bash
# install_custom_nodes_local.sh - 解压 custom_nodes.zip
set -e

ZIP_FILE="/app/custom_nodes.zip"
DEST_DIR="/app/custom_nodes"
TEMP_UNZIP_DIR="/app/temp_unzip"

echo "--- Starting local custom node installation from ZIP ---"

if [ ! -f "$ZIP_FILE" ]; then
    echo "ZIP file $ZIP_FILE not found. Skipping local node installation."
    exit 0
fi

mkdir -p "$DEST_DIR"
mkdir -p "$TEMP_UNZIP_DIR"

echo "Unzipping $ZIP_FILE to temporary directory $TEMP_UNZIP_DIR..."
unzip -q "$ZIP_FILE" -d "$TEMP_UNZIP_DIR"

# 确定实际的节点源目录，以处理嵌套的 'custom_nodes' 目录
ACTUAL_SRC_DIR="$TEMP_UNZIP_DIR"
if [ -d "$TEMP_UNZIP_DIR/custom_nodes" ] && [ "$(ls -A "$TEMP_UNZIP_DIR")" = "custom_nodes" ]; then
    echo "Detected a nested 'custom_nodes' directory inside the ZIP. Adjusting source path."
    ACTUAL_SRC_DIR="$TEMP_UNZIP_DIR/custom_nodes"
fi

echo "Copying nodes from $ACTUAL_SRC_DIR to $DEST_DIR..."
# 使用 -T 选项可以防止 'cp' 将源目录本身复制到目标目录内
cp -rT "$ACTUAL_SRC_DIR/" "$DEST_DIR/"

echo "Cleaning up temporary files..."
rm -rf "$TEMP_UNZIP_DIR"
rm "$ZIP_FILE"

echo "--- Local custom node installation from ZIP complete ---" 
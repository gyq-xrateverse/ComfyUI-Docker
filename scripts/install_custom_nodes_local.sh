#!/bin/bash
# install_custom_nodes_local.sh
set -e

SRC_DIR="/app/custom_nodes_src"
DEST_DIR="/app/custom_nodes"

echo "--- Starting local custom node installation ---"

if [ ! -d "$SRC_DIR" ] || [ -z "$(ls -A $SRC_DIR)" ]; then
    echo "Source directory $SRC_DIR is empty or does not exist. No local nodes to copy."
    exit 0
fi

mkdir -p "$DEST_DIR"

# Iterate over each sub-directory in the source directory and copy it
for node_path in "$SRC_DIR"/*; do
    if [ -d "$node_path" ]; then
        node_name=$(basename "$node_path")
        echo "Copying local node: $node_name"
        # cp -r ensures the directory and its contents are copied.
        cp -r "$node_path" "$DEST_DIR/"
    fi
done

echo "--- Local custom node installation complete ---" 
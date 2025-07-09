#!/bin/bash
set -e

# Make sure scripts directory exists
mkdir -p /app/scripts

# Update ComfyUI and custom nodes if requested
if [ "${UPDATE_REPOSITORIES:-false}" = "true" ]; then
    echo "Updating ComfyUI..."
    cd /app
    git pull

    echo "Updating custom nodes..."
    for dir in /app/custom_nodes/*; do
        if [ -d "$dir/.git" ]; then
            echo "Updating $(basename $dir)..."
            cd "$dir"
            git pull
        fi
    done
fi

# Download models if they don't exist or if forced
download_model() {
    local model_url="$1"
    local output_dir="$2"
    local filename=$(basename "$model_url")
    
    if [ ! -f "$output_dir/$filename" ] || [ "${FORCE_DOWNLOAD_MODELS:-false}" = "true" ]; then
        echo "Downloading $filename to $output_dir..."
        mkdir -p "$output_dir"
        wget -q --show-progress -O "$output_dir/$filename" "$model_url"
    else
        echo "Model $filename already exists, skipping download."
    fi
}

# Download example models if requested
if [ "${DOWNLOAD_EXAMPLE_MODELS:-false}" = "true" ]; then
    # SD 1.5 model
    download_model "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" "/app/models/checkpoints"
    
    # Upscaler models
    download_model "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth" "/app/models/upscale_models"
    
    # ControlNet models
    download_model "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth" "/app/models/controlnet"
    download_model "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth" "/app/models/controlnet"
fi

# Check and install missing critical packages at runtime
echo "Checking for missing critical packages..."
missing_packages=""

# Check each critical package
python3.11 -c "import sortedcontainers" 2>/dev/null || missing_packages="$missing_packages sortedcontainers==2.4.0"
python3.11 -c "import pyhocon" 2>/dev/null || missing_packages="$missing_packages pyhocon==0.3.59"
python3.11 -c "import imagesize" 2>/dev/null || missing_packages="$missing_packages imagesize==1.4.1"
python3.11 -c "import evalidate" 2>/dev/null || missing_packages="$missing_packages evalidate==2.0.5"
python3.11 -c "import litelama" 2>/dev/null || missing_packages="$missing_packages litelama==0.1.7"
python3.11 -c "import pytorch_lightning" 2>/dev/null || missing_packages="$missing_packages pytorch-lightning==2.5.2"
python3.11 -c "import nunchaku" 2>/dev/null || missing_packages="$missing_packages nunchaku==0.15.4"

# Install missing packages if any
if [ -n "$missing_packages" ]; then
    echo "Installing missing packages: $missing_packages"
    for package in $missing_packages; do
        echo "Installing $package..."
        python3.11 -m pip install --no-cache-dir "$package" || echo "Failed to install $package"
    done
else
    echo "All critical packages are already installed."
fi

# Generate requirements file if it doesn't exist
if [ ! -f "/app/requirements.txt" ] || [ "${REGENERATE_REQUIREMENTS:-false}" = "true" ]; then
    echo "Generating requirements.txt..."
    python3.11 /app/scripts/gather_requirements.py
    python3.11 -m pip install -r /app/requirements.txt
fi

# Run user-provided init script if it exists
if [ -f "/app/custom_init.sh" ]; then
    echo "Running custom initialization script..."
    chmod +x /app/custom_init.sh
    /app/custom_init.sh
fi

# Set ownership of all files to the running user
if [ "${FIX_PERMISSIONS:-true}" = "true" ]; then
    echo "Setting proper permissions..."
    find /app -not -user $(id -u) -exec chown -R $(id -u):$(id -g) {} \; 2>/dev/null || true
fi

echo "==================================================="
echo "ComfyUI is now starting. Server will be available at:"
echo "http://localhost:8188 (if port 8188 is exposed)"
echo "==================================================="

# Execute CMD
exec "$@" 
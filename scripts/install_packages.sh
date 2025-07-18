#!/bin/bash
set -e

echo "Upgrading pip and installing wheel and setuptools..."
python3.11 -m pip install --no-cache-dir --upgrade pip
python3.11 -m pip install --no-cache-dir wheel setuptools

# Function to install a package with multiple fallback methods
install_package() {
    local package=$1
    local version=$2
    
    # Special handling for insightface
    if [ "$package" = "insightface" ]; then
        echo "Installing insightface with optimized command..."
        python3.11 -m pip install --no-cache-dir --upgrade --prefer-binary "insightface==$version" && return 0
        echo "Warning: Failed to install insightface with optimized command, continuing..."
        return 0
    fi
    
    echo "Trying to install $package==$version..."
    
    # Try method 1: Install from binary wheel
    echo "Method 1: Installing $package==$version from binary wheel..."
    python3.11 -m pip install --no-cache-dir "$package==$version" --only-binary=:all: && return 0
    
    # Try method 2: Install with no build isolation
    echo "Method 2: Installing $package==$version with --no-build-isolation..."
    python3.11 -m pip install --no-cache-dir --no-build-isolation "$package==$version" && return 0
    
    # Try method 3: Install with no dependencies
    echo "Method 3: Installing $package==$version with --no-deps..."
    python3.11 -m pip install --no-cache-dir --no-deps "$package==$version" && return 0
    
    # If all methods fail, just continue
    echo "Warning: Failed to install $package==$version, continuing anyway..."
    return 0
}

# Install problematic packages separately
install_package "dlib" "19.24.2"
install_package "insightface" "0.7.3"
install_package "fairscale" "0.4.13"
install_package "pytorch-lightning" "2.5.2"
install_package "voluptuous" "0.15.2"
install_package "gguf" "0.17.1"
install_package "nunchaku" "0.15.4"
install_package "imagesize" "1.4.1"
install_package "argostranslate" "1.9.6"
install_package "litelama" "0.1.7"
install_package "evalidate" "2.0.5"
install_package "bizyengine" "1.2.33"
install_package "sortedcontainers" "2.4.0"
install_package "pyhocon" "0.3.59"
install_package "fal-client" "0.6.0"

# Try to install the main requirements
echo "Installing main requirements..."
# Use --no-deps for specific problematic packages
python3.11 -m pip install --no-cache-dir --no-deps insightface==0.7.3 dlib==19.24.2 fairscale==0.4.13 \
    pytorch-lightning==2.5.2 voluptuous==0.15.2 gguf==0.17.1 nunchaku==0.15.4 imagesize==1.4.1 \
    argostranslate==1.9.6 litelama==0.1.7 evalidate==2.0.5 bizyengine==1.2.33 \
    sortedcontainers==2.4.0 pyhocon==0.3.59 fal-client==0.6.0 || true
python3.11 -m pip install --no-cache-dir -r /app/requirements.txt || {
    echo "Main requirements installation failed, trying with --ignore-installed flag..."
    python3.11 -m pip install --no-cache-dir --ignore-installed -r /app/requirements.txt || {
        echo "Warning: Some packages failed to install, but we'll continue anyway."
    }
}

echo "Package installation completed." 
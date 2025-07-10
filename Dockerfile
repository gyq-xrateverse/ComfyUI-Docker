ARG PYTHON_VERSION=3.10
ARG CUDA_VERSION=12.9.0
FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    software-properties-common \
    git \
    wget \
    curl \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-dev \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    python3-setuptools \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    build-essential \
    pkg-config \
    cmake \
    ninja-build \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Python version
RUN ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python && \
    ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python3

# Set working directory
WORKDIR /app

# Clone ComfyUI (shallow clone to save space)
RUN git clone --depth=1 https://github.com/comfyanonymous/ComfyUI.git /app && \
    rm -rf /app/.git

# Clone required custom nodes (optimized for space)
RUN mkdir -p /app/custom_nodes && \
    cd /app/custom_nodes && \
    git clone --depth=1 https://github.com/Comfy-Org/ComfyUI-Manager.git && \
    git clone --depth=1 https://github.com/kijai/ComfyUI-WanVideoWrapper.git && \
    git clone --depth=1 https://github.com/kijai/ComfyUI-KJNodes.git && \
    git clone --depth=1 https://github.com/cubiq/ComfyUI_essentials.git && \
    git clone --depth=1 https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git && \
    git clone --depth=1 https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git && \
    git clone --depth=1 https://github.com/rgthree/rgthree-comfy.git && \
    git clone --depth=1 https://github.com/crystian/ComfyUI-Crystools.git && \
    git clone --depth=1 https://github.com/cubiq/ComfyUI_FaceAnalysis.git && \
    git clone --depth=1 https://github.com/cubiq/ComfyUI_InstantID.git && \
    git clone --depth=1 https://github.com/cubiq/PuLID_ComfyUI.git && \
    git clone --depth=1 https://github.com/Fannovel16/comfyui_controlnet_aux.git && \
    git clone --depth=1 https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git && \
    git clone --depth=1 https://github.com/FizzleDorf/ComfyUI_FizzNodes.git && \
    git clone --depth=1 https://github.com/Gourieff/ComfyUI-ReActor.git && \
    git clone --depth=1 https://github.com/huchenlei/ComfyUI-layerdiffuse.git && \
    git clone --depth=1 https://github.com/jags111/efficiency-nodes-comfyui.git && \
    git clone --depth=1 https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && \
    git clone --depth=1 https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git && \
    git clone --depth=1 https://github.com/ltdrdata/ComfyUI-Inspire-Pack.git && \
    git clone --depth=1 https://github.com/melMass/comfy_mtb.git && \
    git clone --depth=1 https://github.com/storyicon/comfyui_segment_anything.git && \
    git clone --depth=1 https://github.com/WASasquatch/was-node-suite-comfyui.git && \
    git clone --depth=1 https://github.com/chflame163/ComfyUI_LayerStyle.git && \
    git clone --depth=1 https://github.com/chflame163/ComfyUI_LayerStyle_Advance.git && \
    git clone --depth=1 https://github.com/shadowcz007/comfyui-mixlab-nodes.git && \
    git clone --depth=1 https://github.com/yolain/ComfyUI-Easy-Use.git && \
    git clone --depth=1 https://github.com/kijai/ComfyUI-IC-Light.git && \
    git clone --depth=1 https://github.com/siliconflow/BizyAir.git && \
    git clone --depth=1 https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch.git && \
    git clone --depth=1 https://github.com/lldacing/comfyui-easyapi-nodes.git && \
    git clone --depth=1 https://github.com/aptx4869ntu/ComfyUI-Apt_Preset.git && \
    git clone --depth=1 https://github.com/MinusZoneAI/ComfyUI-MingNodes.git && \
    git clone --depth=1 https://github.com/kijai/ComfyUI-FluxTrainer.git && \
    git clone --depth=1 https://github.com/kealiu/comfyui-supir.git && \
    git clone --depth=1 https://github.com/kijai/ComfyUI-3D-Pack.git && \
    git clone --depth=1 https://github.com/AlexanderDzhoganov/comfyui-dream-video-batches.git && \
    git clone --depth=1 https://github.com/Phando/ComfyUI-nunchaku.git && \
    find /app/custom_nodes -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true

# Copy scripts
COPY scripts/gather_requirements.py /app/scripts/
COPY scripts/problematic_requirements.txt /app/scripts/
COPY scripts/install_packages.sh /app/scripts/
RUN mkdir -p /app/scripts && chmod +x /app/scripts/install_packages.sh

# Run the requirement gathering script
RUN cd /app && python${PYTHON_VERSION} /app/scripts/gather_requirements.py

# Install Torch with CUDA support and xformers first
RUN python${PYTHON_VERSION} -m pip install --no-cache-dir torch==2.6.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --extra-index-url https://pypi.org/simple && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir xformers==0.0.29.post3

# Install problematic packages directly with fallback strategies
RUN echo "Installing problematic packages directly..." && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir sortedcontainers==2.4.0 || echo "Failed to install sortedcontainers" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir pyhocon==0.3.59 || echo "Failed to install pyhocon" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir fal-client==0.6.0 || echo "Failed to install fal-client" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir imagesize==1.4.1 || echo "Failed to install imagesize" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir evalidate==2.0.5 || echo "Failed to install evalidate" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir litelama==0.1.7 || echo "Failed to install litelama" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir pytorch-lightning==2.5.2 || echo "Failed to install pytorch-lightning" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir nunchaku==0.15.4 || echo "Failed to install nunchaku" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir voluptuous==0.15.2 || echo "Failed to install voluptuous" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir gguf==0.17.1 || echo "Failed to install gguf" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir argostranslate==1.9.6 || echo "Failed to install argostranslate" && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir bizyengine==1.2.33 || echo "Failed to install bizyengine"

# Install more complex packages with special handling
RUN echo "Installing dlib with special handling..." && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir dlib==19.24.2 --only-binary=:all: || \
    python${PYTHON_VERSION} -m pip install --no-cache-dir --no-build-isolation dlib==19.24.2 || \
    echo "Failed to install dlib"

RUN echo "Installing insightface with special handling..." && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir insightface==0.7.3 --only-binary=:all: || \
    python${PYTHON_VERSION} -m pip install --no-cache-dir --no-deps insightface==0.7.3 || \
    echo "Failed to install insightface"

RUN echo "Installing fairscale with special handling..." && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir fairscale==0.4.13 --only-binary=:all: || \
    python${PYTHON_VERSION} -m pip install --no-cache-dir --no-build-isolation fairscale==0.4.13 || \
    echo "Failed to install fairscale"

# Run the requirement gathering script and install remaining dependencies
RUN cd /app && python${PYTHON_VERSION} /app/scripts/gather_requirements.py && \
    python${PYTHON_VERSION} -m pip install --no-cache-dir -r /app/requirements.txt || echo "Some packages failed to install"

# Verify critical packages installation
RUN echo "Verifying package installation..." && \
    python${PYTHON_VERSION} -c "import sortedcontainers; print('✓ sortedcontainers installed')" || echo "✗ sortedcontainers missing" && \
    python${PYTHON_VERSION} -c "import pyhocon; print('✓ pyhocon installed')" || echo "✗ pyhocon missing" && \
    python${PYTHON_VERSION} -c "import imagesize; print('✓ imagesize installed')" || echo "✗ imagesize missing" && \
    python${PYTHON_VERSION} -c "import evalidate; print('✓ evalidate installed')" || echo "✗ evalidate missing" && \
    python${PYTHON_VERSION} -c "import litelama; print('✓ litelama installed')" || echo "✗ litelama missing" && \
    python${PYTHON_VERSION} -c "import pytorch_lightning; print('✓ pytorch_lightning installed')" || echo "✗ pytorch_lightning missing" && \
    python${PYTHON_VERSION} -c "import nunchaku; print('✓ nunchaku installed')" || echo "✗ nunchaku missing" && \
    echo "Package verification completed"

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app:${PATH}"

# Copy the entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Create directories for models and outputs
RUN mkdir -p /app/models /app/output

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default port
EXPOSE 8188

# Command
CMD ["python3.10", "main.py", "--listen", "0.0.0.0", "--port", "8188", "--enable-cors-header"] 
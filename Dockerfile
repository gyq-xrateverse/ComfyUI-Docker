ARG PYTHON_VERSION=3.11
ARG CUDA_VERSION=12.1.1
FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages and cuDNN from pre-configured NVIDIA repository
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    ca-certificates \
    curl \
    wget \
    && add-apt-repository ppa:deadsnakes/ppa \
    # The -devel base image already includes the NVIDIA repos.
    # We just need to update and install.
    && CUDNN_VERSION="8.9.7.29" \
    && CUDA_VERSION_MAJOR_MINOR=$(echo "${CUDA_VERSION}" | cut -d. -f1-2 | tr -d .) \
    && apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
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
    # The devel image already contains the correct cuDNN version (cuDNN 9 for CUDA 12.4).
    # The verify_dependencies.py script installs a matching PyTorch version.
    # Therefore, manual installation of libcudnn8 is unnecessary and incorrect.
    # --- Cleanup ---
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Python version and setup ComfyUI
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3

# 设置 Python 虚拟环境（隔离系统包，防止 install_layout 冲突）
RUN python3.11 -m venv /venv
ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV="/venv"

# 升级 pip、降级 setuptools/wheel
RUN pip install --upgrade pip && \
    pip install "setuptools<68" "wheel<0.41" "packaging"

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
    git clone --depth=1 https://github.com/MinusZoneAI/ComfyUI-MingNodes.git && \
    git clone --depth=1 https://github.com/kijai/ComfyUI-FluxTrainer.git && \
    git clone --depth=1 https://github.com/kealiu/comfyui-supir.git && \
    git clone --depth=1 https://github.com/kijai/ComfyUI-3D-Pack.git && \
    git clone --depth=1 https://github.com/AlexanderDzhoganov/comfyui-dream-video-batches.git && \
    git clone --depth=1 https://github.com/Phando/ComfyUI-nunchaku.git && \
    git clone --depth=1 https://github.com/Dontdrunk/ComfyUI-DD-Translation.git && \
    git clone --depth=1 https://github.com/AlekPet/ComfyUI_Custom_Nodes_AlekPet.git && \
    git clone --depth=1 https://github.com/TTPlanetPig/Comfyui_TTP_Toolset.git && \
    git clone --depth=1 https://github.com/ZenAI-Vietnam/ComfyUI-Kontext-Inpainting.git && \
    git clone --depth=1 https://github.com/EvilBT/ComfyUI_SLK_joy_caption_two.git && \
    git clone --depth=1 https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper.git && \
    find /app/custom_nodes -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /app/custom_nodes -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true && \
    find /app/custom_nodes -type f -name "go" -exec chmod +x {} \; 2>/dev/null || true && \
    find /app/custom_nodes -path "*/bin/*" -type f -exec chmod +x {} \; 2>/dev/null || true && \
    find /app/custom_nodes -type d -exec chmod 755 {} \; 2>/dev/null || true

# Copy required scripts and set permissions
COPY scripts/setup_external_data.sh /app/scripts/
COPY scripts/set_permissions.sh /app/scripts/
COPY scripts/build_dependencies.py /app/scripts/
COPY scripts/verify_dependencies.py /app/scripts/
RUN mkdir -p /app/scripts && \
    chmod +x /app/scripts/setup_external_data.sh && \
    chmod +x /app/scripts/set_permissions.sh && \
    chmod +x /app/scripts/build_dependencies.py && \
    chmod +x /app/scripts/verify_dependencies.py

# --- 在构建时预安装核心依赖 ---
# RUN python /app/scripts/verify_dependencies.py

# Run the unified dependency builder
RUN python /app/scripts/build_dependencies.py

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app:${PATH}"

# Copy the entrypoint script and setup directories
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh && \
    mkdir -p /app/models /app/output /app/user /app/temp

# Run as root user

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default port
EXPOSE 10001

# Command
CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "10001", "--enable-cors-header"]

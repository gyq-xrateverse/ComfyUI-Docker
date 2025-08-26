ARG PYTHON_VERSION=3.11
ARG CUDA_VERSION=12.1.1
FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages and setup Python environment (merged for efficiency)
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
    jq \
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
    unzip \
    # The devel image already contains the correct cuDNN version (cuDNN 9 for CUDA 12.4).
    # The verify_dependencies.py script installs a matching PyTorch version.
    # Therefore, manual installation of libcudnn8 is unnecessary and incorrect.
    # --- Setup Python environment ---
    && ln -sf /usr/bin/python3.11 /usr/bin/python \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    # --- Cleanup ---
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment in separate layer to ensure persistence
RUN python3.11 -m venv /venv --system-site-packages && \
    /venv/bin/python -m pip install --upgrade pip

# Set environment variables for Python virtual environment
ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV="/venv"

# Install build tools in virtual environment
RUN /venv/bin/pip install "setuptools<68" "wheel<0.41" "packaging"

# Set working directory
WORKDIR /app

# Clone ComfyUI (shallow clone to save space)
RUN git clone --depth=1 https://github.com/comfyanonymous/ComfyUI.git /app && \
    rm -rf /app/.git

# --- 自定义节点安装 ---
# 请从以下两种方式中选择一种来安装自定义节点。
# 将你不使用的那种方式注释掉。

# --- 方式一：在线安装 (默认) ---
# 在构建时直接从 GitHub 克隆节点。
# 这是默认选项，推荐大多数用户使用。
COPY custom_nodes.json /app/custom_nodes.json
COPY scripts/install_custom_nodes.sh /app/scripts/
RUN chmod +x /app/scripts/install_custom_nodes.sh && \
    /app/scripts/install_custom_nodes.sh

# --- 方式二：本地安装 ---
# 使用你预先打包好的 `custom_nodes.zip` 文件。
# 要使用此方式，请取消注释以下三行，并注释掉上面的“方式一”。
# 在构建前，请确保项目根目录下已有名为 `custom_nodes.zip` 的压缩文件。
# COPY custom_nodes.zip /app/custom_nodes.zip
# COPY scripts/install_custom_nodes_local.sh /app/scripts/
# RUN chmod +x /app/scripts/install_custom_nodes_local.sh && \
#     /app/scripts/install_custom_nodes_local.sh


# Copy required scripts first (for better caching)
COPY scripts/setup_external_data.sh /app/scripts/
COPY scripts/set_permissions.sh /app/scripts/
COPY scripts/build_dependencies.py /app/scripts/
COPY scripts/verify_dependencies.py /app/scripts/
COPY scripts/check_venv.py /app/scripts/

# --- 安装后操作和权限设置 (合并为单层) ---
RUN mkdir -p /app/scripts && \
    # 设置脚本权限
    chmod +x /app/scripts/setup_external_data.sh && \
    chmod +x /app/scripts/set_permissions.sh && \
    chmod +x /app/scripts/build_dependencies.py && \
    chmod +x /app/scripts/verify_dependencies.py && \
    chmod +x /app/scripts/check_venv.py && \
    # 清理自定义节点
    find /app/custom_nodes -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /app/custom_nodes -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true && \
    find /app/custom_nodes -type f -name "go" -exec chmod +x {} \; 2>/dev/null || true && \
    find /app/custom_nodes -path "*/bin/*" -type f -exec chmod +x {} \; 2>/dev/null || true && \
    find /app/custom_nodes -type d -exec chmod 755 {} \; 2>/dev/null || true

# --- 在构建时预安装核心依赖 ---
# RUN python /app/scripts/verify_dependencies.py

# Run the unified dependency builder
RUN python /app/scripts/build_dependencies.py

# Final check: Verify virtual environment is properly embedded in image
RUN echo "最终检查：验证虚拟环境是否正确嵌入镜像..." && \
    python /app/scripts/check_venv.py

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/venv/bin:/app:${PATH}"

# Copy the entrypoint script and setup final directories (merged)
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh && \
    mkdir -p /app/models /app/output /app/user /app/temp

# Verify virtual environment exists and is functional
RUN echo "验证虚拟环境..." && \
    ls -la /venv/ && \
    ls -la /venv/bin/ && \
    /venv/bin/python --version && \
    /venv/bin/pip --version && \
    echo "虚拟环境验证完成"

# Run as root user

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default port
EXPOSE 10001 22

# Command
CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "10001", "--enable-cors-header"]

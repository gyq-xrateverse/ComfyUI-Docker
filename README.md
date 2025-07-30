# ComfyUI 高度集成 Docker 环境

[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.9.0-green.svg)](https://developer.nvidia.com/cuda-toolkit)

这是一个高度集成、开箱即用的 ComfyUI Docker 环境，专为希望免去繁琐配置、快速上手的 AI 艺术家和开发者设计。它预装了大量流行的自定义节点和依赖项，并提供了强大的自动化功能。

## ✨ 核心特性

*   **🚀 开箱即用**: 无需手动安装 Python、CUDA 或处理复杂的依赖关系，一键启动即可开始创作。
*   **🧩 丰富的预装节点**: 集成了超过40个社区最受欢迎的自定义节点，涵盖视频、动画、面部修复、ControlNet、IPAdapter 等多种高级功能。
*   **🧠 智能依赖管理**: 内置智能安装和依赖自愈脚本，自动处理和修复潜在的包冲突和缺失问题，确保环境的稳定性。
*   **🔄 自动更新**: 支持通过环境变量一键更新 ComfyUI 核心和所有已安装的自定义节点。
*   **📂 灵活的数据管理**: 轻松挂载外部目录，用于持久化存储模型、输入/输出文件和用户数据。
*   **🤖 自动化模型下载**: 可通过环境变量在首次启动时自动下载常用的基础模型（如 SD1.5, ControlNet），节省您的时间和精力。
*   **🔧 高度可扩展**: 支持自定义初始化脚本 (`custom_init.sh`)，满足个性化配置需求。

## 🚀 快速开始

**先决条件**:
*   [Docker](https://www.docker.com/get-started)
*   [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) (用于 GPU 支持)

使用以下命令即可快速启动 ComfyUI 服务：

```bash
docker run -d \
  --gpus all \
  -p 10001:10001 \
  -v /path/to/your/models:/app/models \
  -v /path/to/your/output:/app/output \
  --name comfyui-integrated \
  your-docker-image-name:tag
```

启动后，在浏览器中访问 `http://localhost:10001` 即可打开 ComfyUI 界面。

## ⚙️ 环境变量

您可以使用以下环境变量来控制容器的行为：

| 变量名                    | 描述                                                                                             | 默认值   |
| ------------------------- | ------------------------------------------------------------------------------------------------ | -------- |
| `UPDATE_REPOSITORIES`     | 设置为 `true` 时，容器启动时会自动 `git pull` 更新 ComfyUI 和所有自定义节点。                      | `false`  |
| `DOWNLOAD_EXAMPLE_MODELS` | 设置为 `true` 时，容器首次启动会自动下载 SD1.5、ControlNet 等示例模型。                            | `false`  |
| `FORCE_DOWNLOAD_MODELS`   | 设置为 `true` 时，即使模型文件已存在，也会强制重新下载。                                           | `false`  |
| `REGENERATE_REQUIREMENTS` | 设置为 `true` 时，容器启动时会重新扫描所有节点的依赖并生成 `requirements.txt`。慎用，可能耗时较长。 | `false`  |

**示例：启动并自动更新和下载模型**
```bash
docker run -d \
  --gpus all \
  -p 10001:10001 \
  -e UPDATE_REPOSITORIES=true \
  -e DOWNLOAD_EXAMPLE_MODELS=true \
  -v /path/to/your/models:/app/models \
  -v /path/to/your/output:/app/output \
  --name comfyui-integrated \
  your-docker-image-name:tag
```

## 📂 目录挂载

为了持久化您的数据，建议挂载以下目录：

*   `/app/models`: 存放您的所有模型文件（Checkpoints, LoRA, VAE, ControlNet 等）。
*   `/app/output`: 保存所有生成的图像和文件。
*   `/app/input`: 存放需要处理的输入文件。
*   `/app/user`: 用于存放用户相关的配置文件或数据。
*   `/app/temp`: 临时文件目录。

## 🧩 自定义节点管理

本项目采用统一的JSON配置文件管理自定义节点，提供了灵活的节点配置和管理方案。

### 配置文件

**主配置文件**: `custom_nodes.json`

```json
{
  "version": "1.0.0",
  "description": "ComfyUI Docker 统一自定义节点配置", 
  "target_directory": "/app/custom_nodes",
  "installation_settings": {
    "max_retries": 3,
    "retry_delay": 5,
    "clone_depth": 1
  },
  "nodes": [
    {
      "name": "ComfyUI-Manager",
      "url": "https://github.com/Comfy-Org/ComfyUI-Manager.git",
      "description": "ComfyUI扩展管理器",
      "category": "core", 
      "priority": 1,
      "enabled": true
    }
  ]
}
```

### 节点管理工具

使用Python管理工具进行节点操作：

```bash
# 查看所有节点
python scripts/manage_nodes.py list

# 按分类查看节点
python scripts/manage_nodes.py list --category core

# 仅查看启用的节点
python scripts/manage_nodes.py list --enabled-only

# 添加新节点
python scripts/manage_nodes.py add "节点名称" "https://github.com/用户/仓库.git" "节点描述" --category utility

# 禁用/启用节点
python scripts/manage_nodes.py toggle "节点名称"

# 删除节点
python scripts/manage_nodes.py remove "节点名称"

# 验证配置文件
python scripts/manage_nodes.py validate

# 查看所有分类
python scripts/manage_nodes.py categories
```

### 预装节点分类

| 分类 | 说明 | 主要节点 |
|------|------|----------|
| **core** | 核心管理工具 | ComfyUI-Manager |
| **utility** | 通用工具类 | ComfyUI_essentials, rgthree-comfy, was-node-suite-comfyui |
| **video** | 视频处理 | ComfyUI-VideoHelperSuite, ComfyUI-Frame-Interpolation |
| **face** | 人脸相关 | ComfyUI_FaceAnalysis, ComfyUI_InstantID, ComfyUI-ReActor |
| **controlnet** | 控制网络 | comfyui_controlnet_aux |
| **style** | 样式处理 | ComfyUI_LayerStyle, ComfyUI_LayerStyle_Advance |
| **audio** | 音频处理 | audio-separation-nodes-comfyui, ComfyUI-F5-TTS |
| **3d** | 3D处理 | ComfyUI-3D-Pack |
| **training** | 模型训练 | ComfyUI-FluxTrainer |
| **upscale** | 超分辨率 | ComfyUI-SUPIR |

### 配置兼容性

- ✅ **自动检测**: 系统会自动检测JSON配置文件
- ✅ **向后兼容**: 如未找到JSON文件，使用默认配置
- ✅ **跨平台**: 支持Linux (bash) 和Windows (batch + PowerShell)

## 🛠️ 技术栈

*   **基础镜像**: `nvidia/cuda:12.9.0-devel-ubuntu22.04`
*   **Python**: `3.11`
*   **PyTorch**: `2.6.0` (CUDA 12.4)
*   **xformers**: `0.0.29.post3`

## 🤝 贡献与反馈

如果您遇到任何问题或有改进建议，欢迎通过 [Issues](https://github.com/your-repo/issues) 提交反馈。
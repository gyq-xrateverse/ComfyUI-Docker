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

## 🧩 自定义节点配置

本项目采用统一的JSON配置文件管理自定义节点，简化节点管理流程。

### 配置文件格式

**配置文件**: `custom_nodes.json`

```json
[
  "https://github.com/Comfy-Org/ComfyUI-Manager.git",
  "https://github.com/kijai/ComfyUI-WanVideoWrapper.git", 
  "https://github.com/kijai/ComfyUI-KJNodes.git",
  "https://github.com/cubiq/ComfyUI_essentials.git"
]
```

### 使用方法

1. **自动检测**: 安装脚本会自动检测并使用JSON配置文件
2. **编辑配置**: 直接编辑`custom_nodes.json`文件添加或删除节点URL
3. **向后兼容**: 如未找到JSON文件，使用内置的默认节点列表

### 预装节点

本镜像预装了46个常用自定义节点，包括：

- **ComfyUI-Manager** - 核心扩展管理器
- **ComfyUI_essentials** - 基础工具集  
- **ComfyUI-VideoHelperSuite** - 视频处理工具
- **ComfyUI_FaceAnalysis** - 人脸分析工具
- **comfyui_controlnet_aux** - ControlNet辅助工具
- **ComfyUI-Impact-Pack** - Impact工具包
- **was-node-suite-comfyui** - WAS节点套件
- 以及更多专业节点...

### 系统特性

- ✅ **全局共享**: 统一的JSON配置文件
- ✅ **简单易用**: 纯URL数组格式，无复杂结构  
- ✅ **跨平台**: 支持Linux和Windows
- ✅ **向后兼容**: 无配置文件时使用默认列表

## 🛠️ 技术栈

*   **基础镜像**: `nvidia/cuda:12.9.0-devel-ubuntu22.04`
*   **Python**: `3.11`
*   **PyTorch**: `2.6.0` (CUDA 12.4)
*   **xformers**: `0.0.29.post3`

## 🤝 贡献与反馈

如果您遇到任何问题或有改进建议，欢迎通过 [Issues](https://github.com/your-repo/issues) 提交反馈。
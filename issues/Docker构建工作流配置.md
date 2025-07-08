# Docker构建工作流配置

## 任务背景
参考腾讯 Coding 容器镜像仓库的配置模式，为 ComfyUI-Docker 项目创建新的 Docker 构建工作流。

## 执行计划
1. ✅ 创建新工作流文件：`.github/workflows/docker-build-coding.yml`
2. ✅ 配置腾讯 Coding 容器镜像仓库
3. ✅ 添加 Secrets 检查机制
4. ✅ 改进版本管理逻辑
5. ✅ 升级到最新的 GitHub Actions
6. ✅ 添加元数据提取和标签管理
7. ✅ 添加构建缓存优化
8. ✅ 添加构建状态通知

## 主要改进
- **仓库配置**：支持腾讯 Coding 容器镜像仓库
- **版本管理**：支持 tag 版本和 commit 版本，保持 ComfyUI 版本同步
- **安全检查**：构建前检查必需的 Secrets 配置
- **性能优化**：添加 GitHub Actions 缓存
- **用户体验**：中文化步骤名称和状态反馈

## 需要配置的 Secrets
- `CODING_DOCKER_REGISTRY`：腾讯 Coding 仓库地址
- `CODING_DOCKER_USER`：腾讯 Coding 用户名
- `CODING_DOCKER_TOKEN`：腾讯 Coding 访问令牌

## 触发条件
- 手动触发：`workflow_dispatch`
- 定时触发：每月3号凌晨0点
- 代码推送：main/master 分支或 v* 标签
- 文件变更：Dockerfile、scripts/**、工作流文件

## 构建特性
- 平台：linux/amd64
- 超时：180分钟
- 缓存：GitHub Actions 缓存
- 标签：版本号、latest、分支名等多种标签 
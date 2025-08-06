# Docker构建优化任务

## 背景
Docker构建失败，出现磁盘空间不足和Python依赖冲突问题。

## 解决方案：混合策略（三阶段）

### 阶段一：立即问题修复
- [x] 清理Docker空间  
- [x] 修复关键依赖冲突
- [x] 优化包安装顺序

### 阶段二：Dockerfile优化  
- [x] 合并RUN指令
- [x] 添加构建缓存优化
- [x] 实现多阶段构建准备

### 阶段三：依赖管理改进
- [x] 增强版本冲突检测
- [x] 实现智能版本协商  
- [x] 添加依赖安装验证

## 关键修改
- numpy: 1.26.4 → 1.24.4 (兼容mediapipe<2)
- 新增scipy版本约束: 1.12.0
- opencv-contrib-python-headless: 移入PINNED_PACKAGES，固定4.8.1.78
- 手动包安装添加--no-deps防止版本覆盖
- 优化安装顺序和构建层数

## 问题修复记录
### 第一次构建失败原因
- MANUAL_PACKAGES中的opencv-contrib-python-headless覆盖了固定版本
- pip自动升级依赖包到最新版本
- 构建在导出阶段卡住

### 修复措施
- ✅ 将opencv-contrib-python-headless移入PINNED_PACKAGES
- ✅ 添加--no-deps标志防止依赖升级
- ✅ 移除重复的包管理逻辑 
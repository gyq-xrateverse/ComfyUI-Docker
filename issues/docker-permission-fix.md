# Docker权限和依赖修复任务

## 任务背景
ComfyUI Docker容器启动时遇到多个权限和依赖问题：
- 多个custom nodes因权限不足无法正常工作
- 缺失关键依赖包：insightface, toolz, plyfile
- ComfyUI-nunchaku版本兼容性问题
- BizyAir包更新失败

## 修复计划

### 1. 依赖包修复
- ✅ 添加insightface==0.7.3到requirements.txt
- ✅ 添加toolz到requirements.txt  
- ✅ 添加plyfile到requirements.txt
- ✅ 修复nunchaku版本为0.3.1

### 2. 权限问题修复
- ✅ 改进scripts/set_permissions.sh脚本
- ✅ 在Dockerfile中添加用户目录创建
- ✅ 在启动脚本中添加运行时权限检查

### 3. 启动脚本优化
- ✅ 在entrypoint.sh中添加依赖包检查
- ✅ 改进错误处理和日志输出
- ✅ 配置pip使用清华源（国内运行环境）

## 受影响的节点
- ComfyUI_InstantID (insightface)
- ComfyUI-ReActor (insightface)
- PuLID_ComfyUI (insightface)
- ComfyUI-Apt_Preset (toolz)
- ComfyUI-3D-Pack (plyfile)
- ComfyUI-nunchaku (版本兼容性)

## 执行状态
- [x] 修改requirements.txt
- [x] 更新权限设置脚本
- [x] 修改Dockerfile
- [x] 优化启动脚本
- [ ] 测试和验证

## 下一步
需要重新构建Docker镜像并测试所有修复是否生效。 
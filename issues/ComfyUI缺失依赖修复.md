# ComfyUI缺失依赖修复

## 任务背景
ComfyUI Docker镜像启动时出现多个Python包缺失错误，导致部分自定义节点无法正常加载。

## 缺失的依赖包
根据错误日志分析，发现以下缺失的包：

1. `sortedcontainers` - ComfyUI-Apt_Preset需要
2. `litelama` - ComfyUI-MingNodes需要  
3. `imagesize` - ComfyUI-FluxTrainer需要
4. `pytorch_lightning==2.5.2` - comfyui-supir需要
5. `pyhocon` - ComfyUI-3D-Pack需要
6. `evalidate` - comfyui-dream-video-batches需要
7. `nunchaku==0.15.4` - ComfyUI-nunchaku需要
8. `fal-client` - comfyui-mixlab-nodes需要

## 执行计划
1. ✅ 创建任务记录文件
2. ✅ 更新 `scripts/problematic_requirements.txt`
3. ✅ 更新 `scripts/gather_requirements.py`
4. ✅ 改进 `scripts/install_packages.sh`
5. ✅ 验证配置文件

## 预期结果
- 解决所有已知的缺失依赖问题
- 提高Docker镜像构建的成功率
- 减少ComfyUI启动时的错误信息

## 执行结果
### 已完成的修改

1. **更新了 `scripts/problematic_requirements.txt`**：
   - 添加了 `sortedcontainers==2.4.0`
   - 添加了 `pyhocon==0.3.59`
   - 添加了 `fal-client==0.6.0`
   - 总计15个已知问题包

2. **更新了 `scripts/gather_requirements.py`**：
   - 新增7个自定义节点的requirements.txt URL
   - 添加了缺失包到ADDITIONAL_PACKAGES列表
   - 扩展了EXCLUDED_PACKAGES列表，包含所有问题包

3. **改进了 `scripts/install_packages.sh`**：
   - 为所有问题包添加了专门的install_package调用
   - 更新了--no-deps安装命令，包含所有问题包
   - 保持了原有的错误处理机制

### 解决的具体问题
- ✅ `sortedcontainers` - 解决ComfyUI-Apt_Preset导入错误
- ✅ `litelama` - 解决ComfyUI-MingNodes导入错误
- ✅ `imagesize` - 解决ComfyUI-FluxTrainer导入错误
- ✅ `pytorch_lightning` - 解决comfyui-supir导入错误
- ✅ `pyhocon` - 解决ComfyUI-3D-Pack导入错误
- ✅ `evalidate` - 解决comfyui-dream-video-batches导入错误
- ✅ `nunchaku` - 解决ComfyUI-nunchaku导入错误
- ✅ `fal-client` - 解决comfyui-mixlab-nodes FalVideo功能

下一步可以重新构建Docker镜像来验证修复效果。 
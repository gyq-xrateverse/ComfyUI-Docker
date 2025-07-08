# Docker推送失败修复方案

## 问题分析
根据您提供的登录信息，Docker镜像推送失败的主要原因是：

1. **镜像名称格式错误**：原配置使用 `registry/comfyui`，正确格式应该是 `registry/namespace/repository`
2. **推送配置不完整**：缺少合适的outputs配置
3. **错误处理机制不够完善**

## 修复内容

### 1. 镜像名称修复
```yaml
# 修改前
CODING_DOCKER_IMAGE: ${{ secrets.CODING_DOCKER_REGISTRY }}/comfyui

# 修改后 (根据正确的推送格式)
CODING_DOCKER_IMAGE: ${{ secrets.CODING_DOCKER_REGISTRY }}/clipshop/comfyui
```

实际推送路径将是：`registry/clipshop/comfyui/comfyui:tag`

### 2. 推送配置优化
添加了 `outputs` 配置确保正确推送：
```yaml
outputs: type=image,push=${{ github.event_name != 'pull_request' }}
```

### 3. 增强验证和重试机制
- 添加了镜像推送权限测试
- 改进了失败后的手动推送逻辑
- 增强了错误诊断信息

## 需要配置的GitHub Secrets

基于您提供的登录信息，需要在GitHub仓库设置中添加以下Secrets：

```
CODING_DOCKER_REGISTRY=g-chqo4329-docker.pkg.coding.net
CODING_DOCKER_USER=comfyui-1751946459274  
CODING_DOCKER_TOKEN=4e5312eb7e814acc7bf03bdb321236c3c98564e1
```

## 预期镜像路径

修复后，镜像将推送到：
- `g-chqo4329-docker.pkg.coding.net/clipshop/comfyui/comfyui:latest`
- `g-chqo4329-docker.pkg.coding.net/clipshop/comfyui/comfyui:版本号`

推送格式遵循：`registry/clipshop/comfyui/<PACKAGE>:<VERSION>`

## 验证步骤

1. 确认GitHub Secrets配置正确
2. 手动触发workflow或推送代码
3. 检查构建日志中的登录验证步骤
4. 验证最终的镜像推送结果

## 安全建议

- 定期轮换访问令牌
- 确保仓库权限设置合适
- 监控推送日志异常情况 
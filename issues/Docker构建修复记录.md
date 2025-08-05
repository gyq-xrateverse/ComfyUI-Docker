# Docker构建修复记录

## 问题1：jq依赖缺失
**现象：** `jq: command not found`，导致无法解析 `custom_nodes.json`
**原因：** Dockerfile中未安装 `jq` 工具
**解决：** ✅ 在Dockerfile第25行添加 `jq \`

## 问题2：git clone重试机制失效  
**现象：** 网络失败时立即退出，不执行重试
**原因：** `set -e` 与重试机制冲突
**解决：** ✅ 在git clone循环前后添加 `set +e` 和 `set -e`

## 修改文件
- Dockerfile（添加jq依赖）
- scripts/install_custom_nodes.sh（修复重试机制）

## 预期效果
1. 正常解析JSON配置（46个节点）
2. 网络失败时自动重试（最多3次）
3. 提高构建成功率和容错性 
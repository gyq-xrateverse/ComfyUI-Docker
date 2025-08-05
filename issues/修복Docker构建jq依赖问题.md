# 修复Docker构建jq依赖问题

## 问题描述
Docker构建时，安装自定义节点的脚本报错：`jq: command not found`，导致无法解析 `custom_nodes.json` 文件，最终安装了0个自定义节点。

## 根本原因
- `install_custom_nodes.sh` 脚本第10行使用 `jq -r '.[]'` 解析JSON
- Dockerfile中未安装 `jq` 工具
- 导致脚本无法读取节点列表

## 解决方案
在Dockerfile的apt-get install命令中添加 `jq` 包

## 执行记录
- ✅ 在第25行添加 `jq \`，位于 `python3-setuptools \` 之后
- 修改文件：Dockerfile

## 预期结果
Docker构建时将自动安装jq工具，脚本能正常解析JSON并安装所有48个自定义节点。 
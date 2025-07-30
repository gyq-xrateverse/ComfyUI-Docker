# 统一自定义节点JSON配置

## 任务背景
创建统一的自定义节点文件，使用JSON格式，全局共享，包含ComfyUI-Manager节点地址。

## 执行计划
1. 创建JSON配置文件 - `custom_nodes.json`
2. 提取现有节点信息
3. 修改Linux安装脚本
4. 修改Windows脚本
5. 创建管理工具
6. 更新文档

## 当前状态
- [x] 计划制定
- [x] JSON配置创建 - `custom_nodes.json`
- [x] Linux脚本修改 - `scripts/install_custom_nodes.sh`
- [x] Windows脚本修改 - `scripts/download_repos.bat`
- [x] Python管理工具 - `scripts/manage_nodes.py`
- [x] 文档更新 - `README.md`

## 完成内容（简化版）
1. **JSON配置文件**: 创建简单的URL数组格式，包含46个节点
2. **Linux脚本**: 支持JSON数组自动读取 
3. **Windows脚本**: 支持PowerShell解析JSON数组
4. **文档更新**: 简化说明使用方法

## 最终实现
- ✅ **简单数组格式**: `["url1", "url2", ...]`
- ✅ **ComfyUI-Manager首位**: 位于数组第一个元素
- ✅ **全局共享**: 统一的JSON配置文件
- ✅ **向后兼容**: 无JSON时使用默认配置
- ✅ **跨平台支持**: Linux/Windows双平台

## 技术要点
- JSON结构设计
- 脚本兼容性保持
- 配置验证机制 
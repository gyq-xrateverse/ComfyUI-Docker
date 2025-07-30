#!/usr/bin/env python3
"""
ComfyUI自定义节点管理工具

提供添加、删除、更新和验证自定义节点配置的功能
支持JSON配置文件的管理和维护
"""
import json
import sys
import argparse
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

# 配置文件路径
CONFIG_FILE = "/app/custom_nodes.json"
LOCAL_CONFIG_FILE = "./custom_nodes.json"

# 选择配置文件路径
config_file = CONFIG_FILE if os.path.exists(CONFIG_FILE) else LOCAL_CONFIG_FILE

class NodeManager:
    def __init__(self, config_path: str = config_file):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载JSON配置文件"""
        if not os.path.exists(self.config_path):
            return self.create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"错误：无法加载配置文件 {self.config_path}: {e}")
            sys.exit(1)
    
    def save_config(self) -> None:
        """保存配置到文件"""
        self.config['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"✓ 配置已保存到: {self.config_path}")
        except IOError as e:
            print(f"错误：无法保存配置文件: {e}")
            sys.exit(1)
    
    def create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().strftime('%Y-%m-%d'),
            "description": "ComfyUI Docker 统一自定义节点配置",
            "target_directory": "/app/custom_nodes",
            "installation_settings": {
                "max_retries": 3,
                "retry_delay": 5,
                "clone_depth": 1
            },
            "nodes": []
        }
    
    def validate_url(self, url: str) -> bool:
        """验证GitHub仓库URL格式"""
        pattern = r'^https://github\.com/[\w\-\.]+/[\w\-\.]+\.git$'
        return bool(re.match(pattern, url))
    
    def validate_node(self, node: Dict[str, Any]) -> List[str]:
        """验证节点配置"""
        errors = []
        required_fields = ['name', 'url', 'description', 'category', 'priority', 'enabled']
        
        for field in required_fields:
            if field not in node:
                errors.append(f"缺少必填字段: {field}")
        
        if 'url' in node and not self.validate_url(node['url']):
            errors.append(f"无效的GitHub仓库URL: {node['url']}")
        
        if 'priority' in node:
            try:
                priority = int(node['priority'])
                if priority < 1 or priority > 5:
                    errors.append("优先级必须在1-5之间")
            except (ValueError, TypeError):
                errors.append("优先级必须是数字")
        
        if 'enabled' in node and not isinstance(node['enabled'], bool):
            errors.append("enabled字段必须是布尔值")
        
        return errors
    
    def get_node_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找节点"""
        for node in self.config['nodes']:
            if node['name'] == name:
                return node
        return None
    
    def get_node_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """根据URL查找节点"""
        for node in self.config['nodes']:
            if node['url'] == url:
                return node
        return None
    
    def add_node(self, name: str, url: str, description: str, category: str = "utility", 
                 priority: int = 3, enabled: bool = True) -> bool:
        """添加新节点"""
        if self.get_node_by_name(name):
            print(f"错误：节点 '{name}' 已存在")
            return False
        
        if self.get_node_by_url(url):
            print(f"错误：URL '{url}' 已存在")
            return False
        
        node = {
            "name": name,
            "url": url,
            "description": description,
            "category": category,
            "priority": priority,
            "enabled": enabled
        }
        
        errors = self.validate_node(node)
        if errors:
            print("节点验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        self.config['nodes'].append(node)
        print(f"✓ 已添加节点: {name}")
        return True
    
    def remove_node(self, name: str) -> bool:
        """删除节点"""
        for i, node in enumerate(self.config['nodes']):
            if node['name'] == name:
                removed = self.config['nodes'].pop(i)
                print(f"✓ 已删除节点: {removed['name']}")
                return True
        
        print(f"错误：未找到节点 '{name}'")
        return False
    
    def update_node(self, name: str, **kwargs) -> bool:
        """更新节点信息"""
        node = self.get_node_by_name(name)
        if not node:
            print(f"错误：未找到节点 '{name}'")
            return False
        
        # 更新指定字段
        for key, value in kwargs.items():
            if key in ['name', 'url', 'description', 'category', 'priority', 'enabled']:
                node[key] = value
        
        errors = self.validate_node(node)
        if errors:
            print("节点更新验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print(f"✓ 已更新节点: {name}")
        return True
    
    def toggle_node(self, name: str) -> bool:
        """启用/禁用节点"""
        node = self.get_node_by_name(name)
        if not node:
            print(f"错误：未找到节点 '{name}'")
            return False
        
        node['enabled'] = not node['enabled']
        status = "启用" if node['enabled'] else "禁用"
        print(f"✓ 已{status}节点: {name}")
        return True
    
    def list_nodes(self, category: Optional[str] = None, enabled_only: bool = False) -> None:
        """列出节点"""
        nodes = self.config['nodes']
        
        if category:
            nodes = [n for n in nodes if n['category'] == category]
        
        if enabled_only:
            nodes = [n for n in nodes if n['enabled']]
        
        if not nodes:
            print("未找到匹配的节点")
            return
        
        print(f"\n节点列表 (共 {len(nodes)} 个):")
        print("-" * 80)
        
        for node in nodes:
            status = "✓" if node['enabled'] else "✗"
            print(f"{status} {node['name']:<30} | {node['category']:<12} | P{node['priority']}")
            print(f"   {node['description']}")
            print(f"   {node['url']}")
            print()
    
    def list_categories(self) -> None:
        """列出所有分类"""
        categories = set(node['category'] for node in self.config['nodes'])
        print("可用分类:")
        for category in sorted(categories):
            count = sum(1 for node in self.config['nodes'] if node['category'] == category)
            enabled_count = sum(1 for node in self.config['nodes'] 
                              if node['category'] == category and node['enabled'])
            print(f"  {category}: {enabled_count}/{count} 个节点")
    
    def validate_config(self) -> bool:
        """验证整个配置文件"""
        print("验证配置文件...")
        
        errors = []
        
        # 验证基本结构
        required_keys = ['version', 'nodes', 'installation_settings']
        for key in required_keys:
            if key not in self.config:
                errors.append(f"缺少必填字段: {key}")
        
        # 验证每个节点
        node_names = set()
        node_urls = set()
        
        for i, node in enumerate(self.config.get('nodes', [])):
            node_errors = self.validate_node(node)
            for error in node_errors:
                errors.append(f"节点 {i+1}: {error}")
            
            # 检查重复
            if 'name' in node:
                if node['name'] in node_names:
                    errors.append(f"重复的节点名称: {node['name']}")
                node_names.add(node['name'])
            
            if 'url' in node:
                if node['url'] in node_urls:
                    errors.append(f"重复的节点URL: {node['url']}")
                node_urls.add(node['url'])
        
        if errors:
            print("配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("✓ 配置验证通过")
        return True

def main():
    parser = argparse.ArgumentParser(description='ComfyUI自定义节点管理工具')
    parser.add_argument('--config', '-c', default=config_file, 
                       help='配置文件路径')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加节点
    add_parser = subparsers.add_parser('add', help='添加新节点')
    add_parser.add_argument('name', help='节点名称')
    add_parser.add_argument('url', help='GitHub仓库URL')
    add_parser.add_argument('description', help='节点描述')
    add_parser.add_argument('--category', default='utility', help='节点分类')
    add_parser.add_argument('--priority', type=int, default=3, help='优先级(1-5)')
    add_parser.add_argument('--disabled', action='store_true', help='添加时禁用节点')
    
    # 删除节点
    remove_parser = subparsers.add_parser('remove', help='删除节点')
    remove_parser.add_argument('name', help='节点名称')
    
    # 更新节点
    update_parser = subparsers.add_parser('update', help='更新节点')
    update_parser.add_argument('name', help='节点名称')
    update_parser.add_argument('--url', help='新的URL')
    update_parser.add_argument('--description', help='新的描述')
    update_parser.add_argument('--category', help='新的分类')
    update_parser.add_argument('--priority', type=int, help='新的优先级')
    
    # 启用/禁用节点
    toggle_parser = subparsers.add_parser('toggle', help='启用/禁用节点')
    toggle_parser.add_argument('name', help='节点名称')
    
    # 列出节点
    list_parser = subparsers.add_parser('list', help='列出节点')
    list_parser.add_argument('--category', help='按分类筛选')
    list_parser.add_argument('--enabled-only', action='store_true', help='仅显示启用的节点')
    
    # 列出分类
    subparsers.add_parser('categories', help='列出所有分类')
    
    # 验证配置
    subparsers.add_parser('validate', help='验证配置文件')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = NodeManager(args.config)
    
    if args.command == 'add':
        success = manager.add_node(
            args.name, args.url, args.description, 
            args.category, args.priority, not args.disabled
        )
        if success:
            manager.save_config()
    
    elif args.command == 'remove':
        success = manager.remove_node(args.name)
        if success:
            manager.save_config()
    
    elif args.command == 'update':
        updates = {}
        if args.url: updates['url'] = args.url
        if args.description: updates['description'] = args.description
        if args.category: updates['category'] = args.category
        if args.priority: updates['priority'] = args.priority
        
        if updates:
            success = manager.update_node(args.name, **updates)
            if success:
                manager.save_config()
        else:
            print("未指定要更新的字段")
    
    elif args.command == 'toggle':
        success = manager.toggle_node(args.name)
        if success:
            manager.save_config()
    
    elif args.command == 'list':
        manager.list_nodes(args.category, args.enabled_only)
    
    elif args.command == 'categories':
        manager.list_categories()
    
    elif args.command == 'validate':
        manager.validate_config()

if __name__ == '__main__':
    main() 
#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class CopyrightDocGenerator:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_info = {}
        self.code_files = []
        
    def analyze_project(self) -> Dict:
        self.project_info = {
            'name': '',
            'version': '',
            'description': '',
            'author': '',
            'type': '',
            'platform': '',
            'tech_stack': [],
            'features': [],
            'structure': {}
        }
        
        app_json = self.project_path / 'app.json'
        if app_json.exists():
            with open(app_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.project_info['name'] = data.get('window', {}).get('navigationBarTitleText', '')
                self.project_info['type'] = '微信小程序'
                self.project_info['platform'] = '微信小程序平台'
                self.project_info['tech_stack'] = ['微信小程序原生框架']
        
        project_config = self.project_path / 'project.config.json'
        if project_config.exists():
            with open(project_config, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.project_info['appid'] = data.get('appid', '')
                self.project_info['lib_version'] = data.get('libVersion', '')
        
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not self.project_info['name']:
                    self.project_info['name'] = data.get('name', '')
                self.project_info['version'] = data.get('version', '1.0.0')
                self.project_info['description'] = data.get('description', '')
                self.project_info['author'] = data.get('author', '')
                if not self.project_info['tech_stack']:
                    self.project_info['tech_stack'] = ['Node.js']
        
        readme = self.project_path / 'README.md'
        if readme.exists():
            with open(readme, 'r', encoding='utf-8') as f:
                content = f.read()
                self._extract_features_from_readme(content)
        
        self._collect_code_files()
        self._analyze_structure()
        
        return self.project_info
    
    def _extract_features_from_readme(self, content: str):
        features = []
        lines = content.split('\n')
        in_features = False
        
        for line in lines:
            if '功能特性' in line or 'Features' in line:
                in_features = True
                continue
            
            if in_features:
                if line.strip().startswith('##') and '功能特性' not in line:
                    break
                if line.strip().startswith('-') or line.strip().startswith('✅'):
                    feature = re.sub(r'^[-✅]\s*', '', line.strip())
                    if feature:
                        features.append(feature)
        
        self.project_info['features'] = features
    
    def _collect_code_files(self):
        code_extensions = ['.js', '.ts', '.wxml', '.wxss', '.json', '.py', '.java', '.go', '.rs']
        exclude_dirs = ['.git', 'node_modules', '__pycache__', 'dist', 'build', '.trae']
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in code_extensions):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.project_path)
                    self.code_files.append(str(relative_path))
        
        self.code_files.sort(key=self._file_priority)
    
    def _file_priority(self, file_path: str) -> int:
        path = Path(file_path)
        
        if path.name == 'app.js':
            return 0
        if path.name == 'main.js':
            return 1
        if path.name == 'index.js':
            return 2
        if 'utils' in str(path):
            return 10
        if 'pages' in str(path):
            return 20
        if 'components' in str(path):
            return 30
        if 'config' in str(path):
            return 40
        
        return 50
    
    def _analyze_structure(self):
        structure = {}
        
        for file_path in self.code_files:
            parts = Path(file_path).parts
            current = structure
            
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    current[part] = 'file'
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
        
        self.project_info['structure'] = structure
    
    def count_code_lines(self) -> int:
        total_lines = 0
        
        for file_path in self.code_files:
            full_path = self.project_path / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        
        return total_lines
    
    def generate_source_code_doc(self, output_path: str, lines_per_page: int = 50, total_pages: int = 60):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.project_info['name']} 源代码文档\n\n")
            f.write(f"软件名称：{self.project_info['name']}\n")
            f.write(f"版本号：{self.project_info['version']}\n")
            f.write(f"生成日期：{datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write("---\n\n")
            
            page_num = 1
            line_on_page = 0
            
            for file_path in self.code_files:
                if page_num > total_pages:
                    break
                
                full_path = self.project_path / file_path
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as source_file:
                        lines = source_file.readlines()
                        
                        f.write(f"## 文件：{file_path}\n")
                        f.write(f"总行数：{len(lines)}\n\n")
                        f.write("```javascript\n")
                        
                        for line in lines:
                            f.write(line.rstrip() + '\n')
                            line_on_page += 1
                            
                            if line_on_page >= lines_per_page:
                                f.write("```\n\n")
                                f.write(f"--- 第 {page_num} 页 ---\n\n")
                                page_num += 1
                                line_on_page = 0
                                
                                if page_num > total_pages:
                                    break
                                
                                f.write(f"## 文件：{file_path}（续）\n\n")
                                f.write("```javascript\n")
                        
                        f.write("```\n\n")
                        
                        if line_on_page >= lines_per_page:
                            f.write(f"--- 第 {page_num} 页 ---\n\n")
                            page_num += 1
                            line_on_page = 0
                
                except Exception as e:
                    f.write(f"无法读取文件：{e}\n\n")
            
            while page_num <= total_pages:
                f.write(f"--- 第 {page_num} 页 ---\n\n")
                page_num += 1
    
    def generate_user_manual(self, output_path: str):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.project_info['name']} 用户手册\n\n")
            f.write(f"## 一、软件简介\n\n")
            f.write(f"{self.project_info['description']}\n\n")
            
            f.write("### 1.1 软件概述\n\n")
            f.write(f"{self.project_info['name']}是一款{self.project_info['type']}，")
            f.write(f"运行于{self.project_info['platform']}。\n\n")
            
            f.write("### 1.2 主要特点\n\n")
            for feature in self.project_info['features'][:10]:
                if feature:
                    f.write(f"- {feature}\n")
            f.write("\n")
            
            f.write("## 二、功能概述\n\n")
            f.write("### 2.1 功能列表\n\n")
            for i, feature in enumerate(self.project_info['features'], 1):
                if feature:
                    f.write(f"{i}. {feature}\n")
            f.write("\n")
            
            f.write("## 三、安装/使用说明\n\n")
            f.write("### 3.1 系统要求\n\n")
            f.write(f"- 平台：{self.project_info['platform']}\n")
            f.write(f"- 技术栈：{', '.join(self.project_info['tech_stack'])}\n\n")
            
            f.write("### 3.2 使用说明\n\n")
            f.write("1. 打开微信客户端\n")
            f.write("2. 搜索或扫描小程序二维码\n")
            f.write("3. 进入小程序开始使用\n\n")
            
            f.write("## 四、主要功能说明\n\n")
            for i, feature in enumerate(self.project_info['features'][:5], 1):
                if feature:
                    f.write(f"### 4.{i} {feature}\n\n")
                    f.write("该功能提供了便捷的操作体验。\n\n")
                    f.write("**操作步骤：**\n")
                    f.write("1. 点击对应功能按钮\n")
                    f.write("2. 按照提示进行操作\n")
                    f.write("3. 查看操作结果\n\n")
            
            f.write("## 五、注意事项\n\n")
            f.write("1. 请确保网络连接正常\n")
            f.write("2. 首次使用可能需要授权\n")
            f.write("3. 数据保存在本地，清除缓存会丢失数据\n\n")
            
            f.write("## 六、技术支持\n\n")
            f.write(f"### 6.1 版本信息\n\n")
            f.write(f"- 软件版本：{self.project_info['version']}\n")
            f.write(f"- 更新日期：{datetime.now().strftime('%Y-%m-%d')}\n")
    
    def generate_design_doc(self, output_path: str):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.project_info['name']} 设计说明书\n\n")
            f.write("## 一、软件概述\n\n")
            f.write("### 1.1 软件简介\n\n")
            f.write(f"{self.project_info['description']}\n\n")
            
            f.write("### 1.2 开发背景\n\n")
            f.write(f"为满足用户在{self.project_info['platform']}上的使用需求，")
            f.write(f"开发了{self.project_info['name']}。\n\n")
            
            f.write("### 1.3 设计目标\n\n")
            f.write("- 提供简洁易用的用户界面\n")
            f.write("- 实现稳定可靠的功能\n")
            f.write("- 优化用户体验\n\n")
            
            f.write("## 二、需求分析\n\n")
            f.write("### 2.1 功能需求\n\n")
            for i, feature in enumerate(self.project_info['features'], 1):
                if feature:
                    f.write(f"{i}. {feature}\n")
            f.write("\n")
            
            f.write("### 2.2 性能需求\n\n")
            f.write("- 响应时间：操作响应时间小于500ms\n")
            f.write("- 并发支持：支持多用户同时使用\n")
            f.write("- 资源占用：内存占用合理\n\n")
            
            f.write("### 2.3 安全需求\n\n")
            f.write("- 数据加密：敏感数据加密存储\n")
            f.write("- 权限控制：合理的权限管理\n")
            f.write("- 防护措施：防止常见安全漏洞\n\n")
            
            f.write("## 三、总体设计\n\n")
            f.write("### 3.1 系统架构\n\n")
            f.write(f"本软件采用{self.project_info['type']}架构，")
            f.write(f"基于{', '.join(self.project_info['tech_stack'])}开发。\n\n")
            
            f.write("### 3.2 模块划分\n\n")
            f.write("软件主要包含以下模块：\n\n")
            f.write("- 主界面模块：负责用户界面的展示和交互\n")
            f.write("- 业务逻辑模块：处理核心业务逻辑\n")
            f.write("- 数据存储模块：负责数据的存储和管理\n")
            f.write("- 工具模块：提供通用工具函数\n\n")
            
            f.write("### 3.3 技术选型\n\n")
            for tech in self.project_info['tech_stack']:
                f.write(f"- {tech}\n")
            f.write("\n")
            
            f.write("### 3.4 运行环境\n\n")
            f.write(f"- 平台：{self.project_info['platform']}\n")
            f.write(f"- 基础库版本：{self.project_info.get('lib_version', '最新')}\n\n")
            
            f.write("## 四、详细设计\n\n")
            f.write("### 4.1 主界面模块\n\n")
            f.write("#### 4.1.1 模块功能\n\n")
            f.write("负责软件主界面的展示和用户交互。\n\n")
            f.write("#### 4.1.2 模块接口\n\n")
            f.write("- 页面路由接口\n")
            f.write("- 事件处理接口\n\n")
            
            f.write("### 4.2 业务逻辑模块\n\n")
            f.write("#### 4.2.1 模块功能\n\n")
            f.write("处理软件的核心业务逻辑。\n\n")
            f.write("#### 4.2.2 模块接口\n\n")
            f.write("- 数据处理接口\n")
            f.write("- 计算接口\n\n")
            
            f.write("## 五、数据结构设计\n\n")
            f.write("### 5.1 数据存储\n\n")
            f.write("使用本地存储保存用户数据。\n\n")
            
            f.write("### 5.2 数据格式\n\n")
            f.write("- JSON格式存储配置信息\n")
            f.write("- 数组格式存储历史记录\n\n")
            
            f.write("## 六、界面设计\n\n")
            f.write("### 6.1 界面布局\n\n")
            f.write("采用响应式布局，适配不同屏幕尺寸。\n\n")
            
            f.write("### 6.2 交互设计\n\n")
            f.write("- 点击交互：按钮点击触发相应功能\n")
            f.write("- 手势交互：支持滑动等手势操作\n\n")
            
            f.write("## 七、安全设计\n\n")
            f.write("### 7.1 安全机制\n\n")
            f.write("- 输入验证：对用户输入进行验证\n")
            f.write("- 错误处理：完善的错误处理机制\n\n")
            
            f.write("## 八、测试设计\n\n")
            f.write("### 8.1 测试策略\n\n")
            f.write("-("- 单元测试：测试各个功能模块\n")
            f.write("- 集成测试：测试模块间的交互\n")
            f.write("- 用户测试：真实用户使用测试\n")
    
    def generate_application_form(self, output_path: str, owner_info: Optional[Dict] = None):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        code_lines = self.count_code_lines()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 软件著作权登记申请表\n\n")
            f.write("## 基本信息\n\n")
            f.write("| 字段 | 内容 |\n")
            f.write("|------|------|\n")
            f.write(f"| 软件全称 | {self.project_info['name']} |\n")
            f.write(f"| 软件简称 | {self.project_info['name'][:10]} |\n")
            f.write(f"| 版本号 | V{self.project_info['version']} |\n")
            f.write(f"| 开发完成日期 | {datetime.now().strftime('%Y-%m-%d')} |\n")
            f.write(f"| 首次发表日期 | {datetime.now().strftime('%Y-%m-%d')} |\n\n")
            
            f.write("## 著作权人信息\n\n")
            f.write("| 字段 | 内容 |\n")
            f.write("|------|------|\n")
            
            if owner_info:
                f.write(f"| 著作权人 | {owner_info.get('name', '')} |\n")
                f.write(f"| 证件类型 | {owner_info.get('id_type', '')} |\n")
                f.write(f"| 证件号码 | {owner_info.get('id_number', '')} |\n")
                f.write(f"| 地址 | {owner_info.get('address', '')} |\n")
                f.write(f"| 邮编 | {owner_info.get('zip_code', '')} |\n")
                f.write(f"| 联系人 | {owner_info.get('contact', '')} |\n")
                f.write(f"| 电话 | {owner_info.get('phone', '')} |\n")
                f.write(f"| 邮箱 | {owner_info.get('email', '')} |\n")
            else:
                f.write("| 著作权人 | （请填写） |\n")
                f.write("| 证件类型 | （请填写） |\n")
                f.write("| 证件号码 | （请填写） |\n")
                f.write("| 地址 | （请填写） |\n")
                f.write("| 邮编 | （请填写） |\n")
                f.write("| 联系人 | （请填写） |\n")
                f.write("| 电话 | （请填写） |\n")
                f.write("| 邮箱 | （请填写） |\n")
            f.write("\n")
            
            f.write("## 开发者信息\n\n")
            f.write("| 字段 | 内容 |\n")
            f.write("|------|------|\n")
            f.write(f"| 开发者 | {self.project_info.get('author', '（请填写）')} |\n")
            f.write("| 证件类型 | （请填写） |\n")
            f.write("| 证件号码 | （请填写） |\n")
            f.write("| 地址 | （请填写） |\n")
            f.write("| 邮编 | （请填写） |\n")
            f.write("| 联系人 | （请填写） |\n")
            f.write("| 电话 | （请填写） |\n")
            f.write("| 邮箱 | （请填写） |\n\n")
            
            f.write("## 软件信息\n\n")
            f.write("| 字段 | 内容 |\n")
            f.write("|------|------|\n")
            f.write("| 软件性质 | 原创 |\n")
            f.write(f"| 软件分类 | 移动应用软件-小程序 |\n")
            f.write(f"| 代码行数 | {code_lines} |\n")
            f.write("| 开发环境 | 微信开发者工具 |\n")
            f.write(f"| 运行环境 | {self.project_info['platform']} |\n")
            f.write("| 编程语言 | JavaScript, WXML, WXSS |\n")
            f.write("| 硬件要求 | 智能手机 |\n\n")
            
            f.write("## 软件功能简介\n\n")
            for feature in self.project_info['features']:
                if feature:
                    f.write(f"- {feature}\n")
            f.write("\n")
            
            f.write("## 备注\n\n")
            f.write("本软件为原创开发，未使用第三方商业代码。\n")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_copyright_docs.py <project_path> [output_dir]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(project_path, 'copyright_docs')
    
    generator = CopyrightDocGenerator(project_path)
    
    print("正在分析项目...")
    project_info = generator.analyze_project()
    print(f"项目名称：{project_info['name']}")
    print(f"项目版本：{project_info['version']}")
    print(f"项目类型：{project_info['type']}")
    print(f"代码文件数：{len(generator.code_files)}")
    print(f"代码总行数：{generator.count_code_lines()}")
    
    print("\n正在生成源代码文档...")
    generator.generate_source_code_doc(os.path.join(output_dir, '源代码文档.md'))
    
    print("正在生成用户手册...")
    generator.generate_user_manual(os.path.join(output_dir, '用户手册.md'))
    
    print("正在生成设计说明书...")
    generator.generate_design_doc(os.path.join(output_dir, '设计说明书.md'))
    
    print("正在生成申请表...")
    generator.generate_application_form(os.path.join(output_dir, '软件著作权登记申请表.md'))
    
    print(f"\n所有文档已生成到：{output_dir}")


if __name__ == '__main__':
    main()

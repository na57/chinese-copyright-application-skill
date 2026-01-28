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
        
        return total

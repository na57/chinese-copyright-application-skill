# Chinese Copyright Application Skill

用于生成中国软件著作权申请材料的完整工具包。支持从项目代码、文档等自动提取信息，生成软件著作权登记申请表、源代码文档（前后各30页）、用户手册和设计说明书。适用于微信小程序、Web应用、移动App、桌面应用等各类软件项目。

## 功能特性

- 自动分析项目结构和配置文件
- 支持微信小程序、Web/Node.js等多种项目类型
- 自动提取项目信息（名称、版本、描述、功能特性等）
- 生成符合中国版权保护中心要求的申请材料
- 支持自定义输出目录

## 使用方法

### 方法1：使用Python脚本

```bash
python3 scripts/generate_copyright_docs.py <项目路径> [输出目录]
```

示例：

```bash
# 在当前目录生成文档
python3 scripts/generate_copyright_docs.py /path/to/your/project

# 指定输出目录
python3 scripts/generate_copyright_docs.py /path/to/your/project /path/to/output
```

### 方法2：在Trae IDE中使用

当用户需要申请中国软件著作权时，这个skill会自动触发，提供完整的生成流程指导。

## 生成的文档

1. **软件著作权登记申请表.md** - 包含所有必填字段的申请表
2. **源代码文档.md** - 前后各30页，每页50行的源代码
3. **用户手册.md** - 完整的用户使用手册
4. **设计说明书.md** - 详细的技术设计文档

## 支持的项目类型

- 微信小程序（app.json, project.config.json）
- Web/Node.js项目（package.json）
- 其他项目（自动查找配置文件）

## 项目信息来源

- **微信小程序**：app.json, project.config.json, package.json, README.md
- **Web/Node.js**：package.json, README.md
- **其他项目**：自动查找配置文件和README

## 注意事项

- 生成的文档为Markdown格式，便于后续转换为Word或PDF
- 源代码文档按照文件重要性排序，优先展示核心业务逻辑
- 申请表中的著作权人信息需要手动填写
- 确保软件为原创，不侵犯他人著作权

## 许可证

MIT License

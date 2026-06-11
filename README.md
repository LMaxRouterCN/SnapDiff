# SnapDiff

**SnapDiff** 是一个轻量级、通用的文件快照对比与变更日志（Changelog）自动生成工具。

<details>
<summary>点击展开图集</summary>

![alt text](<README/屏幕截图 2026-06-11 162507.png>)
![alt text](<README/屏幕截图 2026-06-11 162351.png>)

</details>

## 为什么需要它？
传统版本控制系统（如 Git）在处理纯代码项目时是神，但当你面对包含大量二进制文件（如游戏模组、材质包、模型、音效）的整合包或大型项目时，Git 的 `.git` 文件夹会迅速膨胀到几个 G，且提交记录极其繁琐。

SnapDiff 采用 **"按需快照 + 智能深潜 + 模板渲染"** 的架构，专为解决"我只想知道这次发包到底改了啥"的痛点而生。

## 核心特性
- **极速快照对比**：一键扫描目录，基于 SHA256 精准识别文件的 增、删、改、重命名、移动。
- **智能深潜引擎 (Deep Dive)**：针对压缩包（如 `.jar`），自动进入内部提取 `mods.toml` 或 `fabric.mod.json` 中的版本号，让日志直接显示"JEI 15.2 -> 15.3"，而不是干巴巴的文件名。
- **Jinja2 模板自定义**：日志排版完全由 Markdown 模板控制，想怎么排就怎么排。
- **硬核扁平 UI**：基于 PySide6 打造的深色工业风界面，无圆角，纯粹的效率工具。

## 快速开始

### 1. 运行环境
确保你安装了 Python 3.8+。
```bash
pip install -r requirements.txt
python main.py
```

### 2. 配置规则 (`config/default_rules.yaml`)
你可以通过修改配置文件来适配任何项目：
- **ignore_patterns**：类似 `.gitignore` 语法，过滤不需要追踪的目录（如 `logs/`, `crash-reports/`）。
- **copy_content_extensions**：指定哪些后缀的文本文件需要备份内容，以便后续生成 Diff。
- **deep_dive_rules**：配置针对特定压缩包的"深潜"规则，指定进入包内读取哪个文件的哪个字段。

### 3. 自定义日志模板 (`config/templates/`)
程序使用 Jinja2 引擎渲染日志。你可以复制 `default.md` 并修改其排版逻辑，然后在 `default_rules.yaml` 中指定你的新模板文件。

## 打包发布
如果你想将其打包为独立的 `.exe` 文件分发给他人，或者脱离 Python 环境使用，只需双击运行根目录下的：
```bat
build.bat
```
脚本会自动调用 PyInstaller 编译程序，并将 `config` 文件夹部署到 `dist/SnapDiff/` 目录下。

## 开源协议
MPL-2.0
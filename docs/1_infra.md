# PPTAgent 基础设施搭建详细指南 (1_infra.md)

> **所属阶段**: Phase 0 — 基础设施搭建
> **版本**: v1.0 | **日期**: 2026-07-01 | **作者**: PPTAgent Team
> **前置阅读**: [0_plan.md](./0_plan.md)（项目总体技术架构与实施计划）

---

## 目录

1. [概述与目标](#1-概述与目标)
2. [操作系统与环境准备](#2-操作系统与环境准备)
3. [项目骨架生成](#3-项目骨架生成)
4. [Python 虚拟环境与包管理](#4-python-虚拟环境与包管理)
5. [依赖安装详解](#5-依赖安装详解)
6. [代码质量基础设施](#6-代码质量基础设施)
7. [配置管理系统](#7-配置管理系统)
8. [日志系统搭建](#8-日志系统搭建)
9. [测试基础设施](#9-测试基础设施)
10. [Git 仓库与版本控制规范](#10-git-仓库与版本控制规范)
11. [CI/CD Pipeline](#11-cicd-pipeline)
12. [文档基础设施](#12-文档基础设施)
13. [开发辅助脚本](#13-开发辅助脚本)
14. [IDE 集成配置](#14-ide-集成配置)
15. [验证清单与冒烟测试](#15-验证清单与冒烟测试)
16. [常见问题与故障排除](#16-常见问题与故障排除)

---

## 1. 概述与目标

### 1.1 Phase 0 在整体项目中的位置

```
Phase 0 (本阶段)       Phase 1-5              Phase 6-8
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 基础设施搭建  │ ──▶ │ 工具与引擎实现│ ──▶ │ Agent 集成   │
│              │     │              │     │ 与 UI 交付   │
└──────────────┘     └──────────────┘     └──────────────┘
    1-2 周             10-15 周             4-7 周
```

Phase 0 是整个项目的根基。一个设计良好的基础设施可以让后续开发效率提升 3-5 倍，并大幅减少因环境不一致导致的 "在我机器上能跑" 类问题。

### 1.2 本阶段目标

| 编号 | 目标 | 可验证产出 |
|------|------|-----------|
| INFRA-01 | 项目目录结构完整可用 | `tree PPTAgent/` 输出符合预期 |
| INFRA-02 | Python 虚拟环境可复现 | `pip install -r requirements.txt` 一次成功 |
| INFRA-03 | 代码质量工具就绪 | `pre-commit run --all-files` 零错误 |
| INFRA-04 | 日志系统可工作 | 运行任意模块产生结构化日志 |
| INFRA-05 | 配置系统可加载 | `Config.load()` 正确解析 YAML |
| INFRA-06 | 测试框架可运行 | `pytest` 发现并执行测试（即使只有占位test） |
| INFRA-07 | CI/CD pipeline 通过 | 首个 commit 触发 CI 全绿 |
| INFRA-08 | Git 仓库规范就绪 | `.gitignore`、分支保护规则到位 |

### 1.3 完成标准 (Definition of Done)

- [ ] 任意开发者 clone 仓库后，执行两条命令即可开始开发：
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -e ".[dev]"
  ```
- [ ] `pre-commit` hook 在每次 `git commit` 时自动运行并通过
- [ ] `pytest` 运行不报错（允许 0 个测试 collected）
- [ ] `python -c "from pptagent import __version__; print(__version__)"` 输出 `"0.1.0"`
- [ ] CI 上 lint + type-check + test 三个 job 全部通过

---

## 2. 操作系统与环境准备

### 2.1 支持的操作系统矩阵

| 操作系统 | 版本 | 优先级 | 说明 |
|----------|------|--------|------|
| Ubuntu | 22.04 LTS / 24.04 LTS | P0 | 主要开发与部署平台 |
| macOS | 14 (Sonoma) / 15 (Sequoia) | P1 | 开发者本地环境 |
| Windows | 11 + WSL2 | P1 | 通过 WSL2 兼容，原生 Windows 暂不作为一等公民支持 |
| Debian | 12 (Bookworm) | P2 | 服务器部署备选 |

> **核心原则**：所有脚本必须以 Ubuntu 22.04+ 作为首要目标平台。macOS 通过 Homebrew 提供等效的系统依赖。Windows 用户必须使用 WSL2。

### 2.2 Python 版本要求

```
最低版本:  Python 3.10
推荐版本:  Python 3.11
计划支持:  Python 3.12（待依赖库全面兼容后切换）
```

选择 Python 3.11 的理由：
- 相比 3.10，有显著的性能提升（约 10-25%）
- `tomllib` 标准库内置，无需第三方 TOML 解析
- `asyncio` 改进，对 Agent 的异步工具调用友好
- 所有核心依赖（python-pptx, langchain, opencv-python）均已有稳定支持
- 暂不选择 3.12 的原因：部分依赖（如 paddleocr）的预编译 wheel 在 3.12 上可能不可用

### 2.3 Python 安装指南

#### 2.3.1 Ubuntu 22.04/24.04

```bash
# 方法一：使用 deadsnakes PPA（推荐，可获得最新补丁版本）
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-dev python3.11-venv python3.11-distutils

# 验证安装
python3.11 --version  # 应输出 Python 3.11.x

# 方法二：使用系统自带版本（Ubuntu 24.04 默认为 3.12，需降级）
# 不推荐，建议统一使用 deadsnakes PPA
```

#### 2.3.2 macOS

```bash
# 使用 Homebrew（推荐）
brew install python@3.11

# 验证安装
/opt/homebrew/bin/python3.11 --version

# 确保 pip 可用
/opt/homebrew/bin/python3.11 -m pip install --upgrade pip
```

#### 2.3.3 Windows (WSL2)

```bash
# 在 WSL2 的 Ubuntu 中执行，与 2.3.1 节完全相同
# 首先确保 WSL2 已安装且为 Ubuntu 22.04/24.04
wsl --install -d Ubuntu-22.04  # 在 PowerShell 中执行
```

### 2.4 系统级依赖安装

这些依赖需要在系统级别安装，因为 python-pptx、OpenCV 等库会链接到它们的 C/C++ 库。

#### 2.4.1 Ubuntu / Debian

```bash
#!/bin/bash
# 文件位置: scripts/install_system_deps.sh
# 用途: 一键安装所有系统级依赖
# 执行: bash scripts/install_system_deps.sh

set -euo pipefail

echo "=========================================="
echo " PPTAgent - 系统依赖安装脚本"
echo " 目标平台: Ubuntu 22.04+ / Debian 12+"
echo "=========================================="

# ---------- 基础编译工具链 ----------
echo "[1/8] 安装基础编译工具链..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    build-essential \
    cmake \
    pkg-config \
    gcc \
    g++ \
    make \
    automake \
    autoconf \
    libtool \
    curl \
    wget \
    ca-certificates \
    gnupg \
    git

# ---------- Python 编译依赖 ----------
echo "[2/8] 安装 Python 编译依赖..."
sudo apt-get install -y -qq \
    libpython3-dev \
    python3-dev

# ---------- 图像处理库（Pillow / OpenCV 依赖）----------
echo "[3/8] 安装图像处理库..."
sudo apt-get install -y -qq \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    liblcms2-dev \
    liblzma-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# ---------- LibreOffice（旧版 .ppt 转换）----------
echo "[4/8] 安装 LibreOffice Headless..."
sudo apt-get install -y -qq \
    libreoffice-impress \
    libreoffice-common

# 验证安装
libreoffice --headless --version

# ---------- LaTeX（数学公式渲染）----------
echo "[5/8] 安装 LaTeX 发行版..."
# 使用 texlive-core（完整版约 3GB）或 texlive-latex-extra（精简版约 500MB）
# 开发环境推荐 full，CI 环境推荐精简版
sudo apt-get install -y -qq \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-science \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    dvipng \
    cm-super

# ---------- Poppler（PDF 处理 / pdf2image 依赖）----------
echo "[6/8] 安装 Poppler..."
sudo apt-get install -y -qq \
    poppler-utils \
    libpoppler-dev

# ---------- Graphviz（流程图渲染）----------
echo "[7/8] 安装 Graphviz..."
sudo apt-get install -y -qq \
    graphviz \
    libgraphviz-dev

# ---------- FFmpeg（视频/音频处理）----------
echo "[8/8] 安装 FFmpeg..."
sudo apt-get install -y -qq \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev

echo ""
echo "=========================================="
echo " ✅ 所有系统依赖安装完成！"
echo "=========================================="
echo ""
echo "下一步: 运行 scripts/setup_venv.sh 创建 Python 虚拟环境"
```

#### 2.4.2 macOS (Homebrew)

```bash
#!/bin/bash
# 文件位置: scripts/install_system_deps_macos.sh

set -euo pipefail

echo "=========================================="
echo " PPTAgent - macOS 系统依赖安装脚本"
echo "=========================================="

# 确保 Homebrew 已安装
if ! command -v brew &> /dev/null; then
    echo "❌ 请先安装 Homebrew: https://brew.sh/"
    exit 1
fi

brew install \
    python@3.11 \
    libreoffice \
    --cask mactex-no-gui \
    poppler \
    graphviz \
    ffmpeg

echo "✅ macOS 系统依赖安装完成！"
```

### 2.5 Node.js 依赖（Mermaid CLI）

Mermaid CLI 用于将 Mermaid 语法的流程图/思维导图渲染为图片，以便插入到 PPT 中。

```bash
# 检查 Node.js 版本（要求 >= 18）
node --version

# 如未安装 Node.js:
# Ubuntu: sudo apt-get install -y nodejs npm
# macOS: brew install node

# 全局安装 Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# 验证安装
mmdc --version  # 应输出版本号

# 可选：设置 Puppeteer 跳过 Chromium 下载（如果已安装 Chrome/Chromium）
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
```

### 2.6 环境变量汇总

```bash
# 建议添加到 ~/.bashrc 或 ~/.zshrc 中
# 文件位置: scripts/env.sh（source 此文件即可）

# ---- PPTAgent 环境变量 ----

# Python 路径（按实际安装位置调整）
export PPTAGENT_PYTHON="${PPTAGENT_PYTHON:-python3.11}"

# LibreOffice 路径
export LIBREOFFICE_PATH="${LIBREOFFICE_PATH:-/usr/bin/libreoffice}"

# LaTeX 相关
export PATH="/usr/bin:$PATH"  # 确保 pdflatex 在 PATH 中

# Mermaid CLI 路径
export MERMAID_CLI_PATH="${MERMAID_CLI_PATH:-$(which mmdc)}"

# OCR 语言（按需加载，减少内存占用）
export OCR_LANGUAGES="en,ch"

# 开发模式标志
export PPTAGENT_ENV="${PPTAGENT_ENV:-development}"

# 日志级别
export PPTAGENT_LOG_LEVEL="${PPTAGENT_LOG_LEVEL:-DEBUG}"
```

---

## 3. 项目骨架生成

### 3.1 完整目录树

以下是需要创建的完整目录结构（与 plan_0.md 附录 A 一致，此处做更细致的展开）：

```
PPTAgent/                              # 项目根目录
│
├── pptagent/                          # 主 Python 包
│   ├── __init__.py                    # 包初始化 + __version__
│   │
│   ├── agent/                         # Agent 编排层
│   │   ├── __init__.py
│   │   ├── planner.py                 # 规划器
│   │   ├── executor.py                # 执行器
│   │   ├── evaluator.py               # 评估器
│   │   ├── reflector.py               # 反思器
│   │   ├── loop_controller.py         # Agentic Loop 主控
│   │   └── prompts/                   # Prompt 模板
│   │       ├── __init__.py
│   │       ├── system.yaml            # System Prompt
│   │       ├── research_ppt.yaml      # 科研PPT Prompt
│   │       └── editing.yaml           # 编辑PPT Prompt
│   │
│   ├── core/                          # 核心数据模型与状态管理
│   │   ├── __init__.py
│   │   ├── document.py                # PPTDocument / Slide / Element
│   │   ├── change_manager.py          # Undo / Redo
│   │   ├── session.py                 # Session 状态管理
│   │   ├── converter.py               # .ppt → .pptx 格式转换
│   │   └── exceptions.py             # 自定义异常类
│   │
│   ├── tools/                         # 工具层
│   │   ├── __init__.py
│   │   ├── base.py                    # BaseTool / ToolResult / ToolRegistry
│   │   ├── file/                      # 文件工具 (T01-T05)
│   │   │   ├── __init__.py
│   │   │   ├── finder.py              # T01: find_ppt_files
│   │   │   ├── io.py                  # T02-T05: open/save/rename/close
│   │   │   └── watcher.py             # 文件变更监听（可选）
│   │   ├── extraction/                # 提取工具 (T06-T13)
│   │   │   ├── __init__.py
│   │   │   ├── text.py                # T06: extract_text
│   │   │   ├── image.py               # T07: extract_images
│   │   │   ├── table.py               # T08: extract_tables
│   │   │   ├── formula.py             # T09: extract_formulas
│   │   │   ├── diagram.py             # T10: extract_diagrams
│   │   │   ├── chart.py               # T11: extract_charts
│   │   │   ├── media.py               # T12: extract_media
│   │   │   └── reader.py              # T13: read_element
│   │   ├── manipulation/              # 编辑工具 (T14-T20)
│   │   │   ├── __init__.py
│   │   │   ├── position.py            # T14: set_position
│   │   │   ├── size.py                # T15: set_size
│   │   │   ├── text_format.py         # T16: format_text
│   │   │   ├── alignment.py           # T17: set_alignment
│   │   │   ├── text_effect.py         # T18: set_text_effect
│   │   │   ├── delete.py              # T19: delete_element
│   │   │   └── duplicate.py           # T20: duplicate_element
│   │   ├── insertion/                 # 插入工具 (T21-T30)
│   │   │   ├── __init__.py
│   │   │   ├── image.py               # T21: insert_image
│   │   │   ├── media.py               # T22-T24: insert_video/audio/gif
│   │   │   ├── text_box.py            # T25: insert_text_box
│   │   │   ├── table.py               # T26: insert_table
│   │   │   ├── formula.py             # T27: insert_formula
│   │   │   ├── diagram.py             # T28-T29: insert_flowchart/mindmap
│   │   │   └── chart.py               # T30: insert_chart
│   │   ├── layout/                    # 布局工具 (T31-T34)
│   │   │   ├── __init__.py
│   │   │   ├── auto_layout.py         # T31: auto_layout
│   │   │   ├── template.py            # T32: apply_template
│   │   │   └── arrange.py             # T33-T34: align/distribute
│   │   ├── slide/                     # 幻灯片工具 (T35-T38)
│   │   │   ├── __init__.py
│   │   │   ├── add.py                 # T35: add_slide
│   │   │   ├── delete.py              # T36: delete_slide
│   │   │   ├── reorder.py             # T37: reorder_slides
│   │   │   └── duplicate.py           # T38: duplicate_slide
│   │   ├── search/                    # 搜索工具 (T39-T41)
│   │   │   ├── __init__.py
│   │   │   ├── web_search.py          # T39: web_search
│   │   │   ├── rag_search.py          # T40: rag_search
│   │   │   └── element_search.py      # T41: search_element
│   │   └── utility/                   # 工具类 (T42-T45)
│   │       ├── __init__.py
│   │       ├── preview.py             # T42: preview_slide
│   │       ├── undo_redo.py           # T43-T44: undo/redo
│   │       └── info.py                # T45: get_slide_info
│   │
│   ├── engines/                       # 底层渲染引擎
│   │   ├── __init__.py
│   │   ├── latex_engine.py            # LaTeX 公式编译为图片
│   │   ├── mermaid_engine.py          # Mermaid 图表渲染
│   │   ├── graphviz_engine.py         # Graphviz 流程图渲染
│   │   ├── ocr_engine.py              # OCR 文本识别
│   │   └── chart_engine.py            # matplotlib/plotly 图表生成
│   │
│   ├── knowledge/                     # 知识增强
│   │   ├── __init__.py
│   │   ├── rag.py                     # RAG 检索增强生成
│   │   ├── web_search.py              # 联网搜索实现
│   │   └── template_store.py          # PPT 模板库管理
│   │
│   └── utils/                         # 通用工具
│       ├── __init__.py
│       ├── logger.py                  # 结构化日志
│       ├── emu_utils.py               # EMU <-> 英寸 <-> 厘米 单位转换
│       ├── validators.py              # 输入校验
│       ├── file_utils.py              # 文件路径处理
│       ├── hash_utils.py              # 哈希与去重
│       └── async_utils.py             # 异步工具
│
├── config/                            # 配置文件
│   ├── default.yaml                   # 默认配置（所有可配置项）
│   ├── development.yaml               # 开发环境覆盖
│   ├── production.yaml                # 生产环境覆盖
│   └── prompts/                       # Prompt 模板（YAML格式）
│       ├── system.yaml
│       ├── task_planning.yaml
│       └── element_reading.yaml
│
├── scripts/                           # 辅助脚本
│   ├── install_system_deps.sh         # 系统依赖安装
│   ├── install_system_deps_macos.sh   # macOS 系统依赖安装
│   ├── setup_venv.sh                  # 虚拟环境创建
│   ├── run_lint.sh                    # 运行所有 lint 检查
│   ├── run_tests.sh                   # 运行所有测试
│   ├── convert_legacy.sh              # 批量转换 .ppt → .pptx
│   ├── env.sh                         # 环境变量
│   └── clean.sh                       # 清理临时文件
│
├── tests/                             # 测试
│   ├── __init__.py
│   ├── conftest.py                    # pytest 全局 fixtures
│   ├── unit/                          # 单元测试
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── test_document.py
│   │   │   ├── test_change_manager.py
│   │   │   └── test_converter.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── file/
│   │   │   ├── extraction/
│   │   │   ├── manipulation/
│   │   │   ├── insertion/
│   │   │   └── layout/
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── test_emu_utils.py
│   │       └── test_validators.py
│   ├── integration/                   # 集成测试
│   │   ├── __init__.py
│   │   ├── test_file_operations.py
│   │   ├── test_extraction_pipeline.py
│   │   └── test_editing_pipeline.py
│   └── fixtures/                      # 测试数据
│       ├── sample_simple.pptx          # 简单PPT：纯文本 + 图片
│       ├── sample_complex.pptx         # 复杂PPT：表格 + 公式 + 图表
│       ├── sample_legacy.ppt           # 旧版 .ppt 文件
│       ├── sample_images/              # 测试用图片
│       │   ├── test_photo.png
│       │   └── test_diagram.jpg
│       └── expected/                   # 预期输出（用于对比测试）
│           └── sample_simple_text.json
│
├── data/                              # 运行时数据（gitignore 部分内容）
│   ├── .gitkeep
│   ├── templates/                     # PPT 模板库
│   │   └── .gitkeep
│   ├── vector_db/                     # 向量数据库文件
│   │   └── .gitkeep
│   └── samples/                       # 示例PPT
│       └── .gitkeep
│
├── docs/                              # 项目文档
│   ├── index.md                       # 文档索引
│   ├── architecture.md                # 架构说明
│   ├── api/                           # API 文档（自动生成）
│   │   └── .gitkeep
│   ├── guides/                        # 使用指南
│   │   ├── getting_started.md
│   │   └── tool_development.md
│   └── decisions/                     # 架构决策记录 (ADR)
│       └── .gitkeep
│
├── .github/                           # GitHub 配置
│   ├── workflows/                     # GitHub Actions
│   │   ├── ci.yaml                    # 主 CI 流水线
│   │   └── docs.yaml                  # 文档构建与部署
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── .vscode/                           # VSCode 项目配置
│   ├── settings.json
│   ├── extensions.json                # 推荐插件
│   └── launch.json                    # 调试配置
│
├── .gitignore
├── .gitattributes
├── .pre-commit-config.yaml
├── .editorconfig
├── .markdownlint.yaml
│
├── pyproject.toml                     # 项目元数据 + 工具配置
├── requirements.txt                   # 运行时依赖（锁定版本）
├── requirements-dev.txt               # 开发依赖
├── LICENSE                            # MIT License
├── README.md                          # 项目首页文档
├── CHANGELOG.md                       # 变更日志
├── CODE_OF_CONDUCT.md                 # 行为准则
├── CONTRIBUTING.md                    # 贡献指南
└── Makefile                           # 便捷命令
```

### 3.2 一键生成脚本

```bash
#!/bin/bash
# 文件位置: scripts/create_skeleton.sh
# 用途: 一键创建完整的项目目录结构
# 执行: bash scripts/create_skeleton.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "项目根目录: $PROJECT_ROOT"

# 创建所有目录
create_dirs() {
    local dirs=(
        # 主包
        pptagent/agent/prompts
        pptagent/core
        pptagent/tools/file
        pptagent/tools/extraction
        pptagent/tools/manipulation
        pptagent/tools/insertion
        pptagent/tools/layout
        pptagent/tools/slide
        pptagent/tools/search
        pptagent/tools/utility
        pptagent/engines
        pptagent/knowledge
        pptagent/utils

        # 配置
        config/prompts

        # 脚本
        scripts

        # 测试
        tests/unit/core
        tests/unit/tools/file
        tests/unit/tools/extraction
        tests/unit/tools/manipulation
        tests/unit/tools/insertion
        tests/unit/tools/layout
        tests/unit/utils
        tests/integration
        tests/fixtures/sample_images
        tests/fixtures/expected

        # 数据
        data/templates
        data/vector_db
        data/samples

        # 文档
        docs/api
        docs/guides
        docs/decisions

        # CI/CD
        .github/workflows
        .github/ISSUE_TEMPLATE

        # IDE
        .vscode
    )

    for dir in "${dirs[@]}"; do
        mkdir -p "$PROJECT_ROOT/$dir"
        echo "  ✅ $dir"
    done
}

# 创建所有占位 __init__.py
create_init_files() {
    local init_dirs=(
        pptagent
        pptagent/agent
        pptagent/agent/prompts
        pptagent/core
        pptagent/tools
        pptagent/tools/file
        pptagent/tools/extraction
        pptagent/tools/manipulation
        pptagent/tools/insertion
        pptagent/tools/layout
        pptagent/tools/slide
        pptagent/tools/search
        pptagent/tools/utility
        pptagent/engines
        pptagent/knowledge
        pptagent/utils
        tests
        tests/unit
        tests/unit/core
        tests/unit/tools
        tests/unit/tools/file
        tests/unit/tools/extraction
        tests/unit/tools/manipulation
        tests/unit/tools/insertion
        tests/unit/tools/layout
        tests/unit/utils
        tests/integration
    )

    for dir in "${init_dirs[@]}"; do
        touch "$PROJECT_ROOT/$dir/__init__.py"
        echo "  ✅ $dir/__init__.py"
    done
}

# 创建 .gitkeep 占位文件
create_gitkeep() {
    local keep_dirs=(
        data/templates
        data/vector_db
        data/samples
        docs/api
        docs/decisions
    )

    for dir in "${keep_dirs[@]}"; do
        touch "$PROJECT_ROOT/$dir/.gitkeep"
        echo "  ✅ $dir/.gitkeep"
    done
}

echo ""
echo "📁 创建目录结构..."
create_dirs

echo ""
echo "📄 创建 __init__.py 占位文件..."
create_init_files

echo ""
echo "📄 创建 .gitkeep 占位文件..."
create_gitkeep

echo ""
echo "✅ 项目骨架创建完成！"
echo ""
echo "下一步: 运行 scripts/setup_venv.sh 创建虚拟环境并安装依赖"
```

### 3.3 关键文件初始内容

#### 3.3.1 `pptagent/__init__.py`

```python
"""
PPTAgent —— 科研PPT智能制作Agent

一个面向科研工作者的智能PPT制作Agent，能够通过自然语言交互理解用户意图，
自动调用多类工具完成PPT的读取、分析、编辑、生成、美化、保存全流程操作。
"""

__version__ = "0.1.0"
__author__ = "PPTAgent Team"
__license__ = "MIT"

from pptagent.core.exceptions import (
    PPTAgentError,
    FileNotFoundError as PPTFileNotFoundError,
    ElementNotFoundError,
    FormatNotSupportedError,
    InvalidOperationError,
    ToolExecutionError,
)

__all__ = [
    "__version__",
    "PPTAgentError",
    "PPTFileNotFoundError",
    "ElementNotFoundError",
    "FormatNotSupportedError",
    "InvalidOperationError",
    "ToolExecutionError",
]
```

#### 3.3.2 `pptagent/core/__init__.py`

```python
"""核心模块：数据模型、状态管理、格式转换"""

from pptagent.core.document import PPTDocument, Slide, Element
from pptagent.core.change_manager import ChangeManager, ChangeRecord
from pptagent.core.session import SessionState, WorkingMemory
from pptagent.core.converter import convert_ppt_to_pptx

__all__ = [
    "PPTDocument",
    "Slide",
    "Element",
    "ChangeManager",
    "ChangeRecord",
    "SessionState",
    "WorkingMemory",
    "convert_ppt_to_pptx",
]
```

#### 3.3.3 `pptagent/core/exceptions.py`

```python
"""PPTAgent 自定义异常体系

所有异常继承自 PPTAgentError 基类，外部调用者只需捕获 PPTAgentError 即可。
内部模块可精确捕获子类异常做针对性处理。
"""


class PPTAgentError(Exception):
    """PPTAgent 所有异常的基类"""
    def __init__(self, message: str = "", *, detail: dict | None = None):
        super().__init__(message)
        self.detail = detail or {}


class PPTFileNotFoundError(PPTAgentError):
    """指定的 PPT 文件不存在"""
    pass


class ElementNotFoundError(PPTAgentError):
    """指定的 PPT 要素（文本框、图片、表格等）不存在"""
    pass


class FormatNotSupportedError(PPTAgentError):
    """不支持的文件格式或要素类型"""
    pass


class InvalidOperationError(PPTAgentError):
    """非法的操作（如对不支持的元素类型执行某操作）"""
    pass


class ToolExecutionError(PPTAgentError):
    """工具执行过程中发生错误"""
    pass


class ConversionError(PPTAgentError):
    """文件格式转换失败"""
    pass


class RenderingError(PPTAgentError):
    """公式/图表/流程图渲染失败"""
    pass


class ConfigurationError(PPTAgentError):
    """配置错误"""
    pass
```

---

## 4. Python 虚拟环境与包管理

### 4.1 虚拟环境方案选型

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| `venv` + `pip` | 标准库内置，零额外依赖 | 需手动管理依赖版本 | ⭐⭐⭐⭐⭐ 推荐 |
| Poetry | 依赖锁定、构建打包一体化 | 学习成本，与 CI 集成复杂度 | ⭐⭐⭐⭐ |
| Conda | 可管理系统级库 | 环境臃肿，与 pip 混用易出问题 | ⭐⭐⭐ |

> **本项目采用 `venv` + `pip` + `pip-tools` 方案**：使用 `pip-compile` 从 `requirements.in` 生成锁定的 `requirements.txt`，兼顾简洁性和可复现性。

### 4.2 虚拟环境创建脚本

```bash
#!/bin/bash
# 文件位置: scripts/setup_venv.sh
# 用途: 创建虚拟环境并安装所有依赖
# 执行: bash scripts/setup_venv.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON="${PPTAGENT_PYTHON:-python3.11}"

echo "=========================================="
echo " PPTAgent - Python 虚拟环境设置"
echo "=========================================="
echo ""
echo "项目根目录: $PROJECT_ROOT"
echo "Python:      $PYTHON"
echo "虚拟环境:    $VENV_DIR"
echo ""

# ---------- 检查 Python 版本 ----------
REQUIRED_MAJOR=3
REQUIRED_MINOR=10

PY_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")

echo "检测到 Python 版本: $PY_VERSION"

if [ "$PY_MAJOR" -lt "$REQUIRED_MAJOR" ] || { [ "$PY_MAJOR" -eq "$REQUIRED_MAJOR" ] && [ "$PY_MINOR" -lt "$REQUIRED_MINOR" ]; }; then
    echo "❌ 需要 Python >= ${REQUIRED_MAJOR}.${REQUIRED_MINOR}，当前版本: $PY_VERSION"
    exit 1
fi

echo "✅ Python 版本检查通过"
echo ""

# ---------- 创建虚拟环境 ----------
echo "[1/4] 创建虚拟环境..."
$PYTHON -m venv "$VENV_DIR" --clear

# ---------- 激活虚拟环境并升级 pip ----------
echo "[2/4] 升级 pip 和 setuptools..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel

# ---------- 安装依赖 ----------
echo "[3/4] 安装项目依赖..."
pip install -r "$PROJECT_ROOT/requirements.txt"

# ---------- 安装开发依赖 ----------
echo "[4/4] 安装开发依赖..."
pip install -r "$PROJECT_ROOT/requirements-dev.txt"

# ---------- 以可编辑模式安装项目 ----------
echo ""
echo "以可编辑模式安装 pptagent..."
pip install -e "$PROJECT_ROOT"

# ---------- 验证安装 ----------
echo ""
echo "=========================================="
echo " 验证安装"
echo "=========================================="
echo ""

python -c "
import pptagent
print(f'✅ pptagent {pptagent.__version__} 导入成功')
"

python -c "
import python_pptx
print(f'✅ python-pptx {python_pptx.__version__} 可用')
" 2>/dev/null || echo "⚠️  python-pptx 导入检查（包名为 pptx）" && python -c "import pptx; print(f'✅ pptx 可用')"

python -c "
import PIL
print(f'✅ Pillow {PIL.__version__} 可用')
"

python -c "
import cv2
print(f'✅ OpenCV {cv2.__version__} 可用')
"

echo ""
echo "=========================================="
echo " ✅ 虚拟环境设置完成！"
echo "=========================================="
echo ""
echo "激活环境:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "验证完整环境:"
echo "  python -c 'import pptagent; print(pptagent.__version__)'"
```

### 4.3 `pyproject.toml` 完整配置

```toml
# 文件位置: pyproject.toml
# PPTAgent 项目元数据与构建配置

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pptagent"
version = "0.1.0"
description = "面向科研工作者的智能PPT制作Agent"
readme = "README.md"
license = { text = "MIT" }
authors = [
    { name = "PPTAgent Team" }
]
keywords = ["ppt", "powerpoint", "agent", "ai", "research", "academic"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Office/Business :: Office Suites",
    "Topic :: Multimedia :: Graphics :: Presentation",
]
requires-python = ">=3.10"

dependencies = [
    # 这些在 requirements.txt 中管理
    # pip-compile 会从 requirements.in 生成 requirements.txt
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-mock>=3.12",
    "pytest-asyncio>=0.23",
    "pytest-xdist>=3.5",     # 并行测试
    "black>=24.0",
    "isort>=5.13",
    "ruff>=0.3.0",
    "mypy>=1.8",
    "pre-commit>=3.6",
    "pip-tools>=7.4",
    "coverage>=7.4",
    "ipython>=8.20",
    "ipdb>=0.13",
]

[project.urls]
Homepage = "https://github.com/pptagent/pptagent"
Documentation = "https://pptagent.readthedocs.io/"
Repository = "https://github.com/pptagent/pptagent.git"
Issues = "https://github.com/pptagent/pptagent/issues"

[project.scripts]
pptagent = "pptagent.cli:main"

[tool.setuptools]
package-dir = { "" = "." }
packages = { find = { where = ["."], include = ["pptagent*"] } }

# ---------- Black（代码格式化）----------
[tool.black]
line-length = 100
target-version = ["py310", "py311"]
include = '\.pyi?$'
extend-exclude = '''
/(
    \.eggs
  | \.git
  | \.venv
  | build
  | dist
  | tests/fixtures
)/
'''

# ---------- isort（import 排序）----------
[tool.isort]
profile = "black"
line_length = 100
known_first_party = ["pptagent"]
known_third_party = [
    "pptx", "lxml", "PIL", "cv2", "numpy",
    "langchain", "langchain_anthropic", "openai",
    "pydantic", "yaml", "chromadb", "fastapi",
]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]

# ---------- Ruff（快速 Linter）----------
[tool.ruff]
line-length = 100
target-version = "py310"
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "tests/fixtures",
]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
    "TCH", # flake8-type-checking
    "RUF", # ruff-specific rules
]
ignore = [
    "E501", # line too long（由 Black 处理）
    "B008", # do not perform function calls in argument defaults
    "SIM108", # use ternary operator（有时 if/else 更清晰）
]
fixable = ["ALL"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]           # 允许未使用的 import（用于 __all__ 导出）
"tests/**/*.py" = ["S101", "F841"] # 允许 assert 和未使用变量

# ---------- mypy（类型检查）----------
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
warn_unused_ignores = true
warn_redundant_casts = true
strict_optional = true
disallow_untyped_defs = true
disallow_any_unimported = false
no_implicit_optional = true
check_untyped_defs = true
warn_no_return = true
show_error_codes = true
exclude = [
    "tests/",
    "build/",
    "dist/",
    ".venv/",
]

[[tool.mypy.overrides]]
module = [
    "pptx.*",
    "lxml.*",
    "cv2.*",
    "PIL.*",
    "numpy.*",
    "langchain.*",
    "langchain_anthropic.*",
    "chromadb.*",
    "paddleocr.*",
    "easyocr.*",
    "latex2mathml.*",
    "graphviz.*",
    "gradio.*",
    "uvicorn.*",
    "xxhash.*",
]
ignore_missing_imports = true

# ---------- pytest（测试）----------
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=pptagent",
    "--cov-report=term-missing",
    "--cov-report=html:docs/coverage",
    "--cov-report=xml:coverage.xml",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "gpu: marks tests that require GPU",
    "network: marks tests that require network access",
]

[tool.coverage.run]
source = ["pptagent"]
omit = [
    "pptagent/__init__.py",
    "*/tests/*",
    "*/test_*.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if __name__ == .__main__.:",
    "raise AssertionError",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

---

## 5. 依赖安装详解

### 5.1 依赖分层策略

```
依赖层级:
  Layer 0: 系统级（通过 apt/brew 安装的 C/C++ 库）
  Layer 1: 核心运行时（requirements.txt — 所有环境必须安装）
  Layer 2: 开发工具（requirements-dev.txt — 仅开发环境）
  Layer 3: 可选依赖（如 paddleocr-gpu 替代 paddleocr）
```

### 5.2 `requirements.txt` — 核心运行时依赖

```
# 文件位置: requirements.txt
# 自动生成自 requirements.in，请勿手动编辑
# 生成命令: pip-compile requirements.in

# ============================================================
# PPT 核心操作
# ============================================================
python-pptx==0.6.23
lxml==5.2.1
Pillow==10.3.0
olefile==0.47

# ============================================================
# Agent 框架
# ============================================================
# 选择 langchain 作为 Agent 编排框架
# 注意：如果后续发现 langchain 过度抽象，可切换为自研轻量框架
langchain==0.2.1
langchain-anthropic==0.1.16
langchain-openai==0.1.7
pydantic==2.7.1
pydantic-settings==2.3.0

# ============================================================
# 图像与 OCR
# ============================================================
opencv-python-headless==4.9.0.80   # headless 版本适用于服务器（无GUI依赖）
numpy==1.26.4
easyocr==1.7.1                      # 轻量 OCR（英文为主）
# paddleocr==2.7.3                  # 高精度 OCR（中英文）— 按需取消注释
# paddlepaddle==2.6.1               # PaddleOCR 的 CPU 后端

# ============================================================
# 公式与图表
# ============================================================
latex2mathml==3.77.0
graphviz==0.20.3
matplotlib==3.8.4
plotly==5.22.0

# ============================================================
# RAG 与搜索
# ============================================================
chromadb==0.5.0
tiktoken==0.7.0

# ============================================================
# Web 与 API
# ============================================================
fastapi==0.111.0
uvicorn[standard]==0.29.0

# ============================================================
# 演示 UI
# ============================================================
gradio==4.31.0

# ============================================================
# 基础工具
# ============================================================
pyyaml==6.0.1
rich==13.7.1
xxhash==3.4.1
python-dotenv==1.0.1
httpx==0.27.0
tenacity==8.3.0                     # 重试机制
python-slugify==8.0.4               # 生成安全的文件名/ID
```

### 5.3 `requirements-dev.txt` — 开发工具依赖

```
# 文件位置: requirements-dev.txt
# 开发工具依赖（不会被打包到最终分发中）

# ---------- 测试 ----------
pytest==8.2.0
pytest-cov==5.0.0
pytest-mock==3.14.0
pytest-asyncio==0.23.7
pytest-xdist==3.6.1
pytest-timeout==2.3.1
coverage==7.5.1

# ---------- 代码质量 ----------
black==24.4.2
isort==5.13.2
ruff==0.4.3
mypy==1.10.0
pre-commit==3.7.1

# ---------- 依赖管理 ----------
pip-tools==7.4.1

# ---------- 调试 ----------
ipython==8.24.0
ipdb==0.13.13

# ---------- 文档 ----------
mkdocs==1.6.0
mkdocs-material==9.5.24
mkdocstrings[python]==0.25.1

# ---------- 构建 ----------
build==1.2.1
twine==5.1.0
```

### 5.4 依赖安装验证脚本

```python
#!/usr/bin/env python3
"""文件位置: scripts/verify_deps.py
用途: 验证所有核心依赖是否正确安装

执行: python scripts/verify_deps.py
"""

import sys
from importlib import import_module

# (模块导入名, 显示名, 是否必需)
DEPENDENCIES = [
    # 核心
    ("pptx", "python-pptx", True),
    ("lxml", "lxml", True),
    ("PIL", "Pillow", True),
    ("olefile", "olefile", True),
    # Agent
    ("langchain", "langchain", True),
    ("langchain_anthropic", "langchain-anthropic", True),
    ("langchain_openai", "langchain-openai", True),
    ("pydantic", "pydantic", True),
    # 图像/OCR
    ("cv2", "opencv-python", True),
    ("numpy", "numpy", True),
    ("easyocr", "easyocr", False),  # 可选
    # 公式/图表
    ("graphviz", "graphviz", False),
    ("matplotlib", "matplotlib", True),
    # RAG
    ("chromadb", "chromadb", False),
    ("tiktoken", "tiktoken", False),
    # Web
    ("fastapi", "fastapi", False),
    ("uvicorn", "uvicorn", False),
    # 工具
    ("yaml", "pyyaml", True),
    ("rich", "rich", True),
    ("xxhash", "xxhash", True),
    ("httpx", "httpx", True),
]

def main():
    success = 0
    warning = 0
    failure = 0

    print("=" * 60)
    print(" PPTAgent 依赖验证")
    print("=" * 60)
    print()

    for import_name, display_name, required in DEPENDENCIES:
        try:
            mod = import_module(import_name)
            version = getattr(mod, "__version__", "?")
            print(f"  ✅ {display_name:30s} {version}")
            success += 1
        except ImportError as e:
            if required:
                print(f"  ❌ {display_name:30s} 缺失（必需）: {e}")
                failure += 1
            else:
                print(f"  ⚠️  {display_name:30s} 缺失（可选）: {e}")
                warning += 1

    print()
    print("=" * 60)
    print(f" 结果: {success} 成功, {warning} 可选缺失, {failure} 必需缺失")
    print("=" * 60)

    if failure > 0:
        print("\n❌ 请安装缺失的必需依赖: pip install -r requirements.txt")
        sys.exit(1)
    else:
        print("\n✅ 所有必需依赖已就绪！")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## 6. 代码质量基础设施

### 6.1 质量工具链总览

```
开发者提交代码
    │
    ▼
┌─────────────────────┐
│   pre-commit hook   │  ← 提交前自动运行
│                     │
│  1. ruff (lint)     │  ← 快速静态分析（~10ms）
│  2. isort (imports) │  ← 自动排序 import
│  3. black (format)  │  ← 自动格式化代码
│  4. mypy (type)     │  ← 类型检查（仅修改的文件）
└─────────┬───────────┘
          │ 通过
          ▼
┌─────────────────────┐
│   git commit        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   CI Pipeline       │  ← 完整检查
│                     │
│  1. ruff --check    │
│  2. black --check   │
│  3. isort --check   │
│  4. mypy --strict   │
│  5. pytest + cov    │
└─────────────────────┘
```

### 6.2 `.pre-commit-config.yaml`

```yaml
# 文件位置: .pre-commit-config.yaml
# 安装: pre-commit install
# 运行: pre-commit run --all-files

repos:
  # ---- 通用检查 ----
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-yaml
        args: ["--unsafe"]
      - id: check-json
      - id: check-toml
      - id: check-xml
      - id: check-added-large-files
        args: ["--maxkb=5000"]       # 禁止提交 > 5MB 的文件
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: detect-private-key
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: mixed-line-ending
        args: ["--fix=lf"]
      - id: name-tests-test
        args: ["--pytest-test-first"] # 强制 test_*.py 命名

  # ---- Ruff（快速 Lint + 自动修复）----
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.3
    hooks:
      - id: ruff
        args: ["--fix", "--exit-non-zero-on-fix"]
      - id: ruff-format

  # ---- isort（import 排序）----
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black", "--filter-files"]

  # ---- Black（代码格式化）----
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        args: ["--line-length", "100"]

  # ---- mypy（类型检查）----
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic>=2.7.0
          - types-pyyaml>=6.0
          - types-requests>=2.31
        args: ["--config-file=pyproject.toml"]
        pass_filenames: true

  # ---- 额外检查 ----
  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.28.3
    hooks:
      - id: check-github-workflows
      - id: check-dependabot
```

### 6.3 `.editorconfig`

```ini
# 文件位置: .editorconfig
# 跨编辑器统一基础格式设置

root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.{yaml,yml}]
indent_size = 2

[*.{md,rst}]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab

[*.{json,toml}]
indent_size = 2
```

### 6.4 代码质量检查脚本

```bash
#!/bin/bash
# 文件位置: scripts/run_lint.sh
# 用途: 手动运行所有代码质量检查

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

PASS=0
FAIL=0

run_check() {
    local name="$1"
    local cmd="$2"
    echo -n "🔍 $name ... "
    if eval "$cmd" 2>&1; then
        echo "✅"
        PASS=$((PASS + 1))
    else
        echo "❌"
        FAIL=$((FAIL + 1))
    fi
    echo ""
}

echo "=========================================="
echo " PPTAgent 代码质量检查"
echo "=========================================="
echo ""

run_check "Ruff (lint)"          "ruff check pptagent/ tests/"
run_check "Ruff (format check)"  "ruff format --check pptagent/ tests/"
run_check "Black (format check)" "black --check pptagent/ tests/"
run_check "isort (import check)" "isort --check-only pptagent/ tests/"
run_check "mypy (type check)"    "mypy pptagent/"

echo "=========================================="
echo " 结果: $PASS 通过, $FAIL 失败"
echo "=========================================="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
```

---

## 7. 配置管理系统

### 7.1 设计原则

1. **分层覆盖**：`default.yaml` → `development.yaml` / `production.yaml` → 环境变量
2. **类型安全**：所有配置通过 Pydantic Settings 模型校验
3. **自文档化**：每个配置项有注释说明其含义、默认值、可选值
4. **敏感信息分离**：API Key 等敏感信息通过环境变量传入，不写入配置文件

### 7.2 配置文件

#### 7.2.1 `config/default.yaml`

```yaml
# ============================================================
# PPTAgent 默认配置
# 此文件包含所有可配置项及默认值
# 环境特定覆盖请使用 development.yaml / production.yaml
# 敏感信息请使用环境变量（PPTAGENT_* 前缀）
# ============================================================

# ---- Agent 配置 ----
agent:
  # LLM 模型选择
  model: claude-sonnet-4-6          # 可选: claude-opus-4-8, gpt-4o, gpt-4-turbo
  temperature: 0.1                  # 0.0-2.0，低温度使输出更确定
  max_tokens: 4096                  # 单次响应最大 token 数

  # Agentic Loop 控制
  max_replan_count: 3               # 单任务最大重新规划次数
  max_execution_steps: 20           # 单任务最大工具调用步数
  execution_timeout_seconds: 300    # 单任务执行超时（秒）
  parallel_extraction: true         # 是否并行执行提取操作

  # 用户确认策略
  auto_confirm_readonly: true       # 只读操作无需确认
  auto_confirm_single_edit: true    # 单元素编辑无需确认
  confirm_batch_threshold: 3        # 超过此数量的编辑需确认
  confirm_delete: true              # 删除操作需确认
  confirm_save: true                # 保存/覆盖需确认
  preview_before_layout: true       # 自动布局前显示预览

# ---- 文件系统 ----
file_system:
  search_max_depth: 5               # 递归搜索最大深度（0=仅当前目录）
  supported_formats:                # 支持的PPT格式
    - .ppt
    - .pptx
    - .potx                        # PowerPoint 模板
    - .ppsx                        # PowerPoint 放映
  auto_convert_legacy: true         # 自动将 .ppt 转换为 .pptx
  libreoffice_timeout: 60           # LibreOffice 转换超时（秒）
  file_lock_enabled: true           # 打开文件时加锁
  max_file_size_mb: 200             # 最大可处理的文件大小

# ---- 提取 ----
extraction:
  # OCR 配置
  ocr_engine: easyocr               # easyocr | paddleocr | tesseract
  ocr_languages:                    # OCR 语言列表
    - en
    - ch
  ocr_confidence_threshold: 0.6     # OCR 置信度阈值（低于此值标记为不确定）

  # 图片提取
  extract_image_dpi: 300            # 默认提取DPI
  extract_image_format: png         # 默认提取格式 (png/jpg)

  # 公式提取
  formula_engine: latex             # latex | mathml | omml
  formula_fallback_to_ocr: true     # OMML解析失败时回退到OCR

  # 图表提取
  chart_extract_data: true          # 是否提取图表背后的数据
  chart_extract_image: true         # 是否同时生成图表图片快照

  # 大数据优化
  lazy_load_images: true            # 懒加载图片（大文件场景）
  max_text_length: 100000           # 单次提取文本最大字符数

# ---- 布局 ----
layout:
  # 网格系统
  grid_enabled: true
  grid_size_inches: 0.25            # 网格大小
  snap_to_grid: true                # 自动吸附到网格

  # 边距
  default_margins:                  # 默认页边距（英寸）
    left: 0.5
    right: 0.5
    top: 0.5
    bottom: 0.5

  # 间距建议
  min_element_spacing: 0.1          # 元素间最小间距
  text_line_spacing: 1.15           # 推荐行距倍数

  # 美学评分权重
  aesthetic_weights:
    alignment: 0.25
    whitespace: 0.20
    consistency: 0.20
    golden_ratio: 0.15
    color_harmony: 0.10
    visual_hierarchy: 0.10

# ---- 渲染引擎 ----
engines:
  latex:
    compiler: pdflatex               # pdflatex | xelatex | lualatex
    dpi: 300
    font_size: 12                    # 默认公式字号
    preamble: |                      # 自定义 LaTeX 导言区
      \usepackage{amsmath}
      \usepackage{amssymb}
      \usepackage{amsfonts}
      \usepackage{bm}

  mermaid:
    cli_path: mmdc                   # Mermaid CLI 路径
    theme: default                   # default | forest | dark | neutral
    scale: 2                         # 渲染缩放倍数

  graphviz:
    engine: dot                      # dot | neato | fdp | sfdp | circo
    dpi: 150
    format: png

  chart:
    backend: matplotlib              # matplotlib | plotly
    style: seaborn-v0_8-whitegrid    # matplotlib style
    dpi: 150
    color_palette: viridis           # 颜色方案

# ---- 知识库 ----
knowledge:
  rag:
    db_path: ./data/vector_db
    embedding_model: text-embedding-3-small  # OpenAI embedding 模型
    chunk_size: 500                  # 文档分块大小（tokens）
    chunk_overlap: 50                # 分块重叠（tokens）
    top_k: 5                         # 检索返回数量

  web_search:
    engine: duckduckgo               # duckduckgo | google | bing
    max_results: 5
    timeout_seconds: 10

  template_store:
    path: ./data/templates
    auto_index: true                 # 自动建立索引

# ---- 输出 ----
output:
  default_format: pptx               # 默认保存格式
  preview_dpi: 150                   # 幻灯片预览DPI
  thumbnail_size: [320, 240]         # 缩略图尺寸
  export_formats:                    # 支持的导出格式
    - pptx
    - pdf
    - png
    - jpg

# ---- 日志 ----
logging:
  level: INFO                        # DEBUG | INFO | WARNING | ERROR
  format: structured                 # structured | plain
  output:                            # 日志输出目标
    - console
    - file
  file_path: ./logs/pptagent.log     # 文件日志路径
  rotation: 10 MB                    # 日志轮转大小
  retention: 7 days                  # 日志保留时间

# ---- 安全 ----
security:
  sanitize_file_paths: true          # 过滤文件路径中的危险字符
  max_extraction_file_count: 1000    # 单次操作最大提取文件数（防止 DoS）
  allowed_image_formats:             # 允许插入的图片格式
    - png
    - jpg
    - jpeg
    - gif
    - svg
    - webp
    - bmp
```

#### 7.2.2 `config/development.yaml`

```yaml
# 开发环境覆盖配置

logging:
  level: DEBUG

agent:
  temperature: 0.3                   # 开发时稍高温度以增加多样性
  max_execution_steps: 50            # 开发时放宽限制

file_system:
  max_file_size_mb: 50               # 开发时限制文件大小以加快迭代

extraction:
  ocr_confidence_threshold: 0.4      # 开发时降低阈值

output:
  preview_dpi: 72                    # 开发时降低DPI以加快预览
```

### 7.3 Python 配置加载代码

```python
"""文件位置: pptagent/utils/config.py"""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---- 子配置模型 ----

class AgentConfig(BaseModel):
    model: str = "claude-sonnet-4-6"
    temperature: float = 0.1
    max_tokens: int = 4096
    max_replan_count: int = 3
    max_execution_steps: int = 20
    execution_timeout_seconds: int = 300
    parallel_extraction: bool = True
    auto_confirm_readonly: bool = True
    auto_confirm_single_edit: bool = True
    confirm_batch_threshold: int = 3
    confirm_delete: bool = True
    confirm_save: bool = True
    preview_before_layout: bool = True


class FileSystemConfig(BaseModel):
    search_max_depth: int = 5
    supported_formats: list[str] = [".ppt", ".pptx", ".potx", ".ppsx"]
    auto_convert_legacy: bool = True
    libreoffice_timeout: int = 60
    file_lock_enabled: bool = True
    max_file_size_mb: int = 200


class ExtractionConfig(BaseModel):
    ocr_engine: str = "easyocr"
    ocr_languages: list[str] = ["en", "ch"]
    ocr_confidence_threshold: float = 0.6
    extract_image_dpi: int = 300
    extract_image_format: str = "png"
    formula_engine: str = "latex"
    formula_fallback_to_ocr: bool = True
    chart_extract_data: bool = True
    chart_extract_image: bool = True
    lazy_load_images: bool = True
    max_text_length: int = 100000


class LayoutConfig(BaseModel):
    grid_enabled: bool = True
    grid_size_inches: float = 0.25
    snap_to_grid: bool = True
    default_margins: dict = Field(default_factory=lambda: {
        "left": 0.5, "right": 0.5, "top": 0.5, "bottom": 0.5
    })
    min_element_spacing: float = 0.1
    text_line_spacing: float = 1.15
    aesthetic_weights: dict = Field(default_factory=lambda: {
        "alignment": 0.25, "whitespace": 0.20, "consistency": 0.20,
        "golden_ratio": 0.15, "color_harmony": 0.10, "visual_hierarchy": 0.10,
    })


class Config(BaseSettings):
    """PPTAgent 全局配置"""

    model_config = SettingsConfigDict(
        env_prefix="PPTAGENT_",
        env_nested_delimiter="__",
        extra="allow",
    )

    agent: AgentConfig = Field(default_factory=AgentConfig)
    file_system: FileSystemConfig = Field(default_factory=FileSystemConfig)
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    layout: LayoutConfig = Field(default_factory=LayoutConfig)

    @classmethod
    def load(
        cls,
        env: Optional[str] = None,
        config_dir: Optional[Path] = None,
    ) -> "Config":
        """加载配置：default.yaml → {env}.yaml → 环境变量

        优先级（由低到高）:
        1. config/default.yaml
        2. config/{env}.yaml
        3. PPTAGENT_* 环境变量
        """
        if env is None:
            env = os.getenv("PPTAGENT_ENV", "development")

        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config"

        # 加载 YAML
        config_data = {}
        for config_file in ["default.yaml", f"{env}.yaml"]:
            file_path = config_dir / config_file
            if file_path.exists():
                with open(file_path) as f:
                    data = yaml.safe_load(f)
                    if data:
                        config_data = deep_merge(config_data, data)

        return cls(**config_data)


def deep_merge(base: dict, override: dict) -> dict:
    """递归合并两个字典，override 的值覆盖 base 的值"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# 全局单例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置单例"""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config(env: Optional[str] = None) -> Config:
    """重新加载配置"""
    global _config
    _config = Config.load(env=env)
    return _config
```

---

## 8. 日志系统搭建

### 8.1 设计目标

1. **结构化日志**：每条日志是合法的 JSON，方便 ELK/Loki 等日志系统采集
2. **分级控制**：不同模块可设置独立的日志级别
3. **上下文传递**：session_id、task_id 等上下文信息自动注入
4. **性能友好**：日志输出不影响主流程性能（异步写入）

### 8.2 日志模块实现

```python
"""文件位置: pptagent/utils/logger.py"""

import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---- 上下文变量（跨异步任务安全）----
session_id_ctx: ContextVar[str] = ContextVar("session_id", default="unknown")
task_id_ctx: ContextVar[str] = ContextVar("task_id", default="unknown")


class StructuredFormatter(logging.Formatter):
    """结构化 JSON 日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "session_id": session_id_ctx.get(),
            "task_id": task_id_ctx.get(),
        }

        # 合并 extra 中的自定义字段
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        # 添加异常信息
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class PlainFormatter(logging.Formatter):
    """人类可读的格式化器（开发环境用）"""

    FORMAT = (
        "%(asctime)s | %(levelname)-7s | %(name)s:%(funcName)s:%(lineno)d | "
        "%(message)s"
    )

    def __init__(self):
        super().__init__(self.FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logging(
    name: str = "pptagent",
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    structured: bool = True,
) -> logging.Logger:
    """初始化日志系统

    Args:
        name: Logger 名称
        level: 日志级别，默认从 PPTAGENT_LOG_LEVEL 环境变量读取，回退到 INFO
        log_file: 日志文件路径，为 None 则只输出到控制台
        structured: 是否使用结构化 JSON 格式

    Returns:
        配置好的 Logger 实例
    """
    if level is None:
        import os
        level = os.getenv("PPTAGENT_LOG_LEVEL", "INFO")

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 选择格式化器
    formatter = StructuredFormatter() if structured else PlainFormatter()

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件 handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 设置第三方库的日志级别
    for lib in ["urllib3", "httpx", "openai", "chromadb", "PIL", "matplotlib"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    return logger


def get_logger(name: str = "pptagent") -> logging.Logger:
    """获取 logger 实例（自动复用已有配置）"""
    return logging.getLogger(name)


# ---- 便捷函数 ----

def set_session_id(sid: Optional[str] = None) -> str:
    """设置当前会话 ID"""
    if sid is None:
        sid = uuid.uuid4().hex[:12]
    session_id_ctx.set(sid)
    return sid


def set_task_id(tid: Optional[str] = None) -> str:
    """设置当前任务 ID"""
    if tid is None:
        tid = uuid.uuid4().hex[:8]
    task_id_ctx.set(tid)
    return tid
```

### 8.3 日志使用示例

```python
# 在模块中使用
from pptagent.utils.logger import get_logger

logger = get_logger(__name__)

# 基本日志
logger.info("tool_execution_started", extra={
    "extra_fields": {
        "tool": "format_text",
        "element_id": "text_001",
        "params": {"font_size": 14, "bold": True},
    }
})

# 异常日志
try:
    result = risky_operation()
except Exception as e:
    logger.error("tool_execution_failed", exc_info=True, extra={
        "extra_fields": {
            "tool": "format_text",
            "duration_ms": 1234,
        }
    })

# 性能日志
import time
start = time.perf_counter()
do_something()
elapsed = (time.perf_counter() - start) * 1000
logger.debug("operation_completed", extra={
    "extra_fields": {"operation": "do_something", "duration_ms": elapsed}
})
```

---

## 9. 测试基础设施

### 9.1 测试策略

```
测试金字塔:
          ┌───────┐
          │  E2E  │  少量（关键端到端流程）
          ├───────┤
          │ 集成  │  中等（工具链组合）
          ├───────┤
          │ 单元  │  大量（每个函数/方法）
          └───────┘

覆盖率目标:
  - 核心模块 (pptagent/core):     ≥ 90%
  - 工具模块 (pptagent/tools):    ≥ 85%
  - 引擎模块 (pptagent/engines):  ≥ 75%
  - 整体:                         ≥ 80%
```

### 9.2 `tests/conftest.py`

```python
"""pytest 全局 fixtures 和配置"""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# ---- 确保测试环境变量 ----
os.environ["PPTAGENT_ENV"] = "testing"
os.environ["PPTAGENT_LOG_LEVEL"] = "WARNING"


@pytest.fixture(scope="session")
def project_root() -> Path:
    """项目根目录"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def fixtures_dir(project_root: Path) -> Path:
    """测试数据目录"""
    return project_root / "tests" / "fixtures"


@pytest.fixture(scope="session")
def sample_simple_pptx(fixtures_dir: Path) -> Path:
    """简单 PPT 测试文件"""
    path = fixtures_dir / "sample_simple.pptx"
    if not path.exists():
        pytest.skip(f"测试文件不存在: {path}")
    return path


@pytest.fixture(scope="session")
def sample_complex_pptx(fixtures_dir: Path) -> Path:
    """复杂 PPT 测试文件"""
    path = fixtures_dir / "sample_complex.pptx"
    if not path.exists():
        pytest.skip(f"测试文件不存在: {path}")
    return path


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """临时目录（测试后自动清理）"""
    with tempfile.TemporaryDirectory(prefix="pptagent_test_") as tmp:
        yield Path(tmp)


@pytest.fixture
def temp_pptx(temp_dir: Path, sample_simple_pptx: Path) -> Path:
    """复制测试 PPT 到临时目录，避免修改原始文件"""
    import shutil
    dest = temp_dir / "test_copy.pptx"
    shutil.copy(sample_simple_pptx, dest)
    return dest


@pytest.fixture(autouse=True)
def reset_config():
    """每个测试前重置配置"""
    from pptagent.utils.config import reload_config
    reload_config("testing")
    yield
    reload_config("testing")


@pytest.fixture(autouse=True)
def reset_session_context():
    """每个测试前重置日志上下文"""
    from pptagent.utils.logger import set_session_id, set_task_id
    set_session_id("test-session")
    set_task_id("test-task")
```

### 9.3 示例单元测试

```python
"""文件位置: tests/unit/core/test_change_manager.py"""

import pytest
from pptagent.core.change_manager import ChangeManager, ChangeRecord


class TestChangeManager:
    def test_record_and_undo(self):
        """测试记录变更并撤销"""
        cm = ChangeManager(max_history=100)

        record = ChangeRecord(
            id="chg_001",
            timestamp=None,
            operation="format_text",
            target_element="text_001",
            before_state={"font_size": 12},
            after_state={"font_size": 14},
            slide_index=0,
        )
        cm.record(record)

        assert len(cm.undo_stack) == 1
        assert len(cm.redo_stack) == 0

        undone = cm.undo()
        assert undone is not None
        assert undone.id == "chg_001"
        assert len(cm.undo_stack) == 0
        assert len(cm.redo_stack) == 1

    def test_undo_empty_stack(self):
        """测试空栈撤销"""
        cm = ChangeManager()
        assert cm.undo() is None

    def test_redo_empty_stack(self):
        """测试空栈重做"""
        cm = ChangeManager()
        assert cm.redo() is None

    def test_max_history(self):
        """测试历史记录上限"""
        cm = ChangeManager(max_history=3)

        for i in range(5):
            cm.record(ChangeRecord(
                id=f"chg_{i:03d}",
                timestamp=None,
                operation="test",
                target_element=f"elem_{i}",
                before_state=None,
                after_state=None,
                slide_index=0,
            ))

        assert len(cm.undo_stack) == 3  # 被截断为3
        assert cm.undo_stack[0].id == "chg_002"  # 最早的记录被丢弃

    def test_redo_cleared_on_new_record(self):
        """测试新记录清除 redo 栈"""
        cm = ChangeManager()

        r1 = ChangeRecord(id="1", timestamp=None, operation="a",
                          target_element="e", before_state=None,
                          after_state=None, slide_index=0)
        cm.record(r1)
        cm.undo()

        assert len(cm.redo_stack) == 1

        r2 = ChangeRecord(id="2", timestamp=None, operation="b",
                          target_element="e", before_state=None,
                          after_state=None, slide_index=0)
        cm.record(r2)

        assert len(cm.redo_stack) == 0  # redo 栈被清空
```

### 9.4 测试运行脚本

```bash
#!/bin/bash
# 文件位置: scripts/run_tests.sh

set -euo pipefail
cd "$(dirname "$0")/.."

echo "=========================================="
echo " PPTAgent 测试执行"
echo "=========================================="

# 参数解析
COVERAGE="--cov=pptagent"
MARKERS=""
VERBOSE="-v"

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cov)    COVERAGE=""; shift ;;
        --integration) MARKERS="-m integration"; shift ;;
        --slow)       MARKERS="-m 'slow or integration'"; shift ;;
        -x)           VERBOSE="-x"; shift ;;  # 遇错停止
        *)            break ;;
    esac
done

# 执行测试
pytest $VERBOSE $COVERAGE $MARKERS \
    --cov-report=term-missing \
    --cov-report=html:docs/coverage \
    --cov-report=xml:coverage.xml \
    tests/ "$@"
```

---

## 10. Git 仓库与版本控制规范

### 10.1 `.gitignore`

```gitignore
# 文件位置: .gitignore

# ---- Python ----
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
dist/
build/
eggs/
*.egg
.eggs/

# ---- 虚拟环境 ----
.venv/
venv/
env/
.env

# ---- IDE ----
.vscode/
!.vscode/settings.json
!.vscode/extensions.json
!.vscode/launch.json
.idea/
*.swp
*.swo
*~

# ---- 测试与覆盖率 ----
.coverage
htmlcov/
docs/coverage/
coverage.xml
.pytest_cache/
.tox/

# ---- 日志 ----
logs/
*.log

# ---- 数据 ----
data/vector_db/*
!data/vector_db/.gitkeep
*.db
*.sqlite3

# ---- 临时文件 ----
*.tmp
*.bak
*.swp
.DS_Store
Thumbs.db

# ---- 环境变量 ----
.env
.env.*

# ---- 构建产物 ----
*.whl
*.tar.gz

# ---- Jupyter ----
.ipynb_checkpoints/
*.ipynb

# ---- mypy ----
.mypy_cache/
```

### 10.2 `.gitattributes`

```gitattributes
# 文件位置: .gitattributes
# 统一换行符处理

* text=auto eol=lf

# 二进制文件
*.pptx binary
*.ppt binary
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.pdf binary
*.whl binary
*.tar.gz binary

# 总是以 LF 换行
*.py text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
*.json text eol=lf
*.toml text eol=lf
*.md text eol=lf
*.sh text eol=lf
*.cfg text eol=lf

# 脚本文件可执行
scripts/*.sh text eol=lf
```

### 10.3 Git 分支策略

```
main (保护分支，仅通过 PR 合并)
  │
  ├── develop (日常开发集成分支)
  │     │
  │     ├── feature/xxx (功能分支，从 develop 切出)
  │     ├── fix/xxx     (修复分支)
  │     └── refactor/xxx(重构分支)
  │
  └── release/x.y.z (发布分支，从 develop 切出)
```

#### 分支命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能 | `feature/<phase>-<desc>` | `feature/phase1-file-finder` |
| 修复 | `fix/<issue-id>-<desc>` | `fix/42-ocr-timeout` |
| 重构 | `refactor/<scope>` | `refactor/extraction-pipeline` |
| 发布 | `release/<version>` | `release/0.1.0` |
| 紧急修复 | `hotfix/<desc>` | `hotfix/security-patch` |

### 10.4 Commit Message 规范

采用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**：

| Type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `refactor` | 重构（不改变功能） |
| `docs` | 文档更新 |
| `test` | 测试添加或修改 |
| `chore` | 构建/工具变更 |
| `perf` | 性能优化 |
| `style` | 代码格式（不影响逻辑） |
| `ci` | CI/CD 变更 |

**范围 (scope)**：模块名，如 `core`, `tools`, `agent`, `engines`, `config`

**示例**：

```
feat(tools): implement find_ppt_files with regex support

- Add recursive directory search
- Support .ppt, .pptx, .potx, .ppsx extensions
- Add unit tests with 95% coverage

Closes #12
```

### 10.5 Git Hooks 安装

```bash
# 安装 pre-commit hooks（首次克隆后执行）
pre-commit install

# 安装 commit-msg hook（可选：验证 commit message 格式）
pre-commit install --hook-type commit-msg

# 手动对所有文件运行
pre-commit run --all-files
```

---

## 11. CI/CD Pipeline

### 11.1 GitHub Actions 主流水线

```yaml
# 文件位置: .github/workflows/ci.yaml

name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:  # 允许手动触发

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  PYTHON_VERSION: "3.11"

jobs:
  # =============================================
  # Job 1: 代码质量检查（Lint + Format + Type）
  # =============================================
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install ruff black isort mypy
          pip install pydantic types-pyyaml types-requests

      - name: Ruff (lint)
        run: ruff check pptagent/ tests/

      - name: Ruff (format)
        run: ruff format --check pptagent/ tests/

      - name: Black (format)
        run: black --check pptagent/ tests/

      - name: isort (imports)
        run: isort --check-only pptagent/ tests/

      - name: mypy (type check)
        run: mypy pptagent/

  # =============================================
  # Job 2: 测试（多 Python 版本矩阵）
  # =============================================
  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-22.04
    needs: lint
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11"]

    steps:
      - uses: actions/checkout@v4

      - name: Install system dependencies
        run: |
          sudo apt-get update -qq
          sudo apt-get install -y -qq \
            libreoffice-impress \
            poppler-utils \
            graphviz

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pip install -e .

      - name: Run tests with coverage
        run: |
          pytest \
            -v \
            --tb=short \
            --cov=pptagent \
            --cov-report=term-missing \
            --cov-report=xml:coverage.xml \
            --timeout=60 \
            tests/

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: python-${{ matrix.python-version }}
          fail_ci_if_error: false

  # =============================================
  # Job 3: 构建验证
  # =============================================
  build:
    name: Build Check
    runs-on: ubuntu-22.04
    needs: test
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Build package
        run: |
          pip install build
          python -m build

      - name: Check package
        run: |
          pip install twine
          twine check dist/*

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

### 11.2 Dependabot 配置

```yaml
# 文件位置: .github/dependabot.yaml

version: 2
updates:
  # Python 依赖
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Shanghai"
    labels:
      - "dependencies"
      - "python"
    assignees:
      - "pptagent-team"
    versioning-strategy: increase-if-necessary

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    labels:
      - "dependencies"
      - "ci"
```

---

## 12. 文档基础设施

### 12.1 MkDocs 配置

```yaml
# 文件位置: mkdocs.yml

site_name: PPTAgent Documentation
site_description: 面向科研工作者的智能PPT制作Agent
site_author: PPTAgent Team
repo_url: https://github.com/pptagent/pptagent

theme:
  name: material
  language: zh
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: 切换暗色模式
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: 切换亮色模式
  features:
    - navigation.sections
    - navigation.expand
    - search.highlight
    - content.code.copy

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [.]
          options:
            show_source: true
            show_root_heading: true

nav:
  - 首页: index.md
  - 架构:
    - 总体架构: architecture.md
    - Agentic Loop: agentic_loop.md
    - 工具系统: tools.md
  - 指南:
    - 快速开始: guides/getting_started.md
    - 工具开发: guides/tool_development.md
    - 添加新工具: guides/adding_tools.md
  - API 参考:
    - pptagent.core: api/core.md
    - pptagent.tools: api/tools.md
  - 架构决策记录:
    - ADR 索引: decisions/index.md
```

### 12.2 README.md 模板

```markdown
# PPTAgent

面向科研工作者的智能PPT制作Agent。

[![CI](https://github.com/pptagent/pptagent/actions/workflows/ci.yaml/badge.svg)](https://github.com/pptagent/pptagent/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/pptagent/pptagent/branch/main/graph/badge.svg)](https://codecov.io/gh/pptagent/pptagent)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 快速开始

```bash
# 1. 安装系统依赖
bash scripts/install_system_deps.sh

# 2. 创建虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate

# 3. 安装项目
pip install -e ".[dev]"

# 4. 验证安装
python -c "import pptagent; print(pptagent.__version__)"
```

## 文档

完整文档请访问: https://pptagent.readthedocs.io/

## 开发

请参阅 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解贡献指南。

## 许可证

MIT License. 详见 [LICENSE](./LICENSE)。
```

---

## 13. 开发辅助脚本

### 13.1 `Makefile`（便捷命令入口）

```makefile
# 文件位置: Makefile
# PPTAgent 开发便捷命令

.PHONY: help install test lint format clean docs

help:  ## 显示所有可用命令
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 安装所有依赖（含开发依赖）
	bash scripts/install_system_deps.sh
	bash scripts/setup_venv.sh
	pre-commit install

test:  ## 运行所有测试
	bash scripts/run_tests.sh

test-fast:  ## 运行快速测试（跳过慢速/集成测试）
	pytest -v -m "not slow and not integration" tests/

lint:  ## 运行所有代码质量检查
	bash scripts/run_lint.sh

format:  ## 自动格式化代码
	ruff format pptagent/ tests/
	ruff check --fix pptagent/ tests/
	isort pptagent/ tests/

typecheck:  ## 仅运行类型检查
	mypy pptagent/

clean:  ## 清理临时文件
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	rm -rf docs/coverage coverage.xml
	rm -rf dist build
	bash scripts/clean.sh

docs:  ## 构建文档
	mkdocs build

docs-serve:  ## 启动文档本地服务器
	mkdocs serve

shell:  ## 进入开发 IPython Shell
	ipython -c "import pptagent; print(f'PPTAgent {pptagent.__version__}')" -i

check-all: lint test  ## 运行完整检查（lint + test）
```

### 13.2 `scripts/clean.sh`

```bash
#!/bin/bash
# 文件位置: scripts/clean.sh
# 清理所有临时文件和缓存

set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🧹 清理临时文件..."

# Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# 测试
rm -rf .pytest_cache .coverage htmlcov coverage.xml 2>/dev/null || true

# Lint
rm -rf .mypy_cache .ruff_cache 2>/dev/null || true

# 日志
rm -rf logs/*.log 2>/dev/null || true

# LibreOffice 锁文件
find . -name ".~lock.*" -delete 2>/dev/null || true

echo "✅ 清理完成"
```

---

## 14. IDE 集成配置

### 14.1 `.vscode/settings.json`

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests", "-v", "--tb=short"],
    "python.testing.unittestEnabled": false,
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.diagnosticMode": "workspace",
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit",
            "source.fixAll.ruff": "explicit"
        }
    },
    "black-formatter.args": ["--line-length", "100"],
    "isort.args": ["--profile", "black"],
    "ruff.lint.args": ["--config", "pyproject.toml"],
    "mypy-type-checker.args": ["--config-file", "pyproject.toml"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/.ruff_cache": true,
        "**/*.egg-info": true
    },
    "files.watcherExclude": {
        "**/.git/objects/**": true,
        "**/.git/subtree-cache/**": true,
        "**/.venv/**": true,
        "**/node_modules/**": true,
        "**/data/vector_db/**": true
    }
}
```

### 14.2 `.vscode/extensions.json`

```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "ms-python.isort",
        "charliermarsh.ruff",
        "ms-python.mypy-type-checker",
        "tamasfe.even-better-toml",
        "redhat.vscode-yaml",
        "yzhang.markdown-all-in-one",
        "bierner.markdown-mermaid",
        "github.vscode-github-actions"
    ]
}
```

### 14.3 `.vscode/launch.json`

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "PPTAGENT_ENV": "development",
                "PPTAGENT_LOG_LEVEL": "DEBUG"
            }
        },
        {
            "name": "pytest: Current File",
            "type": "debugpy",
            "request": "launch",
            "module": "pytest",
            "args": ["-v", "--tb=long", "${file}"],
            "console": "integratedTerminal"
        },
        {
            "name": "pytest: All Tests",
            "type": "debugpy",
            "request": "launch",
            "module": "pytest",
            "args": ["-v", "--tb=long", "tests/"],
            "console": "integratedTerminal"
        }
    ]
}
```

---

## 15. 验证清单与冒烟测试

### 15.1 Phase 0 完成验证清单

```bash
#!/bin/bash
# 文件位置: scripts/verify_phase0.sh
# 用途: 全面验证 Phase 0 基础设施是否正确搭建
# 执行: bash scripts/verify_phase0.sh

set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    local condition="$2"
    local severity="${3:-required}"  # required | optional

    echo -n "  [$severity] $name ... "
    if eval "$condition" 2>/dev/null; then
        echo "✅"
        PASS=$((PASS + 1))
    else
        if [ "$severity" = "required" ]; then
            echo "❌"
            FAIL=$((FAIL + 1))
        else
            echo "⚠️"
            WARN=$((WARN + 1))
        fi
    fi
}

echo "=========================================="
echo " Phase 0 验证清单"
echo "=========================================="
echo ""

# ---- 1. 目录结构 ----
echo "📁 1. 目录结构完整性"
check "主包 pptagent/"               "[ -d pptagent ]"
check "核心模块 pptagent/core/"      "[ -d pptagent/core ]"
check "工具模块 pptagent/tools/"     "[ -d pptagent/tools ]"
check "Agent模块 pptagent/agent/"    "[ -d pptagent/agent ]"
check "引擎模块 pptagent/engines/"   "[ -d pptagent/engines ]"
check "配置目录 config/"             "[ -d config ]"
check "测试目录 tests/"              "[ -d tests ]"
check "脚本目录 scripts/"            "[ -d scripts ]"
check "数据目录 data/"               "[ -d data ]"
check "文档目录 docs/"               "[ -d docs ]"
check "__init__.py 存在"             "[ -f pptagent/__init__.py ]"
echo ""

# ---- 2. Python 环境 ----
echo "🐍 2. Python 环境"
PY_VER=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
check "Python 版本 >= 3.10"          "python -c 'import sys; assert sys.version_info >= (3,10)'"
check "虚拟环境已激活"               "[ -n \"${VIRTUAL_ENV:-}\" ]" "optional"
check "pip 可用"                     "pip --version &>/dev/null" echo ""

# ---- 3. 核心依赖 ----
echo "📦 3. 核心依赖"
check "pptagent 可导入"              "python -c 'import pptagent'"
check "pptagent.__version__ 存在"    "python -c 'from pptagent import __version__; assert __version__'"
check "python-pptx (pptx) 可用"      "python -c 'import pptx'"
check "Pillow (PIL) 可用"            "python -c 'import PIL'"
check "pydantic 可用"                "python -c 'import pydantic'"
check "pyyaml 可用"                  "python -c 'import yaml'"
check "rich 可用"                    "python -c 'import rich'" "optional"
echo ""

# ---- 4. 配置文件 ----
echo "⚙️  4. 配置文件"
check "default.yaml 存在"            "[ -f config/default.yaml ]"
check "development.yaml 存在"        "[ -f config/development.yaml ]"
check "default.yaml 是合法 YAML"     "python -c 'import yaml; yaml.safe_load(open(\"config/default.yaml\"))'"
echo ""

# ---- 5. 代码质量工具 ----
echo "🔧 5. 代码质量工具"
check "ruff 可用"                    "ruff --version &>/dev/null" "optional"
check "black 可用"                   "black --version &>/dev/null" "optional"
check "isort 可用"                   "isort --version &>/dev/null" "optional"
check "mypy 可用"                    "mypy --version &>/dev/null" "optional"
check "pre-commit 可用"              "pre-commit --version &>/dev/null" "optional"
echo ""

# ---- 6. 测试框架 ----
echo "🧪 6. 测试框架"
check "pytest 可用"                  "pytest --version &>/dev/null" "optional"
check "conftest.py 存在"             "[ -f tests/conftest.py ]"
check "pytest 可发现测试"            "pytest --collect-only tests/ &>/dev/null" "optional"
echo ""

# ---- 7. Git 配置 ----
echo "📝 7. Git 配置"
check ".gitignore 存在"              "[ -f .gitignore ]"
check ".gitattributes 存在"          "[ -f .gitattributes ]"
check ".editorconfig 存在"           "[ -f .editorconfig ]"
check "pre-commit-config 存在"       "[ -f .pre-commit-config.yaml ]" "optional"
echo ""

# ---- 8. 系统依赖 (可选) ----
echo "💻 8. 系统依赖"
check "LibreOffice 可用"             "libreoffice --headless --version &>/dev/null" "optional"
check "Graphviz 可用"                "dot -V &>/dev/null" "optional"
check "FFmpeg 可用"                  "ffmpeg -version &>/dev/null" "optional"
echo ""

# ---- 输出结果 ----
echo "=========================================="
echo " 验证结果: $PASS 通过, $FAIL 失败, $WARN 可选缺失"
echo "=========================================="

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "❌ 有 $FAIL 项必需检查未通过，请修复后重新运行本脚本。"
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo ""
    echo "⚠️  有 $WARN 项可选依赖缺失（不影响核心功能，但建议安装）。"
    echo "   运行 scripts/setup_venv.sh 安装所有开发依赖。"
    exit 0
else
    echo ""
    echo "🎉 所有检查通过！Phase 0 基础设施搭建完成。"
    exit 0
fi
```

### 15.2 冒烟测试

```python
#!/usr/bin/env python3
"""文件位置: scripts/smoke_test.py
用途: 快速冒烟测试，验证核心链路可通
"""

import sys
from pathlib import Path

# 确保项目在 path 中
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """测试所有核心模块可导入"""
    from pptagent import __version__
    assert __version__ == "0.1.0", f"版本号异常: {__version__}"

    from pptagent.core.exceptions import PPTAgentError
    assert issubclass(PPTAgentError, Exception)


def test_config_load():
    """测试配置加载"""
    from pptagent.utils.config import Config

    config = Config.load(env="development")
    assert config.agent.model is not None
    assert config.agent.temperature >= 0
    assert config.file_system.search_max_depth > 0
    print(f"  ✅ Config loaded: model={config.agent.model}")


def test_logger():
    """测试日志系统"""
    from pptagent.utils.logger import setup_logging, get_logger

    logger = setup_logging(name="smoke_test", structured=False)
    logger.info("Smoke test log message")
    print("  ✅ Logger works")


def test_document_import():
    """测试 pptx 库可用"""
    try:
        from pptx import Presentation
        print("  ✅ python-pptx available")
    except ImportError as e:
        print(f"  ❌ python-pptx not available: {e}")
        return False
    return True


def main():
    print("=" * 50)
    print(" PPTAgent Smoke Test")
    print("=" * 50)
    print()

    tests = [
        ("Import check", test_imports),
        ("Config load", test_config_load),
        ("Logger", test_logger),
        ("python-pptx", test_document_import),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f"🔍 {name}...")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f" Results: {passed} passed, {failed} failed")
    print("=" * 50)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## 16. 常见问题与故障排除

### 16.1 系统依赖问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `fatal error: Python.h: No such file or directory` | 缺少 Python 开发头文件 | `sudo apt-get install python3-dev` |
| `error: libjpeg.h: No such file or directory` | 缺少 JPEG 开发库 | `sudo apt-get install libjpeg-dev` |
| `ImportError: libGL.so.1: cannot open shared object file` | 缺少 OpenGL 库 | `sudo apt-get install libgl1-mesa-glx` |
| LibreOffice 转换超时 | 文件过大或 LibreOffice 未正确安装 | `libreoffice --headless --version` 检查版本 |
| `mmdc: command not found` | Mermaid CLI 未安装 | `npm install -g @mermaid-js/mermaid-cli` |

### 16.2 Python 环境问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `pip install python-pptx` 失败 | lxml 编译缺少依赖 | `sudo apt-get install libxml2-dev libxslt1-dev` |
| `pip install opencv-python` 失败 | 缺少编译工具链 | `sudo apt-get install build-essential cmake` |
| `paddleocr` 安装后导入失败 | 依赖冲突 | 使用 `easyocr` 替代（`export OCR_ENGINE=easyocr`） |
| 虚拟环境中 `python` 指向系统 Python | venv 未正确激活 | 确认使用 `.venv/bin/python` 或 `source .venv/bin/activate` |

### 16.3 pre-commit 问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `pre-commit: command not found` | pre-commit 未安装 | `pip install pre-commit` |
| hooks 运行非常慢 | 首次运行需要下载依赖 | 等待首次完成，后续使用缓存 |
| mypy hook 报大量第三方库错误 | 第三方库 stub 缺失 | 已在 pyproject.toml 配置 `ignore_missing_imports` |

### 16.4 快速诊断命令

```bash
# 全面诊断环境
python scripts/verify_deps.py

# 单独检查某个模块
python -c "import pptx; print('pptx OK')"
python -c "import cv2; print('OpenCV OK')"
python -c "import PIL; print('Pillow OK')"

# 检查 LibreOffice
libreoffice --headless --version

# 检查 Graphviz
dot -V

# 查看 Python 路径
which python
python --version

# 查看已安装包的版本
pip list | grep -E "pptx|pillow|opencv|langchain|pydantic"
```

---

## 附录 A：Phase 0 每日任务分解（建议）

| 天数 | 任务 | 产出 |
|------|------|------|
| Day 1 | 环境准备：安装系统依赖、Python、Node.js | 开发机环境就绪 |
| Day 2 | 项目骨架：创建目录结构、`__init__.py`、占位文件 | `tree PPTAgent/` 符合预期 |
| Day 3 | 虚拟环境：创建 venv、安装核心依赖、验证导入 | `requirements.txt` 全部安装成功 |
| Day 4 | 配置系统：编写 `default.yaml`、`Config.load()`、环境变量支持 | Python 可加载配置 |
| Day 5 | 日志系统：实现 `StructuredFormatter`、`setup_logging()` | 结构化日志输出 |
| Day 6 | 代码质量：配置 Black/isort/Ruff/mypy、`.pre-commit-config.yaml` | `pre-commit run --all-files` 通过 |
| Day 7 | 测试框架：`conftest.py`、编写占位测试、pytest 可运行 | `pytest` 发现测试 |
| Day 8 | Git 仓库：`.gitignore`、分支保护、Conventional Commits | 仓库规范就绪 |
| Day 9 | CI/CD：编写 GitHub Actions workflow、Dependabot | 首个 PR 触发 CI |
| Day 10 | 文档：README、CONTRIBUTING、MkDocs 配置 | 文档框架可用 |
| Day 11-12 | 补充与验证：完善所有缺失、运行验证脚本、修复问题 | `verify_phase0.sh` 全绿 |
| Day 13-14 | Buffer：应对意外问题、团队知识传递 | Phase 0 sign-off |

## 附录 B：Phase 0 完成后的第一个 Commit

```bash
# Phase 0 完成后，建议按以下顺序提交：

git add scripts/install_system_deps.sh scripts/setup_venv.sh
git commit -m "chore: add system dependency and venv setup scripts"

git add pyproject.toml requirements.txt requirements-dev.txt
git commit -m "chore: add Python package configuration and dependencies"

git add config/ pptagent/utils/config.py
git commit -m "feat(config): implement layered configuration system"

git add pptagent/utils/logger.py
git commit -m "feat(logger): implement structured logging system"

git add pptagent/core/exceptions.py pptagent/__init__.py
git commit -m "feat(core): add exception hierarchy and package init"

git add .pre-commit-config.yaml .editorconfig .gitignore .gitattributes
git commit -m "chore: add code quality and git configuration"

git add .github/
git commit -m "ci: add GitHub Actions CI pipeline and Dependabot config"

git add tests/conftest.py tests/unit/core/test_change_manager.py
git commit -m "test: add test infrastructure and example unit tests"

git add README.md CONTRIBUTING.md mkdocs.yml docs/
git commit -m "docs: add project documentation and mkdocs setup"

git add .
git commit -m "chore: complete Phase 0 infrastructure setup"
```

---

> **下一步**: Phase 0 验证通过后，进入 [Phase 1: 文件系统与基础PPT操作](./plan_0.md#phase-1-文件系统与基础ppt操作2-3周)，开始实现 T01-T05 文件工具和 PPTDocument 内存模型。

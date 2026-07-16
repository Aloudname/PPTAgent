# PPTAgent

面向科研工作者的智能PPT制作Agent。

[![CI](https://github.com/pptagent/pptagent/actions/workflows/ci.yaml/badge.svg)](https://github.com/pptagent/pptagent/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/pptagent/pptagent/branch/main/graph/badge.svg)](https://codecov.io/gh/pptagent/pptagent)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 简介

PPTAgent 是一个面向科研工作者的智能 PPT 制作 Agent，能够通过自然语言交互理解用户意图，自动调用多类工具完成 PPT 的**读取、分析、编辑、生成、美化、保存**全流程操作。

## 快速开始

### 前置条件

- [Miniforge](https://github.com/conda-forge/miniforge) (conda 环境管理)
- Node.js >= 18 (Mermaid CLI 渲染流程图)

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/pptagent/pptagent.git
cd PPTAgent

# 2. 创建 conda 环境（一条命令安装所有依赖）
conda env create -f environment.yml

# 3. 激活环境
conda activate pptagent

# 4. 以可编辑模式安装项目
pip install -e . --no-deps

# 5. 安装 pre-commit hooks
pre-commit install

# 6. 验证安装
python -c "import pptagent; print(pptagent.__version__)"
# 输出: 0.1.0
```

### 快速测试

```bash
# 运行测试套件
pytest tests/ -v

# 运行代码质量检查
make lint
```

## 项目结构

```
PPTAgent/
├── pptagent/          # 主 Python 包
│   ├── agent/         # Agent 编排层（Planner/Executor/Evaluator/Reflector）
│   ├── core/          # 核心数据模型与状态管理
│   ├── tools/         # 工具层（45个工具，6大类）
│   ├── engines/       # 底层渲染引擎
│   ├── knowledge/     # RAG 检索与联网搜索
│   └── utils/         # 通用工具
├── config/            # 配置文件
├── tests/             # 测试套件
├── scripts/           # 辅助脚本
├── docs/              # 文档
└── environment.yml    # Conda 环境描述
```

## 开发

请参阅 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解贡献指南。

### 常用命令

| 命令 | 说明 |
|------|------|
| `make install` | 创建/更新 conda 环境 |
| `make test` | 运行所有测试 |
| `make lint` | 运行代码质量检查 |
| `make format` | 自动格式化代码 |
| `make docs-serve` | 启动文档服务器 |

## 文档

完整文档请访问: https://pptagent.readthedocs.io/

## 许可证

MIT License. 详见 [LICENSE](./LICENSE).

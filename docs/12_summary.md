# PPTAgent 项目阶段总结与后续规划

> **日期**: 2026-07-15
> **状态**: Phase 0 ✅ | Phase 1 ✅ | Phase 2 ✅ | Phase 3 ✅ | Phase 4–8 ⬜

---

## 目录

1. [总体进度概览](#1-总体进度概览)
2. [分层盘点：基础设施层](#2-分层盘点基础设施层)
3. [分层盘点：核心层 (core)](#3-分层盘点核心层-core)
4. [分层盘点：工具层 (tools)](#4-分层盘点工具层-tools)
5. [分层盘点：引擎层与知识层](#5-分层盘点引擎层与知识层)
6. [分层盘点：测试层](#6-分层盘点测试层)
7. [分层盘点：文档与运维](#7-分层盘点文档与运维)
8. [差距分析：已完成 vs 计划](#8-差距分析已完成-vs-计划)
9. [下一步：Phase 2 要素提取](#9-下一步phase-2-要素提取)
10. [中期方向：Phase 3–5](#10-中期方向phase-35)
11. [远期愿景：Phase 6–8](#11-远期愿景phase-68)

---

## 1. 总体进度概览

```
Phase 0  ████████████████████ 100%  基础设施搭建        ✅
Phase 1  ████████████████████ 100%  文件系统与基础操作    ✅
Phase 2  ████████████████████ 100%  要素提取            ✅
Phase 3  ████████████████████ 100%  要素编辑            ✅
Phase 4  ░░░░░░░░░░░░░░░░░░░░   0%  高级内容创建
Phase 5  ░░░░░░░░░░░░░░░░░░░░   0%  布局优化
Phase 6  ░░░░░░░░░░░░░░░░░░░░   0%  Agentic Loop 集成
Phase 7  ░░░░░░░░░░░░░░░░░░░░   0%  知识增强
Phase 8  ░░░░░░░░░░░░░░░░░░░░   0%  UI/UX 与交付
```

| 指标          | 数值                       |
| ------------- | -------------------------- |
| Python 源文件 | 47 个（~5,000 行）          |
| 测试文件      | 22 个（~2,500 行）          |
| 测试用例      | 150 个（全部通过）          |
| 代码覆盖率    | 80%                        |
| MyPy          | 零错误通过                  |
| 文档          | 6,800+ 行（5 份文档）       |

---

## 2. 分层盘点：基础设施层

### 2.1 项目骨架

```
PPTAgent/
├── pptagent/          ✅ 主包（8 个子包，含 __init__.py）
├── tests/             ✅ 测试目录（unit + integration + fixtures）
├── config/            ✅ 配置目录（default.yaml + development.yaml）
├── scripts/           ✅ 10 个辅助脚本
├── docs/              ✅ 4 份文档
├── data/              ✅ 模板/向量数据库/样例目录（空，待填充）
├── .github/workflows/ ✅ CI/CD pipeline（conda 版）
└── .vscode/           ✅ IDE 配置
```

### 2.2 构建与依赖管理

| 文件                                | 状态 | 说明                                                            |
| ----------------------------------- | :--: | --------------------------------------------------------------- |
| `pyproject.toml` (224 行)         |  ✅  | setuptools 构建 + Black/isort/Ruff/mypy/pytest 全配置           |
| `environment.yml` (162 行)        |  ✅  | conda 精简方案（18 个 C 库 + 50 个 pip 包），mamba 可秒解       |
| `Makefile` (78 行)                |  ✅  | 15 个便捷命令（install/test/lint/format/docs/shell...）         |
| `.pre-commit-config.yaml`         |  ✅  | 8 个 hooks（yaml/json/toml 检查 + ruff + isort + black + mypy） |
| `.editorconfig`                   |  ✅  | 统一缩进/换行符/编码                                            |
| `.gitignore` / `.gitattributes` |  ✅  | Python/conda/IDE 全覆盖                                         |

### 2.3 配置系统 — `pptagent/utils/config.py`（205 行）

```
Config (BaseSettings) — 三层覆盖（default.yaml → {env}.yaml → PPTAGENT_* 环境变量）
├── AgentConfig        — 模型/温度/token 数/Agentic Loop 控制/用户确认策略
├── FileSystemConfig   — 搜索深度/支持格式/转换超时/文件锁/大小限制
├── ExtractionConfig   — OCR 引擎/DPI/公式引擎/懒加载/文本长度限制
├── LayoutConfig       — 网格/边距/间距/美学权重
└── LoggingConfig      — 级别/格式/输出目标/轮转/保留
```

**特性**：Pydantic Settings 校验、`get_config()` 全局单例、`_deep_merge` 递归合并。

### 2.4 日志系统 — `pptagent/utils/logger.py`（142 行）

| 组件                                     | 功能                                                  |
| ---------------------------------------- | ----------------------------------------------------- |
| `StructuredFormatter`                  | JSON 结构化日志，自动注入`session_id` / `task_id` |
| `PlainFormatter`                       | 人类可读格式（开发环境）                              |
| `setup_logging()`                      | 初始化（控制台 + 文件双输出）                         |
| `get_logger()`                         | 获取 logger 实例                                      |
| `set_session_id()` / `set_task_id()` | ContextVar（异步安全）                                |

---

## 3. 分层盘点：核心层 (core)

### 3.1 文件总览

| 文件                  | 行数 | 状态 | 核心内容                                                                     |
| --------------------- | ---- | ---- | ---------------------------------------------------------------------------- |
| `exceptions.py`     | 59   | ✅   | 9 个异常类（PPTAgentError → 8 个子类）                                      |
| `document.py`       | 777  | 🔄   | 6 个 dataclass + from_file/to_file/from_run 真实实现 + 12 个内部解析辅助函数 |
| `change_manager.py` | 118  | ✅   | ChangeRecord + ChangeManager（undo/redo 双栈）                               |
| `session.py`        | 65   | ✅   | SessionState + WorkingMemory +`get_session()` 全局单例                     |
| `converter.py`      | 133  | ✅   | `find_libreoffice()` + `convert_ppt_to_pptx()`                           |
| `__init__.py`       | 30   | ✅   | 14 个符号的聚合导出                                                          |

### 3.2 数据模型关系图

```
TextFormat ──► Element ──► Slide ──► PPTDocument ──► SessionState.current_document
                 │                        │
                 └── CursorState           ├── ChangeManager ←── ChangeRecord
                                           └── converter.py (LibreOffice)
```

### 3.3 关键设计决策

| 决策                                   | 说明                                                         |
| -------------------------------------- | ------------------------------------------------------------ |
| `position` 始终用 EMU                | 1 inch = 914400 EMU，与 python-pptx 内部一致                 |
| `type` 用字符串枚举                  | 涵盖 8 种语义类型，避免耦合 python-pptx 内部                 |
| `font_color` 用 HEX                  | `"#FF0000"` 格式，在边界处与 python-pptx `RGBColor` 互转 |
| `from __future__ import annotations` | 全局开启，兼容 Python 3.9+                                   |
| ChangeManager 默认`max_history=16`   | 防止内存无限增长                                             |

### 3.4 异常体系

```
PPTAgentError (基类，含 detail: dict 载荷)
├── PPTFileNotFoundError     — 文件不存在
├── ElementNotFoundError     — 要素不存在
├── FormatNotSupportedError  — 格式/类型不支持
├── InvalidOperationError    — 非法操作
├── ToolExecutionError       — 工具执行异常
├── ConversionError          — 格式转换失败（含 LibreOffice）
├── RenderingError           — 公式/图表/流程图渲染失败
└── ConfigError              — 配置错误
```

---

## 4. 分层盘点：工具层 (tools)

### 4.1 工具框架 — `tools/base.py`（94 行）

```
ToolResult    → success / data / error / metadata
BaseTool      → name + description + schema + execute() + to_openai_schema()
ToolRegistry  → register() / get() / list_all() / get_schemas() / __contains__
```

### 4.2 已实现的工具（16 个）

**Phase 1 文件与幻灯片工具（8 个）**

| 编号 | 工具                | 文件                                  | 功能                                                 |
| ---- | ------------------- | ------------------------------------- | ---------------------------------------------------- |
| T01  | `find_ppt_files`  | `tools/file/finder.py` (111 行)     | 递归搜索 PPT 文件，支持正则/glob/max_depth           |
| T02  | `open_ppt`        | `tools/file/io.py` (203 行)         | 打开文件→加载到 SessionState，自动 .ppt→.pptx 转换 |
| T03  | `save_ppt`        | 同上                                  | 保存到原始路径                                       |
| T04  | `save_ppt_as`     | 同上                                  | 另存为/重命名                                        |
| T05  | `close_ppt`       | 同上                                  | 关闭当前文档，可选保存                               |
| T35  | `add_slide`       | `tools/slide/add.py` (94 行)        | 在指定位置插入空白幻灯片                             |
| T36  | `delete_slide`    | `tools/slide/delete.py` (81 行)     | 按索引删除幻灯片                                     |
| T37  | `reorder_slides`  | `tools/slide/reorder.py` (83 行)    | 按排列重排序幻灯片                                   |
| T38  | `duplicate_slide` | `tools/slide/duplicate.py` (101 行) | 深拷贝复制幻灯片（含 element ID 重新生成）           |

**Phase 2 要素提取工具（8 个）**

| 编号 | 工具                 | 文件                                    | 功能                                                |
| ---- | -------------------- | --------------------------------------- | --------------------------------------------------- |
| T06  | `extract_text`     | `tools/extraction/text.py` (76 行)    | 提取所有文本要素及格式属性（font/size/color/style） |
| T07  | `extract_images`   | `tools/extraction/image.py` (75 行)   | 提取嵌入图片，支持 base64 编码和元数据返回          |
| T08  | `extract_tables`   | `tools/extraction/table.py` (69 行)   | 提取表格为 2D 数组结构                              |
| T09  | `extract_formulas` | `tools/extraction/formula.py` (63 行) | 提取数学公式，返回 LaTeX / MathML 字符串            |
| T10  | `extract_diagrams` | `tools/extraction/diagram.py` (61 行) | 提取 SmartArt / 流程图 / 思维导图                   |
| T11  | `extract_charts`   | `tools/extraction/chart.py` (60 行)   | 提取图表数据及类型信息                              |
| T12  | `extract_media`    | `tools/extraction/media.py` (62 行)   | 提取音频/视频嵌入媒体                               |
| T13  | `read_element`     | `tools/extraction/reader.py` (78 行)  | 按 element_id 读取单个要素的完整详细信息            |

### 4.3 所有工具的共同特性

- 通过 `get_session()` 获取当前文档，无状态依赖
- 使用 `ToolResult(success=..., data=.../error=...)` 统一返回
- 支持 ChangeManager undo/redo（通过 `doc._change_manager`）
- 遵循 OpenAI Function Calling schema 规范

### 4.4 待实现的工具（29 个，Phase 2 剩余 + Phase 3–8）

| Phase      | 工具编号                | 类别                             |
| ---------- | ----------------------- | -------------------------------- |
| ✅ Phase 2 | T06–T13                | 要素提取（全部完成）             |
| Phase 3    | T14–T21, T25–T26, T30 | 要素编辑与插入                   |
| Phase 4    | T22–T24, T27–T29      | 高级内容创建                     |
| Phase 5    | T31–T34                | 布局优化                         |
| Phase 7    | T39–T41                | 搜索与 RAG                       |
| —         | T42–T45                | 工具类（preview/undo/redo/info） |

---

## 5. 分层盘点：引擎层与知识层

### 5.1 渲染引擎 — `pptagent/engines/`

| 计划文件               | 用途                                        | 状态       |
| ---------------------- | ------------------------------------------- | ---------- |
| `ocr_engine.py`      | OCR 文本识别封装 (EasyOCR/PaddleOCR 双引擎) | ✅ Phase 2 |
| `latex_engine.py`    | LaTeX 公式编译为图片                        | ⬜ Phase 4 |
| `mermaid_engine.py`  | Mermaid 流程图渲染                          | ⬜ Phase 4 |
| `graphviz_engine.py` | Graphviz DOT 语言渲染                       | ⬜ Phase 4 |
| `chart_engine.py`    | matplotlib/plotly 图表生成                  | ⬜ Phase 4 |

### 5.2 知识增强 — `pptagent/knowledge/`（空壳）

| 计划文件              | 用途                 | 状态       |
| --------------------- | -------------------- | ---------- |
| `rag.py`            | 本地向量检索增强生成 | ⬜ Phase 7 |
| `web_search.py`     | 联网搜索             | ⬜ Phase 7 |
| `template_store.py` | PPT 模板库管理       | ⬜ Phase 7 |

---

## 6. 分层盘点：测试层

### 6.1 测试基础设施

| 文件                                         | 状态 | 内容                                                 |
| -------------------------------------------- | ---- | ---------------------------------------------------- |
| `tests/conftest.py` (75 行)                | ✅   | 10 个 fixtures（session 级 + function 级 + autouse） |
| `pyproject.toml [tool.pytest.ini_options]` | ✅   | pytest 配置（strict-markers/cov/timeout/asyncio）    |

### 6.2 测试文件概览

| 测试文件                   | 用例数       | 覆盖模块                   | 覆盖率        |
| -------------------------- | ------------ | -------------------------- | ------------- |
| `test_exceptions.py`     | 4            | `core/exceptions.py`     | 100%          |
| `test_document.py`       | 20           | `core/document.py`       | 93%           |
| `test_change_manager.py` | 5            | `core/change_manager.py` | 82%           |
| `test_converter.py`      | 4            | `core/converter.py`      | 62%           |
| `test_base.py`           | 9            | `tools/base.py`          | 97%           |
| `test_finder.py`         | 6            | `tools/file/finder.py`   | 94%           |
| `test_io.py`             | 8            | `tools/file/io.py`       | 68%           |
| `test_slide_ops.py`      | 10           | `tools/slide/*.py`       | 88–94%       |
| **总计**             | **69** | —                         | **84%** |

### 6.3 覆盖率缺口分析

| 模块                  | 当前覆盖率 | 缺失原因                                                     |
| --------------------- | ---------- | ------------------------------------------------------------ |
| `converter.py`      | 62%        | `convert_ppt_to_pptx` 需要真实 LibreOffice 环境            |
| `file/io.py`        | 68%        | `to_file()` 为占位，真实序列化未测试                       |
| `change_manager.py` | 82%        | `can_undo`/`can_redo`/`clear`/`__len__` 未被测试覆盖 |
| `logger.py`         | 43%        | 结构化日志仅在集成环境有意义                                 |
| `session.py`        | 96%        | `reset_session` 未被直接测试                               |

---

## 7. 分层盘点：文档与运维

### 7.1 文档矩阵

| 文档                     | 行数  | 内容                               |
| ------------------------ | ----- | ---------------------------------- |
| `0_plan.md`            | 1,006 | 项目总体技术架构与 8 阶段实施计划  |
| `1_infra.md`           | 3,331 | Phase 0 基础设施搭建详细指南       |
| `2_basicOperations.md` | 777   | Phase 1 文件系统与基础操作详细规划 |
| `12_summary.md`        | 本文  | 阶段总结与后续规划                 |

### 7.2 辅助脚本（10 个）

| 脚本                                               | 用途                       |
| -------------------------------------------------- | -------------------------- |
| `setup_conda_env.sh`                             | 一键创建 conda 环境        |
| `install_system_deps.sh`                         | 系统级依赖安装（Ubuntu）   |
| `run_lint.sh` / `run_tests.sh`                 | 代码质量检查 / 测试执行    |
| `verify_deps.py` / `smoke_test.py`             | 依赖验证 / 冒烟测试        |
| `verify_phase0.sh`                               | Phase 0 完成验证           |
| `env.sh` / `clean.sh` / `create_skeleton.sh` | 环境变量 / 清理 / 骨架生成 |

### 7.3 CI/CD

- **GitHub Actions**：`.github/workflows/ci.yaml`（lint → test 矩阵 → build，conda 驱动）
- **Pre-commit**：8 个 hooks 覆盖 yaml/json/toml 检查 + ruff + isort + black + mypy

---

## 8. 差距分析：已完成 vs 计划

### 8.1 Phase 0 — 完成度 100%

| 计划项         | 状态 | 备注                                            |
| -------------- | ---- | ----------------------------------------------- |
| 项目仓库初始化 | ✅   | git init 完成                                   |
| 开发环境配置   | ✅   | conda environment.yml 就绪，pptagent 环境已创建 |
| CI/CD pipeline | ✅   | GitHub Actions 三阶段流水线                     |
| 代码风格规范   | ✅   | Black + isort + Ruff + mypy + pre-commit        |
| 日志系统       | ✅   | 结构化 JSON + 人类可读双模式                    |

### 8.2 Phase 1 — 完成度 100%

| 计划项               | 状态 | 备注                                     |
| -------------------- | ---- | ---------------------------------------- |
| T01–T05 文件工具    | ✅   | finder / open / save / save_as / close   |
| PPTDocument 内存模型 | ✅   | 6 个 dataclass + EMU 转换                |
| Slide 基本操作       | ✅   | T35–T38（add/delete/reorder/duplicate） |
| ChangeManager        | ✅   | undo/redo 双栈 + max_history             |
| 单元测试覆盖         | ✅   | 69 用例，84% 覆盖率                      |

### 8.3 未完成的边缘任务

| 任务                                                  | 优先级       | 影响                             |
| ----------------------------------------------------- | ------------ | -------------------------------- |
| `PPTDocument.from_file()` 真实反序列化              | **P0** | Phase 2 所有提取操作的前置条件   |
| `PPTDocument.to_file()` 真实序列化                  | P1           | 当前仅占位，无法写回 .pptx       |
| ChangeManager`can_undo`/`can_redo`/`clear` 测试 | P2           | 方法已实现但未被测试覆盖         |
| `converter.py` 集成测试                             | P2           | 需要真实 .ppt 文件 + LibreOffice |

---

## 9. Phase 2 要素提取 — 当前进度

### 9.1 总目标

> 使 Agent 能够**打开真实的 PPT 文件**，**提取并阅读**其中的所有前景要素。

### 9.2 已完成（2026-07-15）

| 序号 | 子任务                               | 文件                            | 状态 |
| ---- | ------------------------------------ | ------------------------------- | ---- |
| 2.1  | `PPTDocument.from_file()` 真实实现 | `core/document.py`            | ✅   |
| 2.2  | OCR 引擎封装                         | `engines/ocr_engine.py`       | ✅   |
| 2.3  | T13`read_element`                  | `tools/extraction/reader.py`  | ✅   |
| 2.4  | T06`extract_text`                  | `tools/extraction/text.py`    | ✅   |
| 2.5  | T07`extract_images`                | `tools/extraction/image.py`   | ✅   |
| 2.6  | T08`extract_tables`                | `tools/extraction/table.py`   | ✅   |
| 2.7  | T11`extract_charts`                | `tools/extraction/chart.py`   | ✅   |
| 2.8  | T09`extract_formulas`              | `tools/extraction/formula.py` | ✅   |
| 2.9  | T10`extract_diagrams`              | `tools/extraction/diagram.py` | ✅   |
| 2.10 | T12`extract_media`                 | `tools/extraction/media.py`   | ✅   |
| 2.11 | `PPTDocument.to_file()` 真实序列化 | `core/document.py`            | ✅   |

### 9.3 已完成功能详情

#### from_file() 实现亮点

- 使用 python-pptx 完整解析 .pptx 文件
- 8 种元素类型分类：text / image / table / chart / diagram / formula / media / shape
- TextFormat.from_run() 真实提取：font_name, font_size (EMU→pt), font_color (RGB→HEX), bold/italic/underline/strikethrough
- 图片 Blob 惰性加载、表格 2D 数组提取、图表数据提取
- Group/GroupShape 扁平化处理（1 层递归）
- 空文本 shape 自动跳过
- 错误处理：FileNotFoundError / ImportError / 通用异常包装

#### to_file() 实现亮点

- 完整 roundtrip：from_file → to_file → from_file 验证通过
- 文本元素：还原 font_name, font_size, font_color, bold, italic, underline, alignment
- 图片元素：从 blob 字节还原
- 其他类型（Phase 3+）：静默跳过

#### OCR 引擎

- 双引擎支持：EasyOCR + PaddleOCR
- 延迟加载（懒初始化），按配置切换
- 置信度阈值过滤
- 结构化输出：text / confidence / bbox 三元组

#### 8 个提取工具（T06–T13）

- 全部遵循 BaseTool 接口规范
- 支持按 slide_index 筛选或全文档提取
- 统一 ToolResult 返回格式
- OpenAI Function Calling schema 已定义

### 9.4 已完成（第二轮，2026-07-15）

| 序号 | 子任务                           | 状态 |
| ---- | -------------------------------- | ---- |
| 2.12 | 提取工具单元测试（8 个测试文件，28 用例） | ✅   |
| 2.13 | from_file() + to_file() 集成测试（4 用例） | ✅   |
| 2.14 | OCR 引擎单元测试（5 用例）        | ✅   |
| 2.15 | 端到端 smoke test + roundtrip     | ✅   |

### 9.5 验证状态

- ✅ MyPy: 零错误通过
- ✅ Pytest: **105 个测试全部通过**
- ✅ 覆盖率: **79%**（从 27% 提升）
- ✅ Roundtrip: from_file → to_file → from_file 完整验证
- ✅ 预存在测试修复: converter.py + test_io.py 适配新 from_file 实现

### 9.6 关键风险（同原计划）

| 风险                     | 缓解                                                    |
| ------------------------ | ------------------------------------------------------- |
| OMML 公式解析不完整      | 回退到 OCR 方案（已有`formula_fallback_to_ocr` 配置） |
| 复杂 SmartArt/GroupShape | 提供 "作为图片保留" 备选方案                            |
| 大文件性能               | 懒加载图片（已有`lazy_load_images` 配置）             |
| OCR 准确率不足           | 双引擎（EasyOCR + PaddleOCR）取置信度高者               |
| 竖排文本/艺术字          | 标记为 "部分支持"，转换为图片保留视觉效果               |

---

## 10. Phase 3 要素编辑 — 已完成 (2026-07-15)

### 10.1 完成内容

| 序号 | 工具 | 文件 | 状态 |
|------|------|------|------|
| T14 | `set_position` | `tools/manipulation/element_geometry.py` | ✅ |
| T15 | `set_size` | 同上 | ✅ |
| T16 | `format_text` | `tools/manipulation/text_formatter.py` | ✅ |
| T17 | `set_alignment` | 同上 | ✅ |
| T18 | `set_text_effect` | 同上 | ✅ |
| T19 | `delete_element` | `tools/manipulation/element_delete.py` | ✅ |
| T21 | `insert_image` | `tools/insertion/image_inserter.py` | ✅ |
| T25 | `insert_text_box` | `tools/insertion/text_inserter.py` | ✅ |
| T26 | `insert_table` | `tools/insertion/table_inserter.py` | ✅ |
| T30 | `insert_chart` | `tools/insertion/chart_inserter.py` | ✅ |
| — | to_file() 扩展 | `core/document.py` | ✅ |

### 10.2 关键特性

- 所有编辑操作支持 **undo/redo**（ChangeRecord + ChangeManager）
- **T16 format_text** 支持 14 个 TextFormat 字段的部分更新
- **T15 set_size** 支持 `lock_aspect_ratio` 等比例缩放
- **T21 insert_image** 支持 PIL 自动尺寸检测
- **to_file()** 扩展支持 table/chart 元素写出
- 全部 10 个工具遵循 BaseTool 接口规范

### 10.3 测试覆盖

| 测试文件 | 用例数 | 覆盖率 |
|---------|--------|--------|
| test_element_geometry.py | 9 | 95% |
| test_text_formatter.py | 10 | 86% |
| test_element_delete.py | 5 | 92% |
| test_image_inserter.py | 5 | 78% |
| test_text_inserter.py | 5 | 93% |
| test_table_inserter.py | 5 | 89% |
| test_chart_inserter.py | 6 | 88% |

### 10.4 验证状态

- ✅ MyPy: 零错误通过
- ✅ Pytest: **150 个测试全部通过**（+45 Phase 3 测试）
- ✅ 覆盖率: **80%**
- ✅ Smoke test: 插入→格式化→移动→缩放→删除→undo→roundtrip 全流程

---

## 11. 中期方向：Phase 4–5

```
Phase 3: 要素编辑
  └── 调整位置/尺寸/格式/对齐/效果 (T14–T19)
  └── 插入图片/文本框/表格/图表 (T21, T25, T26, T30)
  └── 此时 Agent 具备完整的 PPT"阅读+修改"能力

Phase 4: 高级内容创建
  └── LaTeX → 公式图片 (latex_engine.py)
  └── Mermaid/Graphviz → 流程图图片 (mermaid_engine.py, graphviz_engine.py)
  └── 视频/音频/动图嵌入 (T22–T24)
  └── 此时 Agent 具备创建科研 PPT 的全部原子能力

Phase 5: 布局优化
  └── 自动对齐/分布/网格吸附 (T31, T33–T34)
  └── 模板系统 + 美学评分 (T32)
  └── 此时 Agent 输出的 PPT 不仅"能看"而且"好看"
```

---

## 11. 远期愿景：Phase 6–8

```
Phase 6: Agentic Loop 集成
  └── Planner → Executor → Evaluator → Reflector 闭环
  └── 用户说"帮我把第 3 页的表格字体调大"，Agent 自动规划并执行
  └── 此时 PPTAgent 真正成为一个 "Agent" 而非 "工具集合"

Phase 7: 知识增强
  └── RAG 检索本地论文/模板库 (T40)
  └── 联网搜索学术会议 PPT 规范 (T39)
  └── 用户说"做一个 NeurIPS 风格的 poster"，Agent 知道该怎么做

Phase 8: UI/UX 与交付
  └── CLI 交互 / Gradio Web UI
  └── 端到端集成测试
  └── 发布 v1.0
```

---

> **当前最紧迫的任务**：实现 `PPTDocument.from_file()`，打通从真实 PPT 文件 → 内存模型的链路。这是 Phase 2 所有提取操作的基石，也是 PPTAgent 从"空壳框架"变为"真正可用工具"的关键一步。

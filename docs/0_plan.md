# PPTAgent：科研PPT智能制作Agent 技术架构与实施计划

> **版本**: v1.0 | **日期**: 2026-06-30 | **作者**: PPTAgent Team

---

## 目录

1. [项目愿景与目标](#1-项目愿景与目标)
2. [总体技术架构](#2-总体技术架构)
3. [核心模块设计](#3-核心模块设计)
4. [工具体系定义](#4-工具体系定义)
5. [Agentic Loop 设计](#5-agentic-loop-设计)
6. [数据流与状态管理](#6-数据流与状态管理)
7. [技术栈选型](#7-技术栈选型)
8. [项目实施阶段](#8-项目实施阶段)
9. [接口与扩展约定](#9-接口与扩展约定)
10. [风险与缓解策略](#10-风险与缓解策略)

---

## 1. 项目愿景与目标

### 1.1 愿景

构建一个面向科研工作者的智能PPT制作Agent，能够通过自然语言交互理解用户意图，自动调用多类工具完成PPT的**读取、分析、编辑、生成、美化、保存**全流程操作，大幅降低科研PPT制作的时间成本。

### 1.2 核心目标

| 编号 | 目标                                                                          | 优先级 |
| ---- | ----------------------------------------------------------------------------- | ------ |
| G1   | 理解用户自然语言意图，转化为可执行的Agentic Loop                              | P0     |
| G2   | 发现并解析指定路径下的PPT文件（.ppt/.pptx等）                                 | P0     |
| G3   | 提取并阅读PPT中所有前景要素（文本、图片、表格、公式、图形、流程图、思维导图） | P0     |
| G4   | 调整任意前景要素的位置、尺寸                                                  | P0     |
| G5   | 调整文本的完整格式属性（字体、大小、颜色、对齐、特殊效果）                    | P0     |
| G6   | 插入图片、视频、音频、动图                                                    | P1     |
| G7   | 插入并编辑数学公式、流程图、思维导图                                          | P1     |
| G8   | 自动布局优化，使PPT美观简洁                                                   | P1     |
| G9   | 保存、重命名PPT文件                                                           | P0     |
| G10  | 具备RAG、联网搜索等辅助能力                                                   | P1     |

---

## 2. 总体技术架构

### 2.1 分层架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      用户交互层 (User Interface)                   │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│   │  CLI / Chat  │  │  Web UI      │  │  IDE Extension       │   │
│   │  Interface   │  │  (Gradio)    │  │  (VSCode Plugin)     │   │
│   └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
└──────────┼──────────────────┼──────────────────────┼──────────────┘
           │                  │                      │
           └──────────────────┼──────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────────────┐
│                  Agent 编排层 (Agent Orchestration)                  │
│  ┌──────────────────────────┴───────────────────────────────┐     │
│  │               Agentic Loop Engine                         │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │     │
│  │  │ Planner  │  │ Executor │  │ Evaluator│  │ Reflector│ │     │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │     │
│  └──────────────────────────────────────────────────────────┘     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │               Memory & Context Manager                     │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐    │     │
│  │  │ Short-term│  │ Long-term│  │  Working Memory      │    │     │
│  │  │  Memory   │  │  (RAG)   │  │  (PPT State Cache)   │    │     │
│  │  └──────────┘  └──────────┘  └──────────────────────┘    │     │
│  └──────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────────────┐
│                    工具层 (Tool Layer)                               │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐         │
│  │ File Tools│ │Extraction │ │Manipulation│ │Creation   │         │
│  │           │ │ Tools     │ │ Tools      │ │ Tools     │         │
│  │ - find    │ │ - text    │ │ - position │ │ - image   │         │
│  │ - open    │ │ - image   │ │ - size     │ │ - video   │         │
│  │ - save    │ │ - table   │ │ - font     │ │ - audio   │         │
│  │ - rename  │ │ - formula │ │ - color    │ │ - formula │         │
│  │           │ │ - diagram │ │ - align    │ │ - diagram │         │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘         │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐         │
│  │Layout     │ │ Search/   │ │ Export    │ │ Utility   │         │
│  │ Tools     │ │ RAG Tools │ │ Tools     │ │ Tools     │         │
│  │           │ │           │ │           │ │           │         │
│  │ - auto    │ │ - web     │ │ - PDF     │ │ - validate│         │
│  │   layout  │ │ - knowledge│ │ - image   │ │ - diff    │         │
│  │ - template│ │   base    │ │ - HTML    │ │ - undo    │         │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘         │
└───────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────────────┐
│                  数据处理层 (Data Processing Layer)                  │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐            │
│  │python-pptx│ │Pillow/    │ │ Pytesseract│ │LaTeX/    │            │
│  │  Engine   │ │OpenCV     │ │ /EasyOCR │ │MathJax   │            │
│  └──────────┘ └───────────┘ └──────────┘ └──────────┘            │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Graphviz │ │ Mermaid   │ │ markitdown│ │  FFmpeg  │            │
│  │ Engine   │ │ Engine    │ │  Engine   │ │  Engine  │            │
│  └──────────┘ └───────────┘ └──────────┘ └──────────┘            │
└───────────────────────────────────────────────────────────────────┘
```

### 2.2 核心设计原则

1. **工具即接口 (Tool as Interface)**：所有PPT操作封装为独立、可组合的工具函数，每个工具有清晰的输入/输出schema
2. **Agentic Loop 驱动**：采用 Plan → Execute → Evaluate → Reflect 的闭环控制流
3. **状态可追溯**：所有操作支持undo/redo，变更以增量方式记录
4. **格式兼容性**：同时支持 .ppt（通过LibreOffice转换）和 .pptx（原生处理）
5. **渐进式复杂度**：先实现P0核心功能，再逐步扩展P1高级功能

---

## 3. 核心模块设计

### 3.1 Agent 编排引擎 (`agent_orchestration/`)

```
agent_orchestration/
├── __init__.py
├── planner.py          # 意图理解 → 任务分解 → 工具选择
├── executor.py         # 工具调用执行器
├── evaluator.py        # 执行结果评估与校验
├── reflector.py        # 反思与自我纠错
├── loop_controller.py  # Agentic Loop 主控制器
└── prompt_templates/   # System Prompt / Task Prompt 模板库
    ├── system.yaml
    ├── research_ppt.yaml
    └── editing.yaml
```

#### 3.1.1 Planner 模块

- **输入**：用户自然语言指令 + 当前工作上下文（已打开文件、已提取要素）
- **处理**：LLM将用户意图解析为结构化的任务计划（DAG）
- **输出**：`TaskPlan` 对象，包含有序的工具调用序列及参数

```python
@dataclass
class TaskPlan:
    goal: str                          # 最终目标描述
    steps: List[ToolCall]              # 有序工具调用步骤
    dependencies: Dict[str, List[str]] # 步骤间依赖关系
    expected_output: str               # 期望输出描述
```

#### 3.1.2 Executor 模块

- 负责按计划顺序执行工具调用
- 支持并行执行无依赖的步骤
- 捕获执行异常并触发Replan

#### 3.1.3 Evaluator 模块

- 每个步骤执行后进行结果校验
- 判断是否符合预期，评分（1-5）
- 决定是否进入下一步或触发Reflect

#### 3.1.4 Reflector 模块

- 当Evaluator评分过低时触发
- 分析失败原因：参数错误？工具选择错误？理解偏差？
- 生成修正方案反馈给Planner重新规划

### 3.2 文件系统模块 (`file_system/`)

```
file_system/
├── __init__.py
├── file_finder.py      # 正则/glob 文件发现
├── file_io.py          # 文件打开、保存、重命名
├── format_converter.py # .ppt → .pptx 转换 (via LibreOffice)
└── file_watcher.py     # 文件变更监听（可选）
```

#### 关键能力

- **递归文件发现**：支持通配符 + 正则表达式，遍历指定路径下所有子目录
- **格式自动识别**：区分 .ppt / .pptx / .potx / .ppsx 等
- **格式转换**：对旧版 .ppt，无损转换为 .pptx 再处理
- **文件锁定**：打开文件时加锁防止并发冲突

### 3.3 PPT解析与提取模块 (`extraction/`)

```
extraction/
├── __init__.py
├── slide_reader.py     # 幻灯片级解析入口
├── text_extractor.py   # 文本提取（含格式属性）
├── image_extractor.py  # 图片提取
├── table_extractor.py  # 表格提取
├── shape_extractor.py  # 图形/形状提取
├── formula_extractor.py# 数学公式提取（OMML/LaTeX/MathML）
├── chart_extractor.py  # 图表提取
├── diagram_extractor.py# 流程图/思维导图提取
├── media_extractor.py  # 视频/音频提取
├── layout_analyzer.py  # 布局结构分析
└── ocr_engine.py       # OCR引擎（处理图片中的文字）
```

#### 3.3.1 要素提取详细说明

| 要素类型        | 提取方法                 | 输出格式                        | 依赖库                    |
| --------------- | ------------------------ | ------------------------------- | ------------------------- |
| 文本            | python-pptx shape.text   | JSON（含字体/颜色/大小/对齐等） | python-pptx               |
| 图片            | python-pptx image blobs  | PNG/JPG 文件                    | python-pptx, Pillow       |
| 表格            | python-pptx table.cell   | CSV / Markdown Table            | python-pptx               |
| 数学公式        | OMML解析 + MathType OLE  | LaTeX 字符串                    | python-pptx, latex2mathml |
| 图表            | python-pptx chart        | 结构化数据 + 图片快照           | python-pptx               |
| 流程图/思维导图 | GroupShape解析 + OCR辅助 | JSON描述 + 图片快照             | python-pptx, OCR          |
| 视频/音频       | OLE对象提取              | 原始文件                        | python-pptx, olefile      |
| SmartArt        | SmartArt图形解析         | JSON结构描述                    | python-pptx               |

#### 3.3.2 格式属性提取规范

文本格式属性需完整提取以下字段：

```python
@dataclass
class TextFormat:
    font_name: str            # 字体名称
    font_size: float          # 字号（pt）
    font_color: str           # 颜色（HEX RGBA）
    bold: bool                # 加粗
    italic: bool              # 斜体
    underline: bool           # 下划线
    strikethrough: bool       # 删除线
    superscript: bool         # 上角标
    subscript: bool           # 下角标
    highlight: str            # 突出显示颜色
    alignment: str            # left/center/right/justify
    line_spacing: float       # 行距
    paragraph_spacing: float  # 段间距
```

### 3.4 PPT编辑与操控模块 (`manipulation/`)

```
manipulation/
├── __init__.py
├── slide_editor.py      # 幻灯片增删改
├── element_position.py  # 前景要素位置调整
├── element_size.py      # 前景要素尺寸调整
├── text_formatter.py    # 文本格式调整
├── image_inserter.py    # 图片插入
├── media_inserter.py    # 视频/音频/动图插入
├── formula_editor.py    # 数学公式编辑
├── diagram_editor.py    # 流程图/思维导图编辑
└── layout_optimizer.py  # 自动布局优化
```

#### 3.4.1 位置与尺寸调整接口

```python
def set_element_position(
    slide_index: int,
    element_id: str,
    left: float,     # 距左边距（EMU或英寸）
    top: float,      # 距顶部距离
) -> bool

def set_element_size(
    slide_index: int,
    element_id: str,
    width: float,
    height: float,
    lock_aspect_ratio: bool = True
) -> bool

def set_element_z_order(
    slide_index: int,
    element_id: str,
    z_index: int
) -> bool
```

#### 3.4.2 文本格式调整接口

```python
def format_text(
    slide_index: int,
    element_id: str,
    format_spec: TextFormat,   # 参见上文 TextFormat 定义
    apply_to: str = "all"      # "all" | "selection" | "paragraph"
) -> bool
```

#### 3.4.3 内容插入接口

```python
def insert_image(slide_index, image_path, position, size, alt_text="") -> str  # 返回 element_id
def insert_video(slide_index, video_path, position, size, auto_play=False) -> str
def insert_audio(slide_index, audio_path, icon_position, auto_play=False) -> str
def insert_gif(slide_index, gif_path, position, size, loop=True) -> str
```

#### 3.4.4 公式与图表编辑

```python
def insert_formula(
    slide_index: int,
    latex_str: str,
    position: Tuple[float, float],
    size: Tuple[float, float],
    render_method: str = "latex2image"  # "latex2image" | "OMML" | "MathML"
) -> str

def insert_flowchart(
    slide_index: int,
    spec: str,                    # Mermaid / Graphviz DOT 语法
    position: Tuple[float, float],
    size: Tuple[float, float],
    format: str = "mermaid"       # "mermaid" | "graphviz"
) -> str

def insert_mindmap(
    slide_index: int,
    spec: Dict,                   # 思维导图结构化描述
    position: Tuple[float, float],
    size: Tuple[float, float],
    style: str = "default"
) -> str
```

#### 3.4.5 自动布局引擎

```python
@dataclass
class LayoutRule:
    name: str
    description: str
    priority: int          # 规则优先级
    condition: Callable    # 触发条件
    apply: Callable        # 布局调整逻辑

# 内置布局规则
DEFAULT_LAYOUT_RULES = [
    Rule("align_left", "左对齐", 1),
    Rule("distribute_horizontal", "水平均匀分布", 2),
    Rule("distribute_vertical", "垂直均匀分布", 2),
    Rule("snap_to_grid", "吸附到网格", 3),
    Rule("golden_ratio", "黄金比例分割", 4),
    Rule("whitespace_balance", "留白平衡", 5),
    Rule("visual_hierarchy", "视觉层级优化", 6),
]
```

### 3.5 搜索与知识增强模块 (`knowledge/`)

```
knowledge/
├── __init__.py
├── rag_engine.py        # 本地知识库检索增强生成
├── web_search.py        # 联网搜索工具
├── template_store.py    # PPT模板库管理
├── academic_styles.py   # 学术会议/期刊风格预设
└── knowledge_base/      # 本地知识库文件
    ├── templates/
    ├── icons/
    └── references/
```

#### 3.5.1 RAG 能力

- **本地知识库**：存储优质PPT模板、科研图表范例、配色方案
- **向量数据库**：ChromaDB / FAISS 存储模板特征的 embedding
- **检索策略**：基于用户任务描述匹配最相关的模板和范例

#### 3.5.2 联网搜索能力

- 检索学术会议PPT规范（如NeurIPS/ICML/ACL等poster/talk要求）
- 搜索素材图片（需标注来源和版权）
- 查找LaTeX公式参考

---

## 4. 工具体系定义

### 4.1 工具分类总览

| 分类             | 编号 | 工具名                  | 功能描述                           | 优先级 |
| ---------------- | ---- | ----------------------- | ---------------------------------- | ------ |
| **文件**   | T01  | `find_ppt_files`      | 正则查找路径及子目录下的PPT文件    | P0     |
|                  | T02  | `open_ppt`            | 打开指定PPT文件并加载到内存        | P0     |
|                  | T03  | `save_ppt`            | 保存当前PPT更改                    | P0     |
|                  | T04  | `save_ppt_as`         | 另存为/重命名PPT                   | P0     |
|                  | T05  | `close_ppt`           | 关闭当前PPT文件                    | P0     |
| **提取**   | T06  | `extract_text`        | 提取所有文本及其格式属性           | P0     |
|                  | T07  | `extract_images`      | 提取所有嵌入图片                   | P0     |
|                  | T08  | `extract_tables`      | 提取所有表格数据                   | P0     |
|                  | T09  | `extract_formulas`    | 提取数学公式并转LaTeX              | P1     |
|                  | T10  | `extract_diagrams`    | 提取流程图/思维导图结构            | P1     |
|                  | T11  | `extract_charts`      | 提取图表及其数据                   | P0     |
|                  | T12  | `extract_media`       | 提取嵌入的视频/音频                | P1     |
|                  | T13  | `read_element`        | 阅读指定要素的详细内容             | P0     |
| **操控**   | T14  | `set_position`        | 调整要素位置                       | P0     |
|                  | T15  | `set_size`            | 调整要素尺寸                       | P0     |
|                  | T16  | `format_text`         | 调整文本字体/大小/颜色/样式        | P0     |
|                  | T17  | `set_alignment`       | 设置文本对齐方式                   | P0     |
|                  | T18  | `set_text_effect`     | 设置特殊效果（斜体/粗体/上下标等） | P0     |
|                  | T19  | `delete_element`      | 删除指定要素                       | P0     |
|                  | T20  | `duplicate_element`   | 复制要素                           | P1     |
| **插入**   | T21  | `insert_image`        | 插入图片文件                       | P0     |
|                  | T22  | `insert_video`        | 插入视频文件                       | P1     |
|                  | T23  | `insert_audio`        | 插入音频文件                       | P1     |
|                  | T24  | `insert_gif`          | 插入动图                           | P1     |
|                  | T25  | `insert_text_box`     | 插入文本框                         | P0     |
|                  | T26  | `insert_table`        | 插入表格                           | P0     |
|                  | T27  | `insert_formula`      | 插入/编辑数学公式                  | P1     |
|                  | T28  | `insert_flowchart`    | 插入流程图                         | P1     |
|                  | T29  | `insert_mindmap`      | 插入思维导图                       | P1     |
|                  | T30  | `insert_chart`        | 插入图表                           | P0     |
| **布局**   | T31  | `auto_layout`         | 自动优化当前幻灯片布局             | P1     |
|                  | T32  | `apply_template`      | 应用PPT模板                        | P1     |
|                  | T33  | `align_elements`      | 批量对齐多个要素                   | P1     |
|                  | T34  | `distribute_elements` | 均匀分布多个要素                   | P1     |
| **幻灯片** | T35  | `add_slide`           | 添加新幻灯片                       | P0     |
|                  | T36  | `delete_slide`        | 删除幻灯片                         | P0     |
|                  | T37  | `reorder_slides`      | 调整幻灯片顺序                     | P0     |
|                  | T38  | `duplicate_slide`     | 复制幻灯片                         | P1     |
| **搜索**   | T39  | `web_search`          | 联网搜索                           | P1     |
|                  | T40  | `rag_search`          | 本地知识库检索                     | P1     |
|                  | T41  | `search_element`      | 在PPT内搜索要素                    | P0     |
| **工具**   | T42  | `preview_slide`       | 生成幻灯片预览图                   | P0     |
|                  | T43  | `undo`                | 撤销上一步操作                     | P0     |
|                  | T44  | `redo`                | 重做                               | P0     |
|                  | T45  | `get_slide_info`      | 获取幻灯片结构概览                 | P0     |

### 4.2 工具Schema规范

每个工具遵循OpenAI Function Calling Schema规范：

```python
TOOL_SCHEMA_TEMPLATE = {
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "清晰的工具描述，说明何时使用",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."},
                "param2": {"type": "number", "description": "..."},
            },
            "required": ["param1"],
        }
    }
}
```

---

## 5. Agentic Loop 设计

### 5.1 主循环流程

```
┌──────────────────────────────────────────────┐
│                  START                        │
│           用户输入自然语言指令                   │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│           Phase 1: Intent Parsing             │
│  - LLM解析用户意图                             │
│  - 提取目标、约束、偏好                          │
│  - 判断任务类型（新建/编辑/审阅/搜索）             │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│           Phase 2: Context Gathering          │
│  - 加载相关PPT文件（如已指定）                    │
│  - 提取当前状态（已有要素、布局）                  │
│  - 检索相关知识（RAG/Web）                      │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│           Phase 3: Planning                   │
│  - 将目标分解为有序子任务                        │
│  - 为每个子任务选择最合适的工具                   │
│  - 生成 TaskPlan（DAG）                        │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│           Phase 4: Execution                  │
│  for each step in TaskPlan:                   │
│    ├── 调用对应工具                            │
│    ├── 收集执行结果                            │
│    └── 更新Working Memory                     │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│           Phase 5: Evaluation                 │
│  - 评估每一步执行结果                          │
│  - 判断是否达到预期目标                         │
│  - 评分（1-5）                                │
└──────────────────┬───────────────────────────┘
                   │
          ┌────────┴────────┐
          │ score >= 4 ?    │
          └────────┬────────┘
             Yes   │   No
                   │    │
                   │    ▼
                   │ ┌──────────────────────────┐
                   │ │  Phase 6: Reflection      │
                   │ │  - 分析失败原因            │
                   │ │  - 生成修正策略            │
                   │ │  - 重新进入 Planning       │
                   │ └──────────────────────────┘
                   │    │
                   ▼    │
┌──────────────────────────────────────────────┐
│           Phase 7: Output Generation          │
│  - 汇总所有变更                                │
│  - 生成操作报告                                │
│  - 返回最终结果给用户                           │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│                    END                        │
│         等待用户反馈或新指令                     │
└──────────────────────────────────────────────┘
```

### 5.2 关键设计决策

#### 5.2.1 最大重规划次数

```python
MAX_REPLAN_COUNT = 3  # 单次任务最多重新规划3次，超过则交给用户决策
```

#### 5.2.2 并行执行策略

- 无依赖的提取操作（T06-T12）可**并行执行**
- 编辑操作（T14-T19）必须**串行执行**（后续操作的输入依赖前序操作的结果）
- 布局优化（T31-T34）在所有编辑完成后**批量执行**

#### 5.2.3 用户确认策略

| 操作类型               | 确认策略   |
| ---------------------- | ---------- |
| 只读操作（提取、阅读） | 无需确认   |
| 单元素编辑             | 无需确认   |
| 批量编辑（>3个元素）   | 预览后确认 |
| 删除操作               | 确认       |
| 保存/覆盖              | 确认       |
| 自动布局               | 预览后确认 |

---

## 6. 数据流与状态管理

### 6.1 PPT内存模型

```python
@dataclass
class PPTDocument:
    """PPT文档的内存表示"""
    file_path: str
    file_name: str
    slides: List[Slide]
    metadata: DocumentMetadata
    change_log: List[ChangeRecord]     # 变更历史（支持undo/redo）
    cursor: CursorState                # 当前操作位置

@dataclass
class Slide:
    index: int
    layout_name: str
    elements: Dict[str, Element]       # element_id → Element
    background: BackgroundInfo
    notes: str

@dataclass
class Element:
    id: str
    type: str                          # "text"|"image"|"table"|"chart"|"formula"|"diagram"|"media"|"shape"
    position: Tuple[float, float, float, float]  # left, top, width, height (EMU)
    content: Any                       # 类型相关的具体内容
    format: Optional[TextFormat]
    z_order: int
    metadata: Dict[str, Any]           # 额外属性（动画、超链接等）
```

### 6.2 变更记录与Undo/Redo

```python
@dataclass
class ChangeRecord:
    id: str
    timestamp: datetime
    operation: str                     # 操作名称
    target_element: str                # 目标元素ID
    before_state: Any                  # 操作前状态（用于undo）
    after_state: Any                   # 操作后状态（用于redo）
    slide_index: int

class ChangeManager:
    def __init__(self, max_history=100):
        self.undo_stack: List[ChangeRecord] = []
        self.redo_stack: List[ChangeRecord] = []
        self.max_history = max_history

    def record(self, change: ChangeRecord): ...
    def undo(self) -> Optional[ChangeRecord]: ...
    def redo(self) -> Optional[ChangeRecord]: ...
    def clear(self): ...
```

### 6.3 会话状态管理

```python
@dataclass
class SessionState:
    """单次对话会话状态"""
    session_id: str
    current_document: Optional[PPTDocument]
    open_files: List[str]              # 当前打开的文件路径列表
    task_history: List[TaskPlan]       # 历史任务
    memory: WorkingMemory              # 工作记忆

@dataclass
class WorkingMemory:
    """Agent的工作记忆"""
    user_preferences: Dict             # 用户偏好（风格、常用模板等）
    context_summary: str               # 当前上下文摘要
    extracted_elements: Dict           # 已提取的要素缓存
    recent_operations: List[str]       # 最近操作列表
    observations: List[str]            # Agent的观察笔记
```

---

## 7. 技术栈选型

### 7.1 核心技术栈

| 层级                 | 技术                          | 版本     | 用途                 |
| -------------------- | ----------------------------- | -------- | -------------------- |
| **Agent框架**  | LangChain / LlamaIndex / 自研 | latest   | Agent编排与工具管理  |
| **LLM**        | Claude API / GPT-4o           | latest   | 意图理解、规划、反思 |
| **PPT处理**    | python-pptx                   | ≥0.6.21 | .pptx文件读写        |
| **旧版PPT**    | LibreOffice (headless)        | ≥7.0    | .ppt → .pptx转换    |
| **图像处理**   | Pillow + OpenCV               | ≥10.0   | 图片提取与处理       |
| **OCR**        | PaddleOCR / EasyOCR           | latest   | 图片内文字识别       |
| **公式渲染**   | LaTeX (texlive) + pdf2image   | latest   | 数学公式渲染为图片   |
| **图表生成**   | matplotlib / plotly           | latest   | 图表生成             |
| **流程图**     | Mermaid CLI / Graphviz        | latest   | 流程图/思维导图渲染  |
| **文档解析**   | markitdown                    | latest   | 多格式文档转Markdown |
| **向量数据库** | ChromaDB / FAISS              | latest   | RAG知识检索          |
| **API服务**    | FastAPI + Pydantic            | ≥2.0    | 对外API接口          |
| **前端UI**     | Gradio / Streamlit            | latest   | 演示界面             |
| **测试**       | pytest + pytest-mock          | latest   | 单元/集成测试        |
| **配置管理**   | YAML + Pydantic Settings      | latest   | 配置管理             |

### 7.2 Python依赖清单 (`requirements.txt`)

```
# Core
python-pptx>=0.6.21
lxml>=4.9.0
Pillow>=10.0.0
olefile>=0.46

# Agent Framework
langchain>=0.2.0
langchain-anthropic>=0.1.0
openai>=1.0.0
pydantic>=2.0.0

# Image & OCR
opencv-python>=4.8.0
paddleocr>=2.7.0
easyocr>=1.7.0

# Formula & Diagram
latex2mathml>=3.0.0
graphviz>=0.20.0

# RAG & Search
chromadb>=0.4.0
tiktoken>=0.5.0

# Web & API
fastapi>=0.100.0
uvicorn>=0.23.0

# UI Demo
gradio>=4.0.0

# Utilities
pyyaml>=6.0
rich>=13.0.0
xxhash>=3.0.0  # 图片去重
```

### 7.3 系统依赖

```bash
# Ubuntu/Debian
sudo apt-get install -y \
    libreoffice-headless \
    texlive-latex-extra \
    texlive-science \
    poppler-utils \
    ffmpeg \
    graphviz

# npm (Mermaid CLI)
npm install -g @mermaid-js/mermaid-cli
```

---

## 8. 项目实施阶段

### Phase 0: 基础设施搭建（1-2周）

- [X] 项目仓库初始化，目录结构创建
- [ ] 开发环境配置（Python venv、依赖安装、系统依赖）
- [ ] CI/CD pipeline 配置（GitHub Actions / GitLab CI）
- [ ] 代码风格规范（Black + isort + mypy）
- [ ] 日志系统搭建

### Phase 1: 文件系统与基础PPT操作（2-3周）

- [ ] T01-T05：文件发现、打开、保存、重命名工具
- [ ] PPTDocument 内存模型实现
- [ ] 基本Slide操作（增删改排序）
- [ ] ChangeManager（undo/redo）
- [ ] 单元测试覆盖

### Phase 2: 要素提取（2-3周）

- [ ] T06, T13：文本提取与阅读
- [ ] T07：图片提取
- [ ] T08：表格提取
- [ ] T11：图表提取
- [ ] OCR引擎集成
- [ ] T09：公式提取（OMML解析）
- [ ] T10, T12：流程图/媒体提取

### Phase 3: 要素编辑（2-3周）

- [ ] T14-T19：位置、尺寸、格式、对齐、特殊效果
- [ ] T21, T25, T26：插入图片、文本框、表格
- [ ] T20：元素复制
- [ ] T30：图表插入

### Phase 4: 高级内容创建（2-3周）

- [ ] T22-T24：视频/音频/动图插入
- [ ] T27：公式插入与编辑
- [ ] T28-T29：流程图/思维导图插入与编辑
- [ ] LaTeX渲染管道
- [ ] Mermaid/Graphviz渲染管道

### Phase 5: 布局优化（1-2周）

- [ ] T31：自动布局引擎
- [ ] T32：模板系统
- [ ] T33-T34：批量对齐与分布
- [ ] 美学评分模型

### Phase 6: Agentic Loop 集成（2-3周）

- [ ] Planner + Executor + Evaluator + Reflector
- [ ] Agentic Loop主控制器
- [ ] Prompt模板库
- [ ] Session状态管理
- [ ] 端到端集成测试

### Phase 7: 知识增强（1-2周）

- [ ] T39：联网搜索
- [ ] T40：RAG本地知识库
- [ ] 模板库与风格预设

### Phase 8: UI/UX 与测试（1-2周）

- [ ] CLI交互界面
- [ ] Gradio Web演示界面
- [ ] 全量集成测试
- [ ] 文档编写
- [ ] 性能调优

---

## 9. 接口与扩展约定

### 9.1 工具注册规范

所有工具必须通过统一的注册机制接入Agent：

```python
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """工具基类"""
    name: str
    description: str
    schema: Dict[str, Any]

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具逻辑"""
        ...

@dataclass
class ToolResult:
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class ToolRegistry:
    """工具注册中心"""
    def register(self, tool: BaseTool): ...
    def get(self, name: str) -> BaseTool: ...
    def list_all(self) -> List[str]: ...
    def get_schemas(self) -> List[Dict]: ...
```

### 9.2 扩展新工具规范

1. 继承 `BaseTool` 基类
2. 实现 `execute()` 方法
3. 定义标准Schema（含清晰的description，帮助LLM理解何时调用）
4. 编写单元测试（覆盖率 > 80%）
5. 注册到 `ToolRegistry`
6. 在Prompt模板中添加工具说明

### 9.3 命名约定

- 文件名：`snake_case.py`
- 类名：`PascalCase`
- 函数/方法：`snake_case`
- 常量：`UPPER_SNAKE_CASE`
- 工具名：`snake_case`（与函数名一致）
- Element ID：`{type}_{uuid8}` 格式，如 `text_a3f2c1b0`

### 9.4 错误处理约定

```python
class PPTAgentError(Exception): pass
class FileNotFoundError(PPTAgentError): pass
class ElementNotFoundError(PPTAgentError): pass
class FormatNotSupportedError(PPTAgentError): pass
class InvalidOperationError(PPTAgentError): pass
class ToolExecutionError(PPTAgentError): pass
```

所有工具异常必须被捕获并包装为 `ToolResult(success=False, error=...)`，不允许原始异常泄漏到Agent层。

### 9.5 日志规范

```python
import logging

logger = logging.getLogger("pptagent")

# 使用结构化日志
logger.info("tool_executed", extra={
    "tool": "format_text",
    "element_id": "text_001",
    "changes": {"font_size": 14, "bold": True},
    "duration_ms": 12
})
```

### 9.6 配置文件结构

```yaml
# config/default.yaml
agent:
  model: "claude-sonnet-4-6"
  max_replan: 3
  temperature: 0.1

file_system:
  search_max_depth: 5           # 文件搜索最大深度
  supported_formats: [".ppt", ".pptx", ".potx", ".ppsx"]
  auto_convert_legacy: true     # 自动转换旧版.ppt

extraction:
  ocr_engine: "easyocr"         # "easyocr" | "paddleocr"
  ocr_languages: ["en", "ch"]   # OCR语言
  extract_image_dpi: 300        # 图片提取DPI

layout:
  grid_size: 0.25               # 网格大小（英寸）
  default_margins: [0.5, 0.5]   # 默认边距

knowledge:
  rag_db_path: "./data/vector_db"
  template_path: "./data/templates"

output:
  preview_dpi: 150
  export_formats: ["pptx", "pdf", "png"]
```

---

## 10. 风险与缓解策略

| 风险                                | 影响 | 概率 | 缓解策略                                                          |
| ----------------------------------- | ---- | ---- | ----------------------------------------------------------------- |
| .ppt旧格式兼容性差                  | 高   | 中   | 使用LibreOffice headless做前置转换；对转换失败的提供手动上传.pptx |
| 复杂公式OMML解析不完整              | 中   | 中   | 结合OCR方案兜底；对于多行公式提供LaTeX重写                        |
| SmartArt/复杂GroupShape无法准确还原 | 中   | 高   | 提供"作为图片保留"选项；记录结构供LLM理解                         |
| LLM幻觉导致编辑出错                 | 高   | 中   | Evaluator严格校验；undo机制兜底；关键操作要求LLM输出推理过程      |
| 大文件（>100MB）性能瓶颈            | 低   | 中   | 懒加载slide；图片按需提取；异步处理                               |
| OCR准确率不足                       | 中   | 中   | 双引擎（PaddleOCR + EasyOCR）取置信度高者                         |
| 中文特殊格式（竖排、艺术字）        | 低   | 高   | 标记为"部分支持"；转换为图片保留视觉效果                          |
| Agentic Loop陷入死循环              | 中   | 低   | 最大迭代次数限制；超时机制；用户可中断                            |

---

## 附录

### A. 项目目录结构总览

```
PPTAgent/
├── pptagent/
│   ├── __init__.py
│   ├── agent/                    # Agent编排
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── evaluator.py
│   │   ├── reflector.py
│   │   ├── loop_controller.py
│   │   └── prompts/
│   ├── tools/                    # 工具集
│   │   ├── __init__.py
│   │   ├── base.py               # BaseTool, ToolResult, ToolRegistry
│   │   ├── file/                 # 文件工具 (T01-T05)
│   │   ├── extraction/           # 提取工具 (T06-T13)
│   │   ├── manipulation/         # 编辑工具 (T14-T20)
│   │   ├── insertion/            # 插入工具 (T21-T30)
│   │   ├── layout/               # 布局工具 (T31-T34)
│   │   ├── slide/                # 幻灯片工具 (T35-T38)
│   │   ├── search/               # 搜索工具 (T39-T41)
│   │   └── utility/              # 工具类 (T42-T45)
│   ├── core/                     # 核心引擎
│   │   ├── document.py           # PPTDocument / Slide / Element 模型
│   │   ├── change_manager.py     # Undo/Redo管理
│   │   ├── session.py            # Session状态管理
│   │   └── converter.py          # 格式转换 (.ppt → .pptx)
│   ├── engines/                  # 底层渲染引擎
│   │   ├── latex_engine.py       # LaTeX公式渲染
│   │   ├── mermaid_engine.py     # Mermaid图表渲染
│   │   ├── graphviz_engine.py    # Graphviz流程图渲染
│   │   ├── ocr_engine.py         # OCR引擎
│   │   └── chart_engine.py       # 图表生成引擎
│   ├── knowledge/                # 知识增强
│   │   ├── rag.py
│   │   ├── web_search.py
│   │   └── template_store.py
│   └── utils/                    # 工具函数
│       ├── logger.py
│       ├── emu_utils.py          # EMU单位转换工具
│       └── validators.py
├── config/                       # 配置文件
│   ├── default.yaml
│   └── prompts/
├── data/                         # 本地数据
│   ├── templates/
│   ├── vector_db/
│   └── samples/
├── tests/                        # 测试
│   ├── unit/
│   ├── integration/
│   └── fixtures/                 # 测试用PPT文件
├── scripts/                      # 辅助脚本
│   ├── install_deps.sh
│   └── convert_legacy.sh
├── docs/                         # 文档
├── requirements.txt
├── pyproject.toml
└── README.md
```

### B. 关键参考资源

- python-pptx 文档: https://python-pptx.readthedocs.io/
- python-pptx 源码中的 OOXML 映射: [pptx/oxml/](https://github.com/scanny/python-pptx/tree/master/src/pptx/oxml)
- OOXML 标准: ECMA-376 / ISO/IEC 29500
- LangChain Agent 文档: https://python.langchain.com/docs/modules/agents/
- PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR

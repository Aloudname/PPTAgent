# Phase 1：文件系统与基础 PPT 操作 —— 详细规划

> **阶段**：1 / 8
> **工期**：2-3 周
> **状态**：⬜ 未开始
> **前置**：[Phase 0：基础设施搭建](./1_infra.md) ✅ 已完成
> **后继**：[Phase 2：要素提取](../docs/0_plan.md#phase-2-要素提取2-3周)

---

## 目录

1. [阶段总览](#1-阶段总览)
2. [现有代码盘点](#2-现有代码盘点)
3. [任务分解](#3-任务分解)
4. [任务一：数据模型层](#4-任务一数据模型层)
5. [任务二：ChangeManager 实现](#5-任务二changemanager-实现)
6. [任务三：文件工具 (T01–T05)](#6-任务三文件工具-t01t05)
7. [任务四：幻灯片操作 (T35–T38)](#7-任务四幻灯片操作-t35t38)
8. [任务五：单元测试完善](#8-任务五单元测试完善)
9. [执行顺序与依赖图](#9-执行顺序与依赖图)
10. [文件清单](#10-文件清单)
11. [验收标准](#11-验收标准)

---

## 1. 阶段总览

### 1.1 目标陈述

> 构建 PowerPoint 文件的**内存表示**以及操作它的**文件 I/O + 幻灯片操控**工具。本阶段完成后，Agent 能够发现、打开、检视、修改幻灯片、保存和重命名 PPT 文件——并具备完整的 undo/redo 支持。

### 1.2 范围界定

| 本阶段范围 | 不在范围内（→ 后续阶段） |
|----------|-------------------------------|
| `PPTDocument` / `Slide` / `Element` 数据模型 | 从要素中提取文本/图片/表格（→ Phase 2） |
| 文件查找器（正则/glob，递归） | 编辑要素位置/尺寸/字体（→ Phase 3） |
| 打开 / 保存 / 另存为 / 关闭 PPT 文件 | 插入新内容（→ Phase 3–4） |
| 通过 LibreOffice 转换 .ppt → .pptx | OCR、公式渲染（→ Phase 2, 4） |
| 添加 / 删除 / 排序 / 复制幻灯片 | 自动布局、模板（→ Phase 5） |
| 通过 ChangeManager 实现 undo/redo | Agentic Loop 集成（→ Phase 6） |
| 单元测试覆盖率 ≥85% | RAG、联网搜索（→ Phase 7） |

### 1.3 交付物一览

| # | 交付物 | 新建文件 | 修改文件 |
|---|-------------|-----------|----------------|
| D1 | 数据模型类 | `core/document.py` | `core/__init__.py` |
| D2 | ChangeManager（undo/redo） | — | `core/change_manager.py` |
| D3 | 文件工具（T01–T05） | `tools/file/finder.py`, `tools/file/io.py` | `tools/file/__init__.py` |
| D4 | 幻灯片工具（T35–T38） | `tools/slide/*.py`（4 个文件） | `tools/slide/__init__.py` |
| D5 | 格式转换器（.ppt→.pptx） | — | `core/converter.py` |
| D6 | 单元测试 | `tests/unit/core/test_document.py`、`tests/unit/tools/file/test_finder.py` 等 | `tests/unit/core/test_change_manager.py` |

---

## 2. 现有代码盘点

### 2.1 已存在的文件

```
pptagent/
├── __init__.py              ✅ version, exception re-exports
├── core/
│   ├── __init__.py          ✅ placeholder imports (commented out)
│   ├── exceptions.py        ✅ 8 exception classes
│   └── change_manager.py    ⚠️  Stub only (empty ChangeManager, ChangeRecord)
├── tools/
│   ├── __init__.py          ✅ placeholder
│   ├── base.py              ✅ BaseTool, ToolResult, ToolRegistry
│   ├── file/__init__.py     ⬜ Empty
│   └── slide/__init__.py    ⬜ Empty
└── utils/
    ├── logger.py            ✅ Structured + plain logging
    └── config.py            ✅ Pydantic Settings config loader

tests/
├── conftest.py              ✅ 8 fixtures
├── unit/core/
│   ├── test_exceptions.py   ✅ 5 test methods
│   └── test_change_manager.py ⚠️  Tests written, import skipped (ChangeManager stub)
└── unit/tools/
    └── test_base.py         ✅ 6 test methods
```

### 2.2 需创建或完成的文件

| 文件 | 当前状态 | 目标状态 |
|------|--------------|--------------|
| `core/document.py` | **不存在** | PPTDocument、Slide、Element、TextFormat、CursorState 等 dataclass |
| `core/change_manager.py` | 空壳占位 | 完整的 ChangeManager + ChangeRecord（含 undo/redo 栈） |
| `core/converter.py` | **不存在** | 基于 LibreOffice 的 `convert_ppt_to_pptx()` |
| `core/session.py` | **不存在** | SessionState、WorkingMemory dataclass |
| `tools/file/finder.py` | **不存在** | `find_ppt_files()` 工具（T01） |
| `tools/file/io.py` | **不存在** | `open_ppt`、`save_ppt`、`save_ppt_as`、`close_ppt`（T02–T05） |
| `tools/slide/add.py` | **不存在** | `add_slide`（T35） |
| `tools/slide/delete.py` | **不存在** | `delete_slide`（T36） |
| `tools/slide/reorder.py` | **不存在** | `reorder_slides`（T37） |
| `tools/slide/duplicate.py` | **不存在** | `duplicate_slide`（T38） |

---

## 3. 任务分解

```
Phase 1
│
├── Task 1: Data Model Layer (3 days)
│   ├── 1.1  TextFormat dataclass
│   ├── 1.2  Element dataclass
│   ├── 1.3  Slide dataclass
│   ├── 1.4  PPTDocument dataclass
│   └── 1.5  CursorState + DocumentMetadata
│
├── Task 2: ChangeManager (1 day)
│   ├── 2.1  ChangeRecord dataclass
│   ├── 2.2  ChangeManager (undo/redo stack)
│   └── 2.3  Integrate with PPTDocument
│
├── Task 3: File Tools T01–T05 (3 days)
│   ├── 3.1  find_ppt_files (T01)
│   ├── 3.2  open_ppt (T02)
│   ├── 3.3  save_ppt / save_ppt_as (T03–T04)
│   ├── 3.4  close_ppt (T05)
│   └── 3.5  .ppt → .pptx converter (core/converter.py)
│
├── Task 4: Slide Operations T35–T38 (2 days)
│   ├── 4.1  add_slide (T35)
│   ├── 4.2  delete_slide (T36)
│   ├── 4.3  reorder_slides (T37)
│   └── 4.4  duplicate_slide (T38)
│
└── Task 5: Testing & Integration (2 days)
    ├── 5.1  test_document.py
    ├── 5.2  test_converter.py
    ├── 5.3  test_finder.py + test_io.py
    ├── 5.4  test_slide_operations.py
    ├── 5.5  Update test_change_manager.py
    └── 5.6  Cross-module integration tests
```

---

## 4. 任务一：数据模型层

> **文件**：`pptagent/core/document.py`
> **依赖**：`core/exceptions.py`（已存在）

### 4.1 子任务 1.1 — `TextFormat`

```python
@dataclass
class TextFormat:
    """Complete description of text formatting properties.

    Mirrors the full set of run-level properties in OOXML CT_TextCharacterProperties.
    """
    font_name: str = "Calibri"
    font_size: float = 12.0          # in points (pt)
    font_color: str = "#000000"      # HEX RGBA or "theme"
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    superscript: bool = False
    subscript: bool = False
    highlight: str | None = None     # highlight color HEX, or None
    alignment: str = "left"          # "left" | "center" | "right" | "justify"
    line_spacing: float = 1.0        # multiplier (1.0 = single)
    paragraph_spacing: float = 0.0   # space before/after in pt

    @classmethod
    def from_run(cls, run) -> "TextFormat":
        """Extract TextFormat from a python-pptx Run object."""
        ...
```

**关键设计决策**：
- `font_color` 使用 HEX 字符串（`"#FF0000"`）——python-pptx 的 `RGBColor` 在边界处转换。
- `alignment` 使用字符串枚举而非 `pptx.enum.text.PP_ALIGN`，避免模型层耦合 python-pptx 内部实现。

### 4.2 子任务 1.2 — `Element`

```python
@dataclass
class Element:
    """A single foreground element on a slide.

    This is an abstraction over python-pptx shapes, grouping them by semantic type.
    """
    id: str                           # unique id, format: "{type}_{uuid8}"
    type: str                         # "text" | "image" | "table" | "chart"
                                      # | "formula" | "diagram" | "media" | "shape"
    position: tuple[float, float, float, float]  # (left, top, width, height) in EMU
    content: Any                      # type-specific payload (str, bytes, DataFrame, etc.)
    format: TextFormat | None = None  # text formatting (None for non-text elements)
    z_order: int = 0                  # stacking order
    metadata: dict[str, Any] = field(default_factory=dict)  # animation, hyperlinks, alt-text, etc.

    # --- EMU conversion helpers (static methods) ---
    @staticmethod
    def emu_to_inches(emu: int) -> float: ...
    @staticmethod
    def inches_to_emu(inches: float) -> int: ...
    @staticmethod
    def emu_to_cm(emu: int) -> float: ...
    @staticmethod
    def cm_to_emu(cm: float) -> int: ...
```

**关键设计决策**：
- `position` 始终使用 EMU（英制公制单位，1 英寸 = 914400 EMU）——与 python-pptx 内部表示一致。
- `type` 枚举覆盖 plan §3.3.1 中所有语义要素类型，为后续阶段基于类型的分发奠定基础。
- `content` 为 `Any` 类型，因为不同类型承载完全不同性质的数据（文本用 str、图片用 bytes、表格用 DataFrame）。

### 4.3 子任务 1.3 — `Slide`

```python
@dataclass
class Slide:
    """A single slide within a presentation."""
    index: int                        # 0-based position in the slide list
    layout_name: str = "Blank"        # slide layout name (e.g., "Title Slide")
    elements: dict[str, Element] = field(default_factory=dict)  # element_id → Element
    background: dict[str, Any] = field(default_factory=dict)    # fill color, image, etc.
    notes: str = ""                   # speaker notes (plain text)
```

### 4.4 子任务 1.4 — `PPTDocument`

```python
@dataclass
class PPTDocument:
    """In-memory representation of a PowerPoint file.

    This is the central data structure that all tools read from and write to.
    It wraps a python-pptx Presentation object and provides a higher-level,
    element-oriented view of the content.
    """
    file_path: str | None = None      # None when created from scratch (not yet saved)
    file_name: str = "Untitled.pptx"
    slides: list[Slide] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    change_manager: ChangeManager | None = None  # lazily initialized
    cursor: CursorState = field(default_factory=CursorState)

    # --- Factory methods ---
    @classmethod
    def from_file(cls, path: str | Path) -> "PPTDocument":
        """Load a PPTDocument from a .pptx (or .ppt via conversion) file."""
        ...

    @classmethod
    def from_scratch(cls) -> "PPTDocument":
        """Create an empty single-slide presentation."""
        ...

    # --- Serialization ---
    def to_file(self, path: str | Path | None = None) -> str:
        """Write the document back to a .pptx file. Returns the saved path."""
        ...

    # --- Slide access ---
    def get_slide(self, index: int) -> Slide: ...
    def get_element(self, slide_index: int, element_id: str) -> Element: ...

    # --- Undo/redo delegation ---
    def record_change(self, change: ChangeRecord) -> None: ...
    def undo(self) -> ChangeRecord | None: ...
    def redo(self) -> ChangeRecord | None: ...
```

### 4.5 子任务 1.5 — `CursorState` and `DocumentMetadata`

```python
@dataclass
class CursorState:
    """Tracks the user's current position in the document."""
    current_slide_index: int = 0
    selected_element_ids: list[str] = field(default_factory=list)

@dataclass
class BackgroundInfo:
    fill_color: str | None = None      # HEX
    image_path: str | None = None
```

### 4.6 子任务间依赖关系

```
TextFormat ──► Element ──► Slide ──► PPTDocument
                 │
                 └──► CursorState
```

五个子任务全部写入同一个文件 `core/document.py`，因为它们构成紧耦合模块。

---

## 5. 任务二：ChangeManager 实现

> **文件**：`pptagent/core/change_manager.py`（替换空壳）
> **测试**：`tests/unit/core/test_change_manager.py`（已编写，待实现后激活）

### 5.1 子任务 2.1 — `ChangeRecord`

```python
@dataclass
class ChangeRecord:
    """A single undoable/redoable change."""
    id: str                           # unique change id
    timestamp: float                  # time.time() when change was made
    operation: str                    # human-readable operation name
    target_element: str               # element_id that was changed
    slide_index: int                  # which slide the element belongs to
    before_state: Any                 # snapshot before the change
    after_state: Any                  # snapshot after the change
```

### 5.2 子任务 2.2 — `ChangeManager`

```python
class ChangeManager:
    """Manages undo and redo stacks for a PPTDocument.

    Constraints:
    - max_history limits the undo stack size (default 100).
    - Recording a new change clears the redo stack (standard behavior).
    """

    def __init__(self, max_history: int = 100) -> None:
        self.undo_stack: list[ChangeRecord] = []
        self.redo_stack: list[ChangeRecord] = []
        self.max_history = max_history

    def record(self, change: ChangeRecord) -> None:
        """Push a change onto the undo stack, clear redo stack, enforce max_history."""
        ...

    def undo(self) -> ChangeRecord | None:
        """Pop the most recent change from undo stack, push to redo stack."""
        ...

    def redo(self) -> ChangeRecord | None:
        """Pop the most recent undone change from redo stack, push to undo stack."""
        ...

    def clear(self) -> None:
        """Clear both stacks (e.g., when closing a document)."""
        ...

    def can_undo(self) -> bool: ...
    def can_redo(self) -> bool: ...
```

### 5.3 子任务 2.3 — Integration with PPTDocument

`PPTDocument` 类持有一个 `ChangeManager` 实例。每个修改文档的工具在返回前**必须**调用 `doc.record_change(...)`。Phase 1 中通过约定强制执行；Phase 3 可引入更严格的装饰器方案。

```python
# In PPTDocument:
def record_change(self, change: ChangeRecord) -> None:
    if self.change_manager is None:
        self.change_manager = ChangeManager()
    self.change_manager.record(change)
```

---

## 6. 任务三：文件工具（T01–T05）

> **Files**: `tools/file/finder.py`, `tools/file/io.py`, `core/converter.py`
> **Depends on**: Task 1 (PPTDocument), Task 2 (ChangeManager)

### 6.1 子任务 3.1 — T01 `find_ppt_files`

**工具**：`find_ppt_files`
**Schema**：
```json
{
  "name": "find_ppt_files",
  "description": "Recursively search a directory for PowerPoint files (.ppt, .pptx, .potx, .ppsx). Supports glob patterns and regex filtering.",
  "parameters": {
    "search_path": {"type": "string", "description": "Root directory to search"},
    "pattern": {"type": "string", "description": "Optional glob or regex pattern to filter results"},
    "recursive": {"type": "boolean", "description": "Whether to search subdirectories (default true)"},
    "max_depth": {"type": "integer", "description": "Maximum recursion depth (0 = root only)"}
  }
}
```

**实现方案**：
```python
# tools/file/finder.py
class FindPPTFilesTool(BaseTool):
    name = "find_ppt_files"
    description = "Recursively search for PowerPoint files using glob patterns and regex."

    async def execute(self, search_path: str, pattern: str = "*",
                       recursive: bool = True, max_depth: int = 5) -> ToolResult:
        # 1. Validate search_path exists and is a directory
        # 2. If recursive, use pathlib.rglob; else use pathlib.glob
        # 3. Filter by supported extensions: .ppt, .pptx, .potx, .ppsx
        # 4. If pattern is a regex, apply re.search on filename
        # 5. Return sorted list of matching Path objects (as strings)
        ...
```

### 6.2 子任务 3.2 — T02 `open_ppt`

**工具**：`open_ppt`
**Schema**：
```json
{
  "name": "open_ppt",
  "description": "Open a PowerPoint file and load it into the in-memory document model. Automatically converts legacy .ppt to .pptx if needed.",
  "parameters": {
    "file_path": {"type": "string", "description": "Absolute or relative path to the .ppt/.pptx file"}
  }
}
```

**实现方案**：
```python
# tools/file/io.py
class OpenPPTTool(BaseTool):
    name = "open_ppt"
    description = "Open a PowerPoint file and load it into memory."

    async def execute(self, file_path: str) -> ToolResult:
        # 1. Normalize path, check file exists
        # 2. If .ppt, call convert_ppt_to_pptx() first (Subtask 3.5)
        # 3. Load via PPTDocument.from_file()
        # 4. Store in SessionState as "current document"
        # 5. Return document summary: slide count, file size, etc.
        ...
```

### 6.3 子任务 3.3 — T03/T04 Save Operations

**工具**：`save_ppt`（T03）、`save_ppt_as`（T04）

```python
class SavePPTTool(BaseTool):
    name = "save_ppt"
    description = "Save the current in-memory document to its original file path."

    async def execute(self) -> ToolResult:
        # 1. Get current document from SessionState
        # 2. If from_scratch (no file_path), raise error → suggest save_ppt_as
        # 3. Serialize PPTDocument → python-pptx Presentation → .pptx bytes
        # 4. Write to file_path
        # 5. Return confirmation + file size
        ...

class SavePPTAsTool(BaseTool):
    name = "save_ppt_as"
    description = "Save the current document to a new file path (Save As / Rename)."

    async def execute(self, new_path: str) -> ToolResult:
        # 1. Validate new_path directory exists
        # 2. Serialize and write
        # 3. Update PPTDocument.file_path
        # 4. Return confirmation
        ...
```

### 6.4 子任务 3.4 — T05 `close_ppt`

```python
class ClosePPTTool(BaseTool):
    name = "close_ppt"
    description = "Close the current presentation, optionally saving changes."

    async def execute(self, save: bool = True) -> ToolResult:
        # 1. If save and dirty, call save_ppt logic
        # 2. Clear SessionState.current_document
        # 3. Return confirmation
        ...
```

### 6.5 子任务 3.5 — `.ppt → .pptx` Converter

```python
# core/converter.py

def find_libreoffice() -> str | None:
    """Locate LibreOffice binary. Priority:
    1. LIBREOFFICE_PATH env var
    2. shutil.which("libreoffice")   ← most Linux systems
    3. shutil.which("soffice")       ← macOS / alternate name
    4. ~/.local/bin/libreoffice*     ← AppImage / manual extract
    """
    ...

def convert_ppt_to_pptx(source: str | Path) -> Path:
    """Convert a legacy .ppt file to .pptx using LibreOffice headless.

    Raises ConversionError if:
    - LibreOffice is not found
    - The input file is not a .ppt
    - The conversion process fails or times out
    """
    # 1. Find libreoffice binary
    # 2. Run: libreoffice --headless --convert-to pptx --outdir <tmp> <source>
    # 3. Wait for output file (with timeout using config.libreoffice_timeout)
    # 4. Return path to converted .pptx
    ...
```

---

## 7. 任务四：幻灯片操作（T35–T38）

> **文件**：`tools/slide/add.py`、`delete.py`、`reorder.py`、`duplicate.py`
> **依赖**：任务一（PPTDocument）、任务二（ChangeManager）

### 7.1 子任务 4.1 — T35 `add_slide`

```python
class AddSlideTool(BaseTool):
    name = "add_slide"
    description = "Add a new blank slide at the specified position."

    async def execute(self, position: int | None = None,
                       layout: str = "Blank") -> ToolResult:
        # 1. position=None means append at end
        # 2. Create Slide object with next index
        # 3. Insert into PPTDocument.slides at position
        # 4. Re-index subsequent slides
        # 5. Record ChangeRecord (before_state=slide_list_snapshot)
        ...
```

### 7.2 子任务 4.2 — T36 `delete_slide`

```python
class DeleteSlideTool(BaseTool):
    name = "delete_slide"
    description = "Delete a slide by index."

    async def execute(self, slide_index: int) -> ToolResult:
        # 1. Validate slide_index is in range
        # 2. Save before_state snapshot
        # 3. Remove slide from PPTDocument.slides
        # 4. Re-index remaining slides
        # 5. Record ChangeRecord for undo
        ...
```

### 7.3 子任务 4.3 — T37 `reorder_slides`

```python
class ReorderSlidesTool(BaseTool):
    name = "reorder_slides"
    description = "Change the order of slides by providing a new index ordering."

    async def execute(self, new_order: list[int]) -> ToolResult:
        # 1. Validate new_order is a permutation of current indices
        # 2. Reorder PPTDocument.slides
        # 3. Re-index
        # 4. Record change
        ...
```

### 7.4 子任务 4.4 — T38 `duplicate_slide`

```python
class DuplicateSlideTool(BaseTool):
    name = "duplicate_slide"
    description = "Duplicate an existing slide."

    async def execute(self, slide_index: int,
                       insert_after: bool = True) -> ToolResult:
        # 1. Deep-copy the Slide object (including all Elements)
        # 2. Regenerate element IDs to avoid collisions
        # 3. Insert at slide_index + 1 (or slide_index if insert_after=False)
        # 4. Re-index
        # 5. Record change
        ...
```

---

## 8. 任务五：单元测试完善

> **目标**：`pptagent/core/`、`pptagent/tools/file/`、`pptagent/tools/slide/` 行覆盖率 ≥85%

### 8.1 新建测试文件

| 测试文件 | 测试对象 | 关键测试用例 |
|-----------|-----------|----------------|
| `tests/unit/core/test_document.py` | PPTDocument、Slide、Element、TextFormat | 构造、EMU 单位转换、from_file（mock pptx）、序列化、要素查找 |
| `tests/unit/core/test_converter.py` | convert_ppt_to_pptx | LibreOffice 找到/未找到、.ppt 转换成功、超时处理、非 .ppt 输入 |
| `tests/unit/tools/file/test_finder.py` | find_ppt_files（T01） | 递归搜索、glob 过滤、正则过滤、max_depth、空目录、无匹配 |
| `tests/unit/tools/file/test_io.py` | open/save/close（T02–T05） | 打开有效 .pptx、打开不存在文件、保存到新路径、不保存关闭 |
| `tests/unit/tools/slide/test_slide_ops.py` | T35–T38 | 添加幻灯片、删除幻灯片、排序、复制、边界情况（空文档、最后一张） |

### 8.2 需更新的已有测试文件

| 测试文件 | 需要的修改 |
|-----------|--------------|
| `tests/unit/core/test_change_manager.py` | ChangeManager 实现后移除 `pytestmark = pytest.mark.skipif(...)` |

### 8.3 需新增的测试 Fixtures

```python
# In tests/conftest.py — add these:

@pytest.fixture
def sample_pptx_path(fixtures_dir: Path) -> Path:
    """Path to a real .pptx file for integration tests."""
    ...

@pytest.fixture
def empty_document() -> PPTDocument:
    """A fresh PPTDocument created from scratch."""
    return PPTDocument.from_scratch()

@pytest.fixture
def document_with_slides() -> PPTDocument:
    """A PPTDocument with 3 slides, each containing known elements."""
    doc = PPTDocument.from_scratch()
    for i in range(3):
        slide = Slide(index=i)
        slide.elements[f"text_{i}"] = Element(
            id=f"text_{i}", type="text",
            position=(100000, 100000, 500000, 300000),
            content="Hello",
        )
        doc.slides.append(slide)
    return doc
```

---

## 9. 执行顺序与依赖图

```
Day 1–3  │  Task 1: Data Model Layer
         │  └── core/document.py (TextFormat → Element → Slide → PPTDocument)
         │
Day 4    │  Task 2: ChangeManager
         │  └── core/change_manager.py (stub → full impl)
         │
Day 5–7  │  Task 3: File Tools
         │  └── core/converter.py (LibreOffice wrapper)
         │  └── tools/file/finder.py (T01)
         │  └── tools/file/io.py (T02–T05)
         │
Day 8–9  │  Task 4: Slide Operations
         │  └── tools/slide/{add,delete,reorder,duplicate}.py
         │
Day 10–12│  Task 5: Testing & Integration
         │  └── Write new test files
         │  └── Activate existing test_change_manager.py
         │  └── Coverage review, edge case hardening
```

```
Dependency graph:

  TextFormat ──► Element ──► Slide ──► PPTDocument
                                            │
                     ┌──────────────────────┼──────────────────────┐
                     ▼                      ▼                      ▼
               ChangeManager          File Tools           Slide Operations
               (Task 2)              (Task 3)               (Task 4)
                     │                      │                      │
                     └──────────────────────┼──────────────────────┘
                                            ▼
                                     Unit Tests
                                      (Task 5)
```

---

## 10. 文件清单

### 新建文件（共 13 个）

```
pptagent/core/
├── document.py              ← NEW  Task 1: full data model
├── converter.py             ← NEW  Task 3.5: .ppt→.pptx
└── session.py               ← NEW  SessionState, WorkingMemory

pptagent/tools/file/
├── finder.py                ← NEW  Task 3.1: T01
└── io.py                    ← NEW  Task 3.2–3.4: T02–T05

pptagent/tools/slide/
├── add.py                   ← NEW  Task 4.1: T35
├── delete.py                ← NEW  Task 4.2: T36
├── reorder.py               ← NEW  Task 4.3: T37
└── duplicate.py             ← NEW  Task 4.4: T38

tests/unit/core/
├── test_document.py         ← NEW  Task 5
└── test_converter.py        ← NEW  Task 5

tests/unit/tools/file/
├── test_finder.py           ← NEW  Task 5
└── test_io.py               ← NEW  Task 5

tests/unit/tools/slide/
└── test_slide_ops.py        ← NEW  Task 5
```

### 修改文件（共 4 个已有文件）

```
pptagent/core/change_manager.py     ← REPLACE stub with full impl
pptagent/core/__init__.py           ← UNCOMMENT imports
pptagent/tools/file/__init__.py     ← ADD exports
pptagent/tools/slide/__init__.py    ← ADD exports
tests/conftest.py                   ← ADD new fixtures
tests/unit/core/test_change_manager.py ← REMOVE skip marker
```

---

## 11. 验收标准

### 11.1 功能验收

- [ ] `PPTDocument.from_file(path)` 能加载真实 .pptx 文件并填充所有 Slide/Element 对象
- [ ] `PPTDocument.from_file(path)` 自动通过 LibreOffice 将 .ppt 转换为 .pptx
- [ ] `find_ppt_files` 能递归发现 .ppt/.pptx 文件，支持正则过滤
- [ ] `open_ppt` → `save_ppt` → `close_ppt` 完整回路保持文件完整性（二进制 diff 一致）
- [ ] `save_ppt_as` 能创建新文件并更新文档路径
- [ ] 所有幻灯片操作（添加/删除/排序/复制）均可正常工作且可撤销
- [ ] Undo/redo 能正确撤销和重做变更
- [ ] ChangeManager 强制执行 `max_history` 上限，且新记录会清空 redo 栈

### 11.2 代码质量

- [ ] 所有新代码通过 `ruff check`、`black --check`、`isort --check-only`
- [ ] `mypy pptagent/` 在新模块上零错误
- [ ] 所有 docstring 遵循 Google 风格格式
- [ ] `pptagent/core/`、`pptagent/tools/file/`、`pptagent/tools/slide/` 行覆盖率 ≥85%

### 11.3 可运行验证

```bash
# After Phase 1, these commands should all succeed:
conda activate pptagent
pytest tests/unit/core/test_document.py -v
pytest tests/unit/core/test_change_manager.py -v   # was skipped, now passes
pytest tests/unit/core/test_converter.py -v
pytest tests/unit/tools/file/ -v
pytest tests/unit/tools/slide/ -v
python -c "
from pptagent.core import PPTDocument, Slide, Element, ChangeManager
from pptagent.tools.file.finder import FindPPTFilesTool
from pptagent.tools.file.io import OpenPPTTool, SavePPTTool
print('All Phase 1 imports OK')
"
```

### 11.4 建议的 Git 提交顺序

```
feat(core): add TextFormat, Element, Slide, PPTDocument data models
feat(core): implement ChangeManager with undo/redo stacks
feat(core): add .ppt to .pptx converter via LibreOffice
feat(tools): implement T01 find_ppt_files with regex/glob support
feat(tools): implement T02-T05 open/save/save_as/close PPT tools
feat(tools): implement T35-T38 slide add/delete/reorder/duplicate
test: add unit tests for document model, file tools, and slide ops
chore: activate ChangeManager tests, update core __init__ exports
```

---

> **下一步**：Phase 1 验收通过后，进入 [Phase 2：要素提取](../docs/0_plan.md#phase-2-要素提取2-3周)——从 PPT 要素中提取文本、图片、表格、图表、公式和流程图。

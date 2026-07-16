# Phase 3：要素编辑与插入 —— 详细规划

> **阶段**：3 / 8
> **工期**：2-3 周
> **状态**：⬜ 未开始
> **前置**：[Phase 2：要素提取](./12_summary.md) ✅ 已完成
> **后继**：[Phase 4：高级内容创建](../docs/0_plan.md#phase-4-高级内容创建2-3周)

---

## 目录

1. [阶段总览](#1-阶段总览)
2. [现有代码盘点](#2-现有代码盘点)
3. [任务分解](#3-任务分解)
4. [任务一：要素编辑工具 (T14–T19)](#4-任务一要素编辑工具-t14t19)
5. [任务二：要素插入工具 (T21, T25, T26, T30)](#5-任务二要素插入工具-t21-t25-t26-t30)
6. [任务三：to_file() 扩展](#6-任务三to_file-扩展)
7. [任务四：单元测试完善](#7-任务四单元测试完善)
8. [执行顺序与依赖图](#8-执行顺序与依赖图)
9. [文件清单](#9-文件清单)
10. [验收标准](#10-验收标准)

---

## 1. 阶段总览

### 1.1 目标陈述

> Phase 2 打通了"真实 PPT → 内存模型 → 序列化"的全链路。Phase 3 在此基础上赋予 Agent **编辑现有要素**和**插入新要素**的能力。
>
> 本阶段完成后，Agent 可以接收到诸如"把第 3 页标题字体改成 Arial 20pt 加粗"、"在第二页右下角插入 data/chart.png"这样的指令，并直接在内存模型中执行修改，然后写回 .pptx 文件。

### 1.2 范围界定

| 本阶段范围 | 不在范围内（→ 后续阶段） |
|-----------|------------------------------|
| 调整要素位置 (left/top) 和尺寸 (width/height) | 批量对齐/分布 (→ Phase 5) |
| 修改文本格式属性 (font/size/color/style) | LaTeX 公式渲染插入 (→ Phase 4) |
| 删除指定要素 | 流程图/思维导图插入 (→ Phase 4) |
| 插入图片文件 | 视频/音频/动图插入 (→ Phase 4) |
| 插入文本框 | 自动布局引擎 (→ Phase 5) |
| 插入表格 | 模板系统 (→ Phase 5) |
| 插入图表 | Agentic Loop 集成 (→ Phase 6) |
| 所有编辑操作支持 undo/redo | — |
| 单元测试覆盖率 ≥85% | — |

### 1.3 交付物一览

| # | 交付物 | 新建文件 | 修改文件 |
|---|--------|---------|---------|
| D1 | 要素编辑工具 (T14–T19) | `tools/manipulation/element_geometry.py`、`text_formatter.py`、`element_delete.py` | `tools/manipulation/__init__.py` |
| D2 | 要素插入工具 (T21, T25, T26, T30) | `tools/insertion/image_inserter.py`、`text_inserter.py`、`table_inserter.py`、`chart_inserter.py` | `tools/insertion/__init__.py` |
| D3 | to_file() 扩展 (table/chart 写出) | — | `core/document.py` |
| D4 | 单元测试 (8 个测试文件) | `tests/unit/tools/manipulation/*.py`、`tests/unit/tools/insertion/*.py` | — |

---

## 2. 现有代码盘点

### 2.1 Phase 2 已完成的、可直接复用的部分

#### 2.1.1 核心数据模型（零改动）

```
pptagent/core/document.py (777 行)
├── TextFormat      ← 14 个格式字段，T16 的参数规格
├── Element         ← position/format/content 是编辑的直接目标
├── Slide           ← elements dict 承载增删操作
├── PPTDocument     ← get_slide() / get_element() 定位目标
├── from_file()     ← 打开文件 → 编辑 → to_file() 完整闭环
└── to_file()       ← 已支持 text/image 写出，Phase 3 需扩展 table/chart
```

#### 2.1.2 Undo/Redo 体系（零改动）

```
pptagent/core/change_manager.py (114 行)
├── ChangeRecord    ← id / operation / target_element / slide_index / before_state / after_state
└── ChangeManager   ← undo_stack + redo_stack, record() / undo() / redo() / clear()
```

每个编辑工具执行时：
1. 操作前深拷贝目标状态 → `before_state`
2. 执行修改
3. 深拷贝修改后状态 → `after_state`
4. 构造 `ChangeRecord` → `doc.record_change(record)`

#### 2.1.3 会话与配置（零改动）

| 组件 | 文件 | 用途 |
|------|------|------|
| `get_session()` | `core/session.py` | 获取 `current_document` |
| `get_config().agent.confirm_*` | `utils/config.py` | 批量编辑/删除/保存的确认策略 |
| `ToolResult` + `BaseTool` | `tools/base.py` | 统一返回规范 |
| `ToolRegistry` | `tools/base.py` | 工具注册 |

#### 2.1.4 序列化基础（Phase 3 需扩写）

| 函数 | 已有能力 | Phase 3 需新增 |
|------|---------|---------------|
| `to_file()` | 写出 text / image 元素 | 写出 table / chart 元素 |
| `_write_text_element()` | 完整可用 | 不改动 |
| `_write_image_element()` | 完整可用 | 不改动 |

### 2.2 待创建的文件

```
pptagent/tools/manipulation/       ← 目录已存在，仅有空 __init__.py
├── __init__.py                    ← 需添加导出
├── element_geometry.py            ← T14 set_position + T15 set_size
├── text_formatter.py              ← T16 format_text + T17 set_alignment + T18 set_text_effect
└── element_delete.py              ← T19 delete_element

pptagent/tools/insertion/          ← 目录已存在，仅有空 __init__.py
├── __init__.py                    ← 需添加导出
├── image_inserter.py              ← T21 insert_image
├── text_inserter.py               ← T25 insert_text_box
├── table_inserter.py              ← T26 insert_table
└── chart_inserter.py              ← T30 insert_chart
```

### 2.3 需修改的文件

| 文件 | 当前状态 | 修改内容 |
|------|---------|---------|
| `core/document.py` | `to_file()` 仅写出 text/image | 新增 table/chart 元素写出逻辑 |
| `tools/manipulation/__init__.py` | 空文件 | 添加 4 个工具类的导出 |
| `tools/insertion/__init__.py` | 空文件 | 添加 4 个工具类的导出 |

---

## 3. 任务分解

```
Phase 3
│
├── Task 1: 要素编辑工具 T14–T19 (3 days)
│   ├── 1.1  T14 set_position — 调整要素位置
│   ├── 1.2  T15 set_size — 调整要素尺寸
│   ├── 1.3  T16 format_text — 修改文本格式（核心）
│   ├── 1.4  T17 set_alignment — 设置对齐方式
│   ├── 1.5  T18 set_text_effect — 设置文字效果
│   └── 1.6  T19 delete_element — 删除要素
│
├── Task 2: 要素插入工具 T21,T25,T26,T30 (3 days)
│   ├── 2.1  T21 insert_image — 插入图片
│   ├── 2.2  T25 insert_text_box — 插入文本框
│   ├── 2.3  T26 insert_table — 插入表格
│   └── 2.4  T30 insert_chart — 插入图表
│
├── Task 3: to_file() 扩展 (1 day)
│   ├── 3.1  _write_table_element() 实现
│   └── 3.2  _write_chart_element() 实现
│
└── Task 4: 单元测试完善 (3 days)
    ├── 4.1  test_element_geometry.py
    ├── 4.2  test_text_formatter.py
    ├── 4.3  test_element_delete.py
    ├── 4.4  test_image_inserter.py
    ├── 4.5  test_text_inserter.py
    ├── 4.6  test_table_inserter.py
    ├── 4.7  test_chart_inserter.py
    └── 4.8  test_document_roundtrip_edit.py (集成测试)
```

---

## 4. 任务一：要素编辑工具 (T14–T19)

> **目录**：`pptagent/tools/manipulation/`
> **依赖**：PPTDocument / Element / TextFormat / ChangeManager（全部已完成）

### 4.1 子任务 1.1 + 1.2 — `element_geometry.py` (T14, T15)

将 T14 (`set_position`) 和 T15 (`set_size`) 合并为一个文件——它们操作的都是 `Element.position` 元组。

```python
# pptagent/tools/manipulation/element_geometry.py

class SetPositionTool(BaseTool):
    """T14: Adjust the position (left, top) of an element."""
    name = "set_position"
    description = (
        "Move an element to a new position on the slide. "
        "Coordinates are in EMU (1 inch = 914400 EMU)."
    )

    schema = {
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based index of the slide containing the element.",
            },
            "element_id": {
                "type": "string",
                "description": "Unique ID of the element to move.",
            },
            "left": {
                "type": "number",
                "description": "New distance from the left edge, in EMU.",
            },
            "top": {
                "type": "number",
                "description": "New distance from the top edge, in EMU.",
            },
        },
        "required": ["slide_index", "element_id", "left", "top"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        element_id: str,
        left: float,
        top: float,
    ) -> ToolResult:
        ...


class SetSizeTool(BaseTool):
    """T15: Adjust the size (width, height) of an element."""
    name = "set_size"
    description = (
        "Resize an element on the slide. "
        "Dimensions are in EMU (1 inch = 914400 EMU)."
    )

    schema = {
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index.",
            },
            "element_id": {
                "type": "string",
                "description": "Unique ID of the element to resize.",
            },
            "width": {
                "type": "number",
                "description": "New width in EMU.",
            },
            "height": {
                "type": "number",
                "description": "New height in EMU.",
            },
            "lock_aspect_ratio": {
                "type": "boolean",
                "description": "If true, adjust the unspecified dimension to preserve aspect ratio (default false).",
            },
        },
        "required": ["slide_index", "element_id", "width", "height"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        element_id: str,
        width: float,
        height: float,
        lock_aspect_ratio: bool = False,
    ) -> ToolResult:
        ...
```

**核心实现逻辑**（两个工具共用）：

```python
def _update_position(
    doc: PPTDocument,
    slide_index: int,
    element_id: str,
    left: float | None = None,
    top: float | None = None,
    width: float | None = None,
    height: float | None = None,
) -> tuple[Element, dict, dict]:
    """Partially update element position. Returns (element, before_state, after_state)."""
    import copy

    el = doc.get_element(slide_index, element_id)
    old_pos = el.position  # (left, top, width, height)
    before = {"position": old_pos}

    new_pos = (
        left if left is not None else old_pos[0],
        top if top is not None else old_pos[1],
        width if width is not None else old_pos[2],
        height if height is not None else old_pos[3],
    )
    el.position = new_pos
    after = {"position": new_pos}
    return el, before, after
```

**undo 记录模式**：

```python
from pptagent.core.change_manager import ChangeRecord

doc.record_change(ChangeRecord(
    operation="set_position",       # or "set_size"
    target_element=element_id,
    slide_index=slide_index,
    before_state=before,
    after_state=after,
))
```

---

### 4.2 子任务 1.3 — `text_formatter.py` (T16)

Phase 3 最复杂的编辑工具。`TextFormat` 有 14 个字段，T16 需要支持任意子集的"部分更新"——只修改传入的字段，保留其他字段不变。

```python
# pptagent/tools/manipulation/text_formatter.py

class FormatTextTool(BaseTool):
    """T16: Modify one or more text formatting properties."""
    name = "format_text"
    description = (
        "Modify text formatting for a specific text element. "
        "Only the properties you specify will be changed; omitted properties "
        "keep their current values. All colour values use HEX format (#RRGGBB)."
    )

    schema = {
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index.",
            },
            "element_id": {
                "type": "string",
                "description": "Unique ID of the text element to format.",
            },
            "font_name": {
                "type": "string",
                "description": "Font family name (e.g. 'Arial', 'Times New Roman').",
            },
            "font_size": {
                "type": "number",
                "description": "Font size in points (pt).",
            },
            "font_color": {
                "type": "string",
                "description": "Font colour in HEX format (e.g. '#FF0000' for red).",
            },
            "bold": {
                "type": "boolean",
                "description": "Enable or disable bold.",
            },
            "italic": {
                "type": "boolean",
                "description": "Enable or disable italic.",
            },
            "underline": {
                "type": "boolean",
                "description": "Enable or disable underline.",
            },
            "strikethrough": {
                "type": "boolean",
                "description": "Enable or disable strikethrough.",
            },
            "superscript": {
                "type": "boolean",
                "description": "Enable superscript.",
            },
            "subscript": {
                "type": "boolean",
                "description": "Enable subscript.",
            },
            "highlight": {
                "type": "string",
                "description": "Highlight colour in HEX format (e.g. '#FFFF00').",
            },
            "alignment": {
                "type": "string",
                "enum": ["left", "center", "right", "justify"],
                "description": "Text horizontal alignment.",
            },
            "line_spacing": {
                "type": "number",
                "description": "Line spacing multiplier (1.0 = single, 1.5 = 1.5 lines).",
            },
            "paragraph_spacing": {
                "type": "number",
                "description": "Space before/after paragraphs in points (pt).",
            },
        },
        "required": ["slide_index", "element_id"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        element_id: str,
        font_name: str | None = None,
        font_size: float | None = None,
        font_color: str | None = None,
        bold: bool | None = None,
        italic: bool | None = None,
        underline: bool | None = None,
        strikethrough: bool | None = None,
        superscript: bool | None = None,
        subscript: bool | None = None,
        highlight: str | None = None,
        alignment: str | None = None,
        line_spacing: float | None = None,
        paragraph_spacing: float | None = None,
    ) -> ToolResult:
        ...
```

**部分更新逻辑**：

```python
import copy

el = doc.get_element(slide_index, element_id)
if el.type != "text":
    return ToolResult(success=False, error=f"Element {element_id} is not a text element")

if el.format is None:
    el.format = TextFormat()

before = {"format": copy.deepcopy(el.format)}

# Apply only the non-None fields
for field_name in ("font_name", "font_size", "font_color", "bold", "italic",
                    "underline", "strikethrough", "superscript", "subscript",
                    "highlight", "alignment", "line_spacing", "paragraph_spacing"):
    value = locals().get(field_name)
    if value is not None:
        setattr(el.format, field_name, value)

after = {"format": copy.deepcopy(el.format)}
```

---

### 4.3 子任务 1.4 — `text_formatter.py` (T17)

T17 (`set_alignment`) 是 T16 的快捷工具——只修改对齐方式，参数更少，LLM 更容易正确调用。

```python
class SetAlignmentTool(BaseTool):
    """T17: Set the text alignment for an element."""
    name = "set_alignment"
    description = "Set the horizontal text alignment of a text element."

    schema = {
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index.",
            },
            "element_id": {
                "type": "string",
                "description": "Unique ID of the text element.",
            },
            "alignment": {
                "type": "string",
                "enum": ["left", "center", "right", "justify"],
                "description": "Horizontal alignment to apply.",
            },
        },
        "required": ["slide_index", "element_id", "alignment"],
    }

    async def execute(  # type: ignore[override]
        self, slide_index: int, element_id: str, alignment: str,
    ) -> ToolResult:
        ...
```

---

### 4.4 子任务 1.5 — `text_formatter.py` (T18)

T18 (`set_text_effect`) 是 T16 的另一个快捷工具——只修改 6 个布尔效果标志。

```python
class SetTextEffectTool(BaseTool):
    """T18: Toggle text effects (bold, italic, underline, etc.)."""
    name = "set_text_effect"
    description = (
        "Toggle one or more text effects for a text element. "
        "Unspecified effects keep their current state."
    )

    schema = {
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index.",
            },
            "element_id": {
                "type": "string",
                "description": "Unique ID of the text element.",
            },
            "bold": {"type": "boolean", "description": "Enable or disable bold."},
            "italic": {"type": "boolean", "description": "Enable or disable italic."},
            "underline": {"type": "boolean", "description": "Enable or disable underline."},
            "strikethrough": {"type": "boolean", "description": "Enable or disable strikethrough."},
            "superscript": {"type": "boolean", "description": "Enable superscript."},
            "subscript": {"type": "boolean", "description": "Enable subscript."},
        },
        "required": ["slide_index", "element_id"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        element_id: str,
        bold: bool | None = None,
        italic: bool | None = None,
        underline: bool | None = None,
        strikethrough: bool | None = None,
        superscript: bool | None = None,
        subscript: bool | None = None,
    ) -> ToolResult:
        ...
```

---

### 4.5 子任务 1.6 — `element_delete.py` (T19)

```python
# pptagent/tools/manipulation/element_delete.py

class DeleteElementTool(BaseTool):
    """T19: Remove an element from a slide."""
    name = "delete_element"
    description = (
        "Delete a specific element from a slide. "
        "The operation can be undone."
    )

    schema = {
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index.",
            },
            "element_id": {
                "type": "string",
                "description": "Unique ID of the element to delete.",
            },
        },
        "required": ["slide_index", "element_id"],
    }

    async def execute(  # type: ignore[override]
        self, slide_index: int, element_id: str,
    ) -> ToolResult:
        ...
```

**核心实现**：

```python
import copy

el = doc.get_element(slide_index, element_id)
slide = doc.get_slide(slide_index)

before = {
    "element": copy.deepcopy(el),
    "element_id": element_id,
}

# 实际删除
del slide.elements[element_id]

after = {"deleted": True}

doc.record_change(ChangeRecord(
    operation="delete_element",
    target_element=element_id,
    slide_index=slide_index,
    before_state=before,
    after_state=after,
))
```

---

## 5. 任务二：要素插入工具 (T21, T25, T26, T30)

> **目录**：`pptagent/tools/insertion/`
> **依赖**：PPTDocument / Element / TextFormat / Slide.elements（全部已完成）

### 5.1 子任务 2.1 — `image_inserter.py` (T21)

```python
# pptagent/tools/insertion/image_inserter.py

class InsertImageTool(BaseTool):
    """T21: Insert an image from a file path into a slide."""
    name = "insert_image"
    description = (
        "Insert an image file into a slide at the specified position. "
        "Supports PNG, JPEG, GIF, and BMP formats."
    )

    schema = {
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index.",
            },
            "image_path": {
                "type": "string",
                "description": "Absolute or relative path to the image file.",
            },
            "left": {
                "type": "number",
                "description": "Distance from left edge in EMU.",
            },
            "top": {
                "type": "number",
                "description": "Distance from top edge in EMU.",
            },
            "width": {
                "type": "number",
                "description": "Width in EMU. If omitted, uses the original image width.",
            },
            "height": {
                "type": "number",
                "description": "Height in EMU. If omitted, uses the original image height.",
            },
            "alt_text": {
                "type": "string",
                "description": "Accessibility description for the image (default '').",
            },
        },
        "required": ["slide_index", "image_path", "left", "top"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        image_path: str,
        left: float,
        top: float,
        width: float | None = None,
        height: float | None = None,
        alt_text: str = "",
    ) -> ToolResult:
        ...
```

**核心实现**：

```python
import uuid
from pathlib import Path

path = Path(image_path).expanduser().resolve()
if not path.exists():
    return ToolResult(success=False, error=f"Image file not found: {image_path}")

blob = path.read_bytes()
content_type = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".gif": "image/gif", ".bmp": "image/bmp"}.get(path.suffix.lower(), "image/png")

# 未指定尺寸时，读取原始尺寸并转换 EMU
if width is None or height is None:
    from PIL import Image
    with Image.open(path) as img:
        ow, oh = img.size  # pixels
    dpi = 96  # 标准屏幕 DPI
    if width is None:
        width = int(ow / dpi * 914400)
    if height is None:
        height = int(oh / dpi * 914400)

element_id = f"image_{uuid.uuid4().hex[:8]}"
el = Element(
    id=element_id,
    type="image",
    position=(left, top, width, height),
    content={"blob": blob, "content_type": content_type, "filename": path.name},
    metadata={"alt_text": alt_text, "source_path": str(path)},
)

slide = doc.get_slide(slide_index)
slide.elements[element_id] = el

doc.record_change(ChangeRecord(
    operation="insert_image",
    target_element=element_id,
    slide_index=slide_index,
    before_state={"element_id": None},
    after_state={"element_id": element_id},
))

return ToolResult(success=True, data={"element_id": element_id, "message": f"Inserted {path.name}"})
```

---

### 5.2 子任务 2.2 — `text_inserter.py` (T25)

```python
# pptagent/tools/insertion/text_inserter.py

class InsertTextBoxTool(BaseTool):
    """T25: Insert a text box into a slide."""
    name = "insert_text_box"
    description = "Insert a new text box with specified content and formatting."

    schema = {
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index.",
            },
            "text": {
                "type": "string",
                "description": "Text content to insert.",
            },
            "left": {"type": "number", "description": "Left position in EMU."},
            "top": {"type": "number", "description": "Top position in EMU."},
            "width": {"type": "number", "description": "Width in EMU."},
            "height": {"type": "number", "description": "Height in EMU."},
            "font_name": {
                "type": "string",
                "description": "Font family (default 'Calibri').",
            },
            "font_size": {
                "type": "number",
                "description": "Font size in pt (default 12).",
            },
            "font_color": {
                "type": "string",
                "description": "Font colour HEX (default '#000000').",
            },
            "bold": {"type": "boolean", "description": "Bold (default false)."},
            "italic": {"type": "boolean", "description": "Italic (default false)."},
            "alignment": {
                "type": "string",
                "enum": ["left", "center", "right", "justify"],
                "description": "Text alignment (default 'left').",
            },
        },
        "required": ["slide_index", "text", "left", "top", "width", "height"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        text: str,
        left: float,
        top: float,
        width: float,
        height: float,
        font_name: str = "Calibri",
        font_size: float = 12.0,
        font_color: str = "#000000",
        bold: bool = False,
        italic: bool = False,
        alignment: str = "left",
    ) -> ToolResult:
        ...
```

---

### 5.3 子任务 2.3 — `table_inserter.py` (T26)

```python
# pptagent/tools/insertion/table_inserter.py

class InsertTableTool(BaseTool):
    """T26: Insert a table into a slide."""
    name = "insert_table"
    description = (
        "Insert a table with the specified number of rows and columns. "
        "Optionally provide pre-filled cell data as a 2D array of strings."
    )

    schema = {
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index.",
            },
            "rows": {
                "type": "integer",
                "description": "Number of rows.",
            },
            "cols": {
                "type": "integer",
                "description": "Number of columns.",
            },
            "left": {"type": "number", "description": "Left position in EMU."},
            "top": {"type": "number", "description": "Top position in EMU."},
            "width": {"type": "number", "description": "Width in EMU."},
            "height": {"type": "number", "description": "Height in EMU."},
            "data": {
                "type": "array",
                "items": {"type": "array", "items": {"type": "string"}},
                "description": "Optional 2D array of cell text. Empty cells used if omitted.",
            },
        },
        "required": ["slide_index", "rows", "cols", "left", "top", "width", "height"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        rows: int,
        cols: int,
        left: float,
        top: float,
        width: float,
        height: float,
        data: list[list[str]] | None = None,
    ) -> ToolResult:
        ...
```

**核心实现**：

```python
# 构建表格内容矩阵
if data is None:
    content = [["" for _ in range(cols)] for _ in range(rows)]
else:
    content = data
    # 补齐不足的行/列
    while len(content) < rows:
        content.append(["" for _ in range(cols)])
    for row in content:
        while len(row) < cols:
            row.append("")

element_id = f"table_{uuid.uuid4().hex[:8]}"
el = Element(
    id=element_id,
    type="table",
    position=(left, top, width, height),
    content=content,
)
```

---

### 5.4 子任务 2.4 — `chart_inserter.py` (T30)

```python
# pptagent/tools/insertion/chart_inserter.py

class InsertChartTool(BaseTool):
    """T30: Insert a chart into a slide."""
    name = "insert_chart"
    description = (
        "Insert a chart (bar, line, pie, or scatter) with category labels and series data."
    )

    schema = {
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index.",
            },
            "chart_type": {
                "type": "string",
                "enum": ["bar", "line", "pie", "scatter"],
                "description": "Type of chart to insert.",
            },
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Category labels (e.g., ['Q1', 'Q2', 'Q3', 'Q4']).",
            },
            "series_data": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Series name."},
                        "values": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Data values for this series.",
                        },
                    },
                },
                "description": "List of data series.",
            },
            "left": {"type": "number", "description": "Left position in EMU."},
            "top": {"type": "number", "description": "Top position in EMU."},
            "width": {"type": "number", "description": "Width in EMU."},
            "height": {"type": "number", "description": "Height in EMU."},
            "title": {
                "type": "string",
                "description": "Optional chart title.",
            },
        },
        "required": ["slide_index", "chart_type", "categories", "series_data",
                     "left", "top", "width", "height"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        chart_type: str,
        categories: list[str],
        series_data: list[dict],
        left: float,
        top: float,
        width: float,
        height: float,
        title: str | None = None,
    ) -> ToolResult:
        ...
```

**核心实现**：

```python
element_id = f"chart_{uuid.uuid4().hex[:8]}"
el = Element(
    id=element_id,
    type="chart",
    position=(left, top, width, height),
    content={
        "chart_type": chart_type,
        "categories": categories,
        "series": series_data,
        "title": title,
    },
)

slide = doc.get_slide(slide_index)
slide.elements[element_id] = el
```

---

## 6. 任务三：to_file() 扩展

> **文件**：`pptagent/core/document.py`（修改）
> **依赖**：Phase 3 插入工具（table / chart 类型的 Element 出现在文档中）

### 6.1 子任务 3.1 — `_write_table_element()`

```python
def _write_table_element(
    slide: Any,          # python-pptx Slide
    element: Element,
    left: float,
    top: float,
    width: float,
    height: float,
) -> None:
    """Add a table shape for *element* to *slide*."""
    rows_data = element.content
    if not isinstance(rows_data, list) or not rows_data:
        return

    rows = len(rows_data)
    cols = max((len(r) for r in rows_data), default=0)
    if cols == 0:
        return

    table_shape = slide.shapes.add_table(
        rows, cols, int(left), int(top), int(width), int(height)
    )
    tbl = table_shape.table
    for r in range(rows):
        for c in range(min(len(rows_data[r]), cols)):
            tbl.cell(r, c).text = str(rows_data[r][c])
```

### 6.2 子任务 3.2 — `_write_chart_element()`

```python
def _write_chart_element(
    slide: Any,          # python-pptx Slide
    element: Element,
    left: float,
    top: float,
    width: float,
    height: float,
) -> None:
    """Add a chart shape for *element* to *slide*."""
    if not isinstance(element.content, dict):
        return

    chart_data = element.content
    chart_type_str = chart_data.get("chart_type", "bar")
    categories = chart_data.get("categories", [])
    series_list = chart_data.get("series", [])
    chart_title = chart_data.get("title")

    from pptx.enum.chart import XL_CHART_TYPE

    _CHART_TYPE_MAP = {
        "bar": XL_CHART_TYPE.COLUMN_CLUSTERED,
        "line": XL_CHART_TYPE.LINE,
        "pie": XL_CHART_TYPE.PIE,
        "scatter": XL_CHART_TYPE.XY_SCATTER,
    }
    chart_type = _CHART_TYPE_MAP.get(chart_type_str, XL_CHART_TYPE.COLUMN_CLUSTERED)

    chart_frame = slide.shapes.add_chart(
        chart_type, int(left), int(top), int(width), int(height),
    )
    chart = chart_frame.chart

    # Populate chart data
    from pptx.chart.data import CategoryChartData
    cd = CategoryChartData()
    cd.categories = categories
    for s in series_list:
        cd.add_series(s.get("name", ""), s.get("values", []))

    chart.replace_data(cd)

    # Title
    if chart_title and chart.has_title:
        chart.chart_title.text_frame.paragraphs[0].text = chart_title
```

### 6.3 修改 `to_file()` 主循环

在 `to_file()` 的元素写出循环中新增：

```python
for element in slide_data.elements.values():
    left, top, width, height = element.position

    if element.type == "text":
        _write_text_element(pptx_slide, element, left, top, width, height)
    elif element.type == "image":
        _write_image_element(pptx_slide, element, left, top, width, height)
    elif element.type == "table":   # ← 新增
        _write_table_element(pptx_slide, element, left, top, width, height)
    elif element.type == "chart":   # ← 新增
        _write_chart_element(pptx_slide, element, left, top, width, height)
```

---

## 7. 任务四：单元测试完善

> **目标**：`pptagent/tools/manipulation/`、`pptagent/tools/insertion/` 行覆盖率 ≥85%

### 7.1 新建测试文件

| 测试文件 | 测试对象 | 关键测试用例 |
|---------|---------|-------------|
| `tests/unit/tools/manipulation/test_element_geometry.py` | T14, T15 | 设置位置、修改尺寸、部分更新、非文本要素、invalid slide index、undo 验证 |
| `tests/unit/tools/manipulation/test_text_formatter.py` | T16, T17, T18 | 单个字段修改、多字段批量修改、仅对齐/效果、非文本要素拒绝、before/after 一致性 |
| `tests/unit/tools/manipulation/test_element_delete.py` | T19 | 删除成功、undo 恢复、不存在的 element_id、已经空的 slide |
| `tests/unit/tools/insertion/test_image_inserter.py` | T21 | 有效图片插入、不存在的图片路径、自动尺寸计算、base64 数据验证 |
| `tests/unit/tools/insertion/test_text_inserter.py` | T25 | 默认格式插入、自定义格式插入、空文本插入 |
| `tests/unit/tools/insertion/test_table_inserter.py` | T26 | 空表格、预填数据表格、行列补齐逻辑 |
| `tests/unit/tools/insertion/test_chart_inserter.py` | T30 | 四种图表类型插入、标题设置、数据验证 |
| `tests/unit/core/test_document_roundtrip.py` | to_file() 扩展 | 编辑后 roundtrip: 打开→编辑→写出→重读→验证编辑效果 |

### 7.2 测试辅助 Fixture

```python
# tests/conftest.py 中新增

@pytest.fixture
def doc_with_text() -> PPTDocument:
    """A document with one slide and a known text element (including TextFormat)."""
    doc = PPTDocument(file_name="test.pptx")
    fmt = TextFormat(font_name="Calibri", font_size=12, font_color="#000000")
    slide0 = Slide(index=0)
    slide0.elements["text_001"] = Element(
        id="text_001", type="text",
        position=(100000, 100000, 500000, 300000),
        content="Hello World", format=fmt,
    )
    doc.slides = [slide0]
    return doc
```

---

## 8. 执行顺序与依赖图

```
Day 1–3  │  Task 1: 要素编辑工具
         │  └── text_formatter.py (T16 最复杂，需优先)
         │  └── element_geometry.py (T14/T15)
         │  └── element_delete.py (T19)
         │  注意: T17/T18 与 T16 同文件，在 T16 完成后实现
         │
Day 4–6  │  Task 2: 要素插入工具
         │  └── image_inserter.py (T21)
         │  └── text_inserter.py (T25)
         │  └── table_inserter.py (T26)
         │  └── chart_inserter.py (T30)
         │
Day 7    │  Task 3: to_file() 扩展
         │  └── _write_table_element()
         │  └── _write_chart_element()
         │
Day 8–10 │  Task 4: 单元测试
         │  └── 7 个工具测试文件 + 1 个集成 roundtrip 测试
```

```
Dependency graph (Phase 3 内部):

  Phase 2 Deliverables (已完成)
  ├── PPTDocument / Element / TextFormat / Slide
  ├── ChangeManager + ChangeRecord
  ├── SessionState + get_session()
  ├── from_file() + to_file()
  └── ToolResult + BaseTool + ToolRegistry
            │
            ├──────────────────────────────────────────────┐
            ▼                                              ▼
  Task 1: 编辑工具 (T14–T19)                    Task 2: 插入工具 (T21–T30)
  └── 依赖: get_element(), Element, ChangeRecord  └── 依赖: Slide.elements, Element(), from_file()
            │                                              │
            └──────────────────┬───────────────────────────┘
                               ▼
                    Task 3: to_file() 扩展
                    └── 依赖: Task 2 产生的 table/chart Element
                               │
                               ▼
                    Task 4: 单元测试
                    └── 依赖: Task 1 + Task 2 + Task 3
```

**Phase 3 对前序阶段的依赖**：

```
Phase 2 提供                          Phase 3 使用方式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PPTDocument.get_element()         →  所有编辑工具定位目标 Element
PPTDocument.get_slide()           →  获取 Slide 对象
Element.position (EMU tuple)      →  T14/T15 直接读写
Element.format (TextFormat)       →  T16/T17/T18 直接读写
Element.content (Any)             →  T21/T25/T26/T30 填充 content
Slide.elements (dict)             →  T19 pop / T21–T30 insert
ChangeManager + ChangeRecord      →  所有编辑操作的 undo 记录
to_file() + _write_*_element()    →  编辑后持久化
TextFormat (14 字段)              →  T16/T25 参数规格
SessionState                      →  获取 current_document
```

**关键洞察**：Phase 3 不需要任何新的底层引擎。所有操作都是对 PPTDocument 内存模型的纯数据操作 + to_file() 持久化。Phase 2 作为"基石"的价值在此体现——它让 Phase 3 变成了 CRUD over dataclasses。

---

## 9. 文件清单

### 新建文件（共 7 个源文件 + 8 个测试文件）

```
pptagent/tools/manipulation/
├── __init__.py                    ← UPDATE: 添加导出
├── element_geometry.py            ← NEW  Task 1: T14 + T15
├── text_formatter.py              ← NEW  Task 1: T16 + T17 + T18
└── element_delete.py              ← NEW  Task 1: T19

pptagent/tools/insertion/
├── __init__.py                    ← UPDATE: 添加导出
├── image_inserter.py              ← NEW  Task 2: T21
├── text_inserter.py               ← NEW  Task 2: T25
├── table_inserter.py              ← NEW  Task 2: T26
└── chart_inserter.py              ← NEW  Task 2: T30

tests/unit/tools/manipulation/
├── __init__.py                    ← NEW: empty
├── test_element_geometry.py       ← NEW  Task 4
├── test_text_formatter.py         ← NEW  Task 4
└── test_element_delete.py         ← NEW  Task 4

tests/unit/tools/insertion/
├── __init__.py                    ← NEW: empty
├── test_image_inserter.py         ← NEW  Task 4
├── test_text_inserter.py          ← NEW  Task 4
├── test_table_inserter.py         ← NEW  Task 4
└── test_chart_inserter.py         ← NEW  Task 4

tests/unit/core/
└── test_document_roundtrip.py     ← NEW  Task 4: 编辑后 roundtrip 集成测试
```

### 修改文件（共 3 个）

```
pptagent/core/document.py          ← UPDATE: to_file() 新增 table/chart 写出
pptagent/tools/manipulation/__init__.py  ← UPDATE: 添加 4 个工具类导出
pptagent/tools/insertion/__init__.py     ← UPDATE: 添加 4 个工具类导出
tests/conftest.py                  ← UPDATE: 新增 doc_with_text fixture
```

---

## 10. 验收标准

### 10.1 功能验收

- [ ] T14 `set_position`: 能修改任意要素的 left/top，非文本要素也可操作
- [ ] T15 `set_size`: 能修改任意要素的 width/height，支持 lock_aspect_ratio
- [ ] T16 `format_text`: 支持 14 个字段的任意子集部分更新，非文本要素返回错误
- [ ] T17 `set_alignment`: 能设置 left/center/right/justify
- [ ] T18 `set_text_effect`: 能单独或组合设置 bold/italic/underline/strikethrough/super/sub script
- [ ] T19 `delete_element`: 能删除要素，且 undo 可恢复完整 Element
- [ ] T21 `insert_image`: 能插入有效图片文件，自动获取尺寸，返回 element_id
- [ ] T25 `insert_text_box`: 能插入文本框，含默认/自定义格式
- [ ] T26 `insert_table`: 能插入空表格或预填数据表格
- [ ] T30 `insert_chart`: 能插入 bar/line/pie/scatter 四种图表
- [ ] 所有编辑操作记录 ChangeRecord，支持 undo
- [ ] 编辑后 to_file() roundtrip: 打开→编辑→写出→重读→验证编辑效果
- [ ] to_file() 能正确写出 table 和 chart 类型 Element

### 10.2 代码质量

- [ ] 所有新代码通过 `ruff check`、`black --check`、`isort --check-only`
- [ ] `mypy pptagent/tools/manipulation/ pptagent/tools/insertion/` 零错误
- [ ] 所有 docstring 遵循 Google 风格格式
- [ ] `pptagent/tools/manipulation/` 行覆盖率 ≥85%
- [ ] `pptagent/tools/insertion/` 行覆盖率 ≥85%
- [ ] `pptagent/core/document.py` `to_file()` 相关路径覆盖率 ≥85%

### 10.3 可运行验证

```bash
conda activate pptagent
pytest tests/unit/tools/manipulation/ -v
pytest tests/unit/tools/insertion/ -v
pytest tests/unit/core/test_document_roundtrip.py -v

# End-to-end edit + roundtrip
python -c "
from pptagent.core.document import PPTDocument
from pptagent.tools.manipulation.element_geometry import SetPositionTool
from pptagent.tools.manipulation.text_formatter import FormatTextTool
from pptagent.tools.insertion.text_inserter import InsertTextBoxTool
from pptagent.core.session import get_session
import tempfile, os

# 1. Open
doc = PPTDocument.from_file('tests/fixtures/sample_simple.pptx')
sess = get_session()
sess.current_document = doc

# 2. Insert text box
tool = InsertTextBoxTool()
result = await tool.execute(slide_index=1, text='Inserted by Phase 3!',
                             left=914400, top=914400, width=4572000, height=914400,
                             font_name='Arial', font_size=18, bold=True)
print(f'Insert: {result.data[\"element_id\"]}')

# 3. Edit format
fmt_tool = FormatTextTool()
result2 = await fmt_tool.execute(slide_index=0, element_id='text_001',
                                  font_size=24, bold=True, font_color='#FF0000')
print(f'Format: {result2.success}')

# 4. Save + reload
with tempfile.NamedTemporaryFile(suffix='.pptx') as f:
    doc.to_file(f.name)
    doc2 = PPTDocument.from_file(f.name)
    print(f'Roundtrip OK: {len(doc2.slides)} slides')
"
```

### 10.4 建议的 Git 提交顺序

```
feat(tools): implement T14 set_position + T15 set_size tools
feat(tools): implement T16 format_text tool (14-parameter partial update)
feat(tools): implement T17 set_alignment + T18 set_text_effect tools
feat(tools): implement T19 delete_element with undo support
feat(tools): implement T21 insert_image tool
feat(tools): implement T25 insert_text_box tool
feat(tools): implement T26 insert_table + T30 insert_chart tools
feat(core): extend to_file() to write table and chart elements
test: add unit tests for manipulation tools (T14-T19)
test: add unit tests for insertion tools (T21,T25,T26,T30)
test: add edit-to-file roundtrip integration tests
```

---

> **下一步**：Phase 3 验收通过后，进入 [Phase 4：高级内容创建](../docs/0_plan.md#phase-4-高级内容创建2-3周)——LaTeX 公式渲染、Mermaid/Graphviz 流程图、视频/音频/动图插入。

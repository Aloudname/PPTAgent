# PPTAgent

An intelligent PPT creation agent for researchers. It understands user intent through natural language interaction and orchestrates tools to read, analyze, edit, generate, beautify, and save PowerPoint presentations.

## Quick Links

- [Project Plan & Architecture](0_plan.md) — overall technical architecture and 8-phase roadmap
- [Phase 0: Infrastructure Setup](1_infra.md) — conda environment, CI/CD, logging, configuration
- [Phase 1: Basic Operations](2_basicOperations.md) — data models, file tools, slide operations
- [Phase 3: Element Editing](3_elementEditing.md) — position, size, formatting, and content editing
- [Phase Summary & Next Steps](12_summary.md) — current state and future direction

## Key Features

- **8 tool categories** — 45 tools covering file I/O, extraction, editing, insertion, layout, slide management, search, and utilities
- **Undo/redo** — every mutation recorded by ChangeManager
- **Layer-override config** — YAML + environment variables, validated by Pydantic
- **Structured logging** — JSON logs with automatic session/task context injection
- **LibreOffice integration** — automatic legacy .ppt → .pptx conversion

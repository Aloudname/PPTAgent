#!/bin/bash
# scripts/create_skeleton.sh
# Create project skeleton script for the project.
# Run by bash scripts/create_skeleton.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "[DEBUG] Project root dir: $PROJECT_ROOT"

create_dirs() {
    local dirs=(
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
        config/prompts
        scripts
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
        data/templates
        data/vector_db
        data/samples
        docs/api
        docs/guides
        docs/decisions
        .github/workflows
        .github/ISSUE_TEMPLATE
        .vscode
    )

    for dir in "${dirs[@]}"; do
        mkdir -p "$PROJECT_ROOT/$dir"
        echo "[DEBUG] Created directory: $dir"
    done
}

echo ""
echo "[CHORES] Creating directory structure..."
create_dirs

echo ""
echo "[CHORES] Project skeleton creation completed!"

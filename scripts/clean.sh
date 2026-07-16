#!/bin/bash
# scripts/clean.sh
# Cache removal script for the project.

set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "[CHORES] Cleaning up caches..."

# Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Test
rm -rf .pytest_cache .coverage htmlcov coverage.xml 2>/dev/null || true

# Lint
rm -rf .mypy_cache .ruff_cache 2>/dev/null || true

# Logs
rm -rf logs/*.log 2>/dev/null || true

# LibreOffice lock files
find . -name ".~lock.*" -delete 2>/dev/null || true

echo "[CHORES] Cache cleanup completed."

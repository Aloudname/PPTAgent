#!/bin/bash
# scripts/run_lint.sh
# run sanity checks for the project.
# run by bash scripts/run_lint.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

PASS=0
FAIL=0

run_check() {
    local name="$1"
    local cmd="$2"
    echo -n " $name ... "
    if eval "$cmd" 2>&1; then
        echo "[PASS]"
        PASS=$((PASS + 1))
    else
        echo "[FAIL]"
        FAIL=$((FAIL + 1))
    fi
    echo ""
}


echo "[CHORES] Running sanity checks for the project..."
echo ""

run_check "Ruff (lint)"          "ruff check pptagent/ tests/"
run_check "Ruff (format check)"  "ruff format --check pptagent/ tests/"
run_check "Black (format check)" "black --check pptagent/ tests/"
run_check "isort (import check)" "isort --check-only pptagent/ tests/"
run_check "mypy (type check)"    "mypy pptagent/"

echo "[CHORES] Sanity checks completed!"
echo " Results: $PASS passed, $FAIL failed"
echo "[CHORES] Sanity checks completed!"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi

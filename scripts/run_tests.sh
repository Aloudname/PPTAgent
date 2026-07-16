#!/bin/bash
# scripts/run_tests.sh

set -euo pipefail
cd "$(dirname "$0")/.."

echo "[CHORES] Running PyTest..."

COVERAGE="--cov=pptagent"
MARKERS=""
VERBOSE="-v"

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cov)    COVERAGE=""; shift ;;
        --integration) MARKERS="-m integration"; shift ;;
        --slow)       MARKERS="-m 'slow or integration'"; shift ;;
        -x)           VERBOSE="-x"; shift ;;
        *)            break ;;
    esac
done

pytest $VERBOSE $COVERAGE $MARKERS \
    --cov-report=term-missing \
    --cov-report=html:docs/coverage \
    --cov-report=xml:coverage.xml \
    tests/ "$@"

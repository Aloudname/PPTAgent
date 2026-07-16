#!/bin/bash
# scripts/env.sh
# run by source scripts/env.sh

# PPTAgent env vars

# Python path
# export PPTAGENT_PYTHON="${PPTAGENT_PYTHON:-python3.11}"

# LibreOffice path
# export LIBREOFFICE_PATH="${LIBREOFFICE_PATH:-/usr/bin/libreoffice}"

# Mermaid CLI path
export MERMAID_CLI_PATH="${MERMAID_CLI_PATH:-$(which mmdc 2>/dev/null || echo '')}"

# OCR
export OCR_LANGUAGES="${OCR_LANGUAGES:-en,ch}"

# dev
export PPTAGENT_ENV="${PPTAGENT_ENV:-development}"

# log level
export PPTAGENT_LOG_LEVEL="${PPTAGENT_LOG_LEVEL:-DEBUG}"

# Conda env name
export PPTAGENT_ENV_NAME="${PPTAGENT_ENV_NAME:-pptagent}"

echo "[CHORES] PPTAgent environment variables loaded."

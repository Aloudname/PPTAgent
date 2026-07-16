#!/bin/bash
# scripts/install_system_deps.sh
# Install system dependencies script for the project.
# Run by bash scripts/install_system_deps.sh

set -euo pipefail

echo "[CHORES] PPTAgent system dependencies installing..."
echo "[NOTE] Only for Ubuntu 22.04+ / Debian 12+"

sudo apt-get update -qq

echo "[1/3] Installing Mermaid CLI dependencies..."
if ! command -v node &> /dev/null; then
    echo "[1/3] Installing Node.js..."
    sudo apt-get install -y -qq nodejs npm
else
    echo "[1/3] Node.js installed with $(node --version)"
fi

echo "[2/3] Installing Mermaid CLI..."
if ! command -v mmdc &> /dev/null; then
    sudo npm install -g @mermaid-js/mermaid-cli
    echo "[2/3] Mermaid CLI installed: $(mmdc --version)"
else
    echo "[2/3] Mermaid CLI already installed`: $(mmdc --version)"
fi

echo "[3/3] Checking core conda management tools..."
for cmd in dot ffmpeg libreoffice; do
    if command -v $cmd &> /dev/null; then
        echo "[3/3] $cmd: $(command -v $cmd)"
    else
        echo "[3/3] $cmd not found. If using conda, please run: conda env create -f environment.yml"
    fi
done

echo ""
echo "[CHORES] System dependencies check completed!"

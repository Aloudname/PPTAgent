#!/bin/bash
# scripts/setup_conda_env.sh
# Create and setup conda environment for the project.
# Run by bash scripts/setup_conda_env.sh
# equals to conda env create -f environment.yml && pip install -e . --no-deps

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_NAME="${PPTAGENT_ENV_NAME:-pptagent}"
PYTHON_VERSION="3.11"

echo "[CHORES] Setting up environment with conda..."
echo ""
echo "[DEBUG] Project Root:   $PROJECT_ROOT"
echo "[DEBUG] Environment Name:     $ENV_NAME"
echo "[DEBUG] Python Version:  $PYTHON_VERSION"
echo ""

if ! command -v conda &> /dev/null; then
    echo "[ERROR] Could not find conda."
    exit 1
fi

# Check if the environment already exists
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "[WARN] Environment '${ENV_NAME}' already exists."
    echo ""
    echo "Options:"
    echo "  1) Delete and recreate (Recommended)"
    echo "  2) Only update dependencies"
    echo "  3) Cancel"
    echo ""
    read -r -p "Select [1-3]: " choice
    case $choice in
        1)
            echo "[CHORES] Deleting existing environment..."
            conda env remove -n "$ENV_NAME" -y
            ;;
        2)
            echo "[CHORES] Updating existing environment..."
            conda env update -n "$ENV_NAME" -f "$PROJECT_ROOT/environment.yml" --prune
            echo "[DEBUG] Environment update completed!"
            exit 0
            ;;
        *)
            echo "[DEBUG] Exiting."
            exit 0
            ;;
    esac
fi

# ---------- 从 environment.yml 创建环境 ----------
echo ""
echo "[1/3] 从 environment.yml 创建 conda 环境..."
echo "      这可能需要 5-15 分钟（首次下载依赖包）..."
conda env create -n "$ENV_NAME" -f "$PROJECT_ROOT/environment.yml"

echo ""
echo "[2/3] 激活环境..."
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

echo ""
echo "[3/3] 以可编辑模式安装 pptagent..."
pip install -e "$PROJECT_ROOT" --no-deps

# ---------- 验证安装 ----------
echo ""
echo "=========================================="
echo " 验证安装"
echo "=========================================="
echo ""

echo "🐍 Python 环境:"
python --version
which python
echo ""

echo "📦 核心依赖验证:"
python -c "import pptagent; print(f'  ✅ pptagent {pptagent.__version__}')"
python -c "import pptx; print(f'  ✅ python-pptx 可用')"
python -c "import PIL; print(f'  ✅ Pillow {PIL.__version__}')"
python -c "import cv2; print(f'  ✅ OpenCV {cv2.__version__}')"
python -c "import numpy; print(f'  ✅ NumPy {numpy.__version__}')"
python -c "import yaml; print(f'  ✅ PyYAML 可用')"
python -c "import pydantic; print(f'  ✅ Pydantic {pydantic.__version__}')"
echo ""

echo "=========================================="
echo " ✅ Conda 环境设置完成！"
echo "=========================================="
echo ""
echo "激活环境:"
echo "  conda activate $ENV_NAME"
echo ""
echo "验证完整环境:"
echo "  python -c 'import pptagent; print(pptagent.__version__)'"
echo ""
echo "导出环境快照:"
echo "  conda env export -n $ENV_NAME > environment-lock.yml"

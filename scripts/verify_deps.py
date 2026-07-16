#!/usr/bin/env python3
"""Verify all core dependencies.
"""

import sys
from importlib import import_module

# (module import name, display name, required)
DEPENDENCIES = [
    # PPT core
    ("pptx", "python-pptx", True),
    ("lxml", "lxml", True),
    ("PIL", "Pillow", True),
    ("olefile", "olefile", True),
    # Numerical computing
    ("numpy", "numpy", True),
    ("scipy", "scipy", False),
    # Image processing
    ("cv2", "opencv-python", True),
    ("imageio", "imageio", False),
    # Data validation
    ("pydantic", "pydantic", True),
    ("yaml", "pyyaml", True),
    # Agent
    ("langchain", "langchain", False),
    ("langchain_anthropic", "langchain-anthropic", False),
    # RAG
    ("chromadb", "chromadb", False),
    ("tiktoken", "tiktoken", False),
    # Charts
    ("matplotlib", "matplotlib", False),
    ("plotly", "plotly", False),
    # Web/API
    ("fastapi", "fastapi", False),
    ("uvicorn", "uvicorn", False),
    # UI
    ("gradio", "gradio", False),
    # Utilities
    ("rich", "rich", True),
    ("xxhash", "xxhash", True),
    ("httpx", "httpx", True),
]


def main() -> None:
    success = 0
    warning = 0
    failure = 0

    print("Running PPTAgent Smoke Test.\n")

    for import_name, display_name, required in DEPENDENCIES:
        try:
            mod = import_module(import_name)
            version = getattr(mod, "__version__", "?")
            print(f"  ✅ {display_name:30s} {version}")
            success += 1
        except ImportError as e:
            if required:
                print(f"  ❌ {display_name:30s} missing (required): {e}")
                failure += 1
            else:
                print(f"  ⚠️  {display_name:30s} missing (optional): {e}")
                warning += 1

    print(f" Result: {success} passed, {warning} optional missing, {failure} required missing")

    if failure > 0:
        print("\n❌ Please install missing required dependencies: conda env update -f environment.yml")
        sys.exit(1)
    else:
        print("\n✅ All required dependencies are ready!")
        sys.exit(0)


if __name__ == "__main__":
    main()

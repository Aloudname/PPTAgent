#!/usr/bin/env python3
"""core pipeline smoke test."""

import sys
from pathlib import Path

# Ensure project is in path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports() -> None:
    """Test that all core modules are importable"""
    from pptagent import __version__
    assert __version__ == "0.1.0", f"Unexpected version: {__version__}"
    from pptagent.core.exceptions import PPTAgentError
    assert issubclass(PPTAgentError, Exception)


def test_config_load() -> None:
    """Test configuration loading"""
    from pptagent.utils.config import Config
    config = Config.load(env="development")
    assert config.agent.model is not None
    assert config.agent.temperature >= 0
    assert config.file_system.search_max_depth > 0
    print(f"  ✅ Config loaded: model={config.agent.model}")


def test_logger() -> None:
    """Test logging system"""
    from pptagent.utils.logger import setup_logging
    logger = setup_logging(name="smoke_test", structured=False)
    logger.info("Smoke test log message")
    print("  ✅ Logger works")


def test_tool_registry() -> None:
    """Test tool registry mechanism"""
    from pptagent.tools.base import ToolRegistry

    registry = ToolRegistry()
    assert len(registry) == 0
    assert registry.list_all() == []
    print("  ✅ ToolRegistry works")


def test_document_import() -> bool:
    """Test pptx library availability"""
    try:
        from pptx import Presentation  # noqa: F401
        print("  ✅ python-pptx available")
    except ImportError as e:
        print(f"  ❌ python-pptx not available: {e}")
        return False
    return True


def main() -> None:
    print("Running PPTAgent Smoke Test.\n")

    tests = [
        ("Import check", test_imports),
        ("Config load", test_config_load),
        ("Logger", test_logger),
        ("Tool registry", test_tool_registry),
        ("python-pptx", test_document_import),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f"Searching {name}...")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()

    print(f" Results: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

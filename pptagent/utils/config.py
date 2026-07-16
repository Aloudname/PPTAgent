"""Config management system

Layered override:
`default.yaml -> {env}.yaml -> environment variables (PPTAGENT_*)`
All config is validated through `Pydantic Settings` models.

Usage:
    from pptagent.utils.config import get_config

    config = get_config()
    print(config.agent.model)
"""

import os
from pathlib import Path
from typing import Optional

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Sub-config models
class AgentConfig(BaseModel):
    """Agent-level configs

    These configs control behavior of the agent,
    including model selection, execution params and user interaction settings."""
    model: str = "claude-sonnet-4-6"
    temperature: float = 0.1
    max_tokens: int = 4096
    max_replan_count: int = 3
    max_execution_steps: int = 20
    execution_timeout_seconds: int = 300
    parallel_extraction: bool = True
    auto_confirm_readonly: bool = True
    auto_confirm_single_edit: bool = True
    confirm_batch_threshold: int = 3
    confirm_delete: bool = True
    confirm_save: bool = True
    preview_before_layout: bool = True


class FileSystemConfig(BaseModel):
    """File system configs

    These configs control how agent interacts with the file system,
    including file search, format support, and conversion behavior."""
    search_max_depth: int = 5
    supported_formats: list[str] = [".ppt", ".pptx", ".potx", ".ppsx"]
    auto_convert_legacy: bool = True
    libreoffice_timeout: int = 60
    file_lock_enabled: bool = True
    max_file_size_mb: int = 200


class ExtractionConfig(BaseModel):
    """Extraction configs

    These configs control how agent extracts content from PPT files,
    including OCR, formula rendering, and image & chart extraction."""
    ocr_engine: str = "easyocr"
    ocr_languages: list[str] = ["en", "ch"]
    ocr_confidence_threshold: float = 0.6
    extract_image_dpi: int = 300
    extract_image_format: str = "png"
    formula_engine: str = "latex"
    formula_fallback_to_ocr: bool = True
    chart_extract_data: bool = True
    chart_extract_image: bool = True
    lazy_load_images: bool = True
    max_text_length: int = 100000


class LayoutConfig(BaseModel):
    """Layout configs

    These configs control how agent performs layout and design adjustments,
    including grid settings, spacing, and aesthetic weights."""
    grid_enabled: bool = True
    grid_size_inches: float = 0.25
    snap_to_grid: bool = True
    default_margins: dict = Field(
        default_factory=lambda: {"left": 0.5, "right": 0.5, "top": 0.5, "bottom": 0.5}
    )
    min_element_spacing: float = 0.1
    text_line_spacing: float = 1.15
    aesthetic_weights: dict = Field(
        default_factory=lambda: {
            "alignment": 0.25,
            "whitespace": 0.20,
            "consistency": 0.20,
            "golden_ratio": 0.15,
            "color_harmony": 0.10,
            "visual_hierarchy": 0.10,
        }
    )


class LoggingConfig(BaseModel):
    """Logging configs

    These configs control how agent logs its operations,
    including log level, format, and output destinations."""
    level: str = "INFO"
    format: str = "structured"
    output: list[str] = ["console", "file"]
    file_path: str = "./logs/pptagent.log"
    rotation: str = "10 MB"
    retention: str = "7 days"


class Config(BaseSettings):
    """Agent global config

    Main config class aggregates all sub-configs.
    Supports layered overrides from:
    - `default.yaml`,
    - `{env}.yaml`,
    - `PPTAGENT_*` envs

    env example:
    ```bash
    export PPTAGENT_ENV=production
    export PPTAGENT_AGENT__MODEL=claude-sonnet-4-6
    export PPTAGENT_FILE_SYSTEM__SEARCH_MAX_DEPTH=10
    ```
    """

    model_config = SettingsConfigDict(
        env_prefix="PPTAGENT_",
        env_nested_delimiter="__",
        extra="allow",
    )

    agent: AgentConfig = Field(default_factory=AgentConfig)
    file_system: FileSystemConfig = Field(default_factory=FileSystemConfig)
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    layout: LayoutConfig = Field(default_factory=LayoutConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def load(
        cls,
        env: Optional[str] = None,
        config_dir: Optional[Path] = None,
    ) -> "Config":
        """Load config via:

        `default.yaml -> {env}.yaml -> envs`

        Later source covers earlier one.

        Expected environment variables format:
        `PPTAGENT_{SUBCONFIG}__{FIELD}`
        """

        if env is None:
            env = os.getenv("PPTAGENT_ENV", "development")

        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config"

        # Load YAML
        config_data: dict = {}
        for config_file in ["default.yaml", f"{env}.yaml"]:
            file_path = config_dir / config_file
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if data:
                    config_data = _deep_merge(config_data, data)

        return cls(**config_data)


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge two dicts,
    with override values taking precedence over base values"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# Global singleton
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config singleton"""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config(env: Optional[str] = None) -> Config:
    """Reload config"""
    global _config
    _config = Config.load(env=env)
    return _config

import asyncio
from pathlib import Path
from types import SimpleNamespace

import yaml
from loguru import logger
from pydantic.v1 import BaseSettings

from agentchat.schema.common import MultiModels, ModelConfig, Tools

class Settings(BaseSettings):
    """Minimal runtime configuration required to run the agents and built-in tools."""

    multi_models: MultiModels = MultiModels()
    tools: Tools = Tools()


app_settings = Settings()
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"

async def initialize_app_settings(file_path: str = None):
    global app_settings

    path = Path(file_path) if file_path else DEFAULT_CONFIG_PATH
    try:
        with path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data is None:
                logger.error("YAML 文件解析为空")
                return

            # 特殊处理multi_models配置
            if 'multi_models' in data:
                # 将字典转换为可以用点号访问的对象
                models_config = SimpleNamespace()
                for model_name, model_config in data['multi_models'].items():
                    setattr(models_config, model_name, ModelConfig(**model_config))
                data['multi_models'] = models_config

            if 'tools' in data:
                tools_config = SimpleNamespace()
                for tool_name, tool_config in data['tools'].items():
                    setattr(tools_config, tool_name, tool_config)
                data['tools'] = tools_config

            for key, value in data.items():
                setattr(app_settings, key, value)
    except Exception as e:
        logger.error(f"Yaml file loading error: {e}")


def load_settings(file_path: str = None):
    """Synchronous helper for loading settings."""
    return asyncio.run(initialize_app_settings(file_path))

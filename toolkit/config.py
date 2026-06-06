#!/usr/bin/env python3
"""统一配置加载器"""

import json
import os
import sys
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATHS = [
    "config.yaml",
    "config.yml",
    "config.json",
    os.path.expanduser("~/.wechat-toolkit/config.yaml"),
    os.path.expanduser("~/.wechat-toolkit/config.yml"),
]


def _load_yaml(filepath: str) -> Dict[str, Any]:
    """加载YAML配置文件"""
    try:
        import yaml
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        logger.warning("PyYAML未安装，无法解析YAML配置")
        return {}


def _load_json(filepath: str) -> Dict[str, Any]:
    """加载JSON配置文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_env() -> Dict[str, str]:
    """从.env文件加载环境变量"""
    env_vars = {}
    env_path = ".env"

    if not os.path.exists(env_path):
        return env_vars

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")

    return env_vars


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """深度合并两个字典"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    """统一配置加载器"""

    def __init__(self, config_path: Optional[str] = None):
        self._data: Dict[str, Any] = {}
        self._env: Dict[str, str] = {}

        # 加载环境变量
        self._env = _load_env()
        for key, value in self._env.items():
            if key not in os.environ:
                os.environ[key] = value

        # 确定配置文件路径
        paths = [config_path] if config_path else DEFAULT_CONFIG_PATHS

        for path in paths:
            if path and os.path.exists(path):
                self._load_file(path)
                logger.debug(f"已加载配置: {path}")
                break

    def _load_file(self, filepath: str) -> None:
        """加载配置文件"""
        if filepath.endswith((".yaml", ".yml")):
            data = _load_yaml(filepath)
        elif filepath.endswith(".json"):
            data = _load_json(filepath)
        else:
            # 尝试两种格式
            try:
                data = _load_yaml(filepath)
            except Exception:
                data = _load_json(filepath)

        self._data = _deep_merge(self._data, data)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的路径"""
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split(".")
        data = self._data
        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value

    @property
    def wechat(self) -> Dict[str, Any]:
        """微信配置"""
        return self._data.get("wechat", {})

    @property
    def wechat_appid(self) -> str:
        return (
            self.get("wechat.appid")
            or os.environ.get("WECHAT_APPID", "")
        )

    @property
    def wechat_secret(self) -> str:
        return (
            self.get("wechat.secret")
            or os.environ.get("WECHAT_SECRET", "")
        )

    @property
    def image_provider(self) -> str:
        return self.get("image.provider", "openai")

    @property
    def image_config(self) -> Dict[str, Any]:
        return self.get("image", {})

    @property
    def style(self) -> Dict[str, Any]:
        """写作风格配置"""
        style_path = self.get("style_file", "style.yaml")
        if os.path.exists(style_path):
            if style_path.endswith((".yaml", ".yml")):
                return _load_yaml(style_path)
            elif style_path.endswith(".json"):
                return _load_json(style_path)
        return self._data.get("style", {})

    @property
    def writing(self) -> Dict[str, Any]:
        """写作参数配置"""
        writing_path = self.get("writing_config_file", "writing-config.yaml")
        if os.path.exists(writing_path):
            if writing_path.endswith((".yaml", ".yml")):
                return _load_yaml(writing_path)
            elif writing_path.endswith(".json"):
                return _load_json(writing_path)
        return self._data.get("writing", {})

    def to_dict(self) -> Dict[str, Any]:
        """返回完整配置字典"""
        return self._data.copy()

    def __repr__(self) -> str:
        # 隐藏敏感信息
        safe_data = self._data.copy()
        if "wechat" in safe_data:
            safe_data["wechat"] = {k: "***" if "secret" in k.lower() or "key" in k.lower() else v for k, v in safe_data["wechat"].items()}
        return f"Config({safe_data})"


# 全局配置实例
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None or config_path:
        _config = Config(config_path)
    return _config

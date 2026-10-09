"""集中配置；测试地址由隔离服务生成。"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_settings():
    settings = json.loads((ROOT / "config" / "settings.json").read_text(encoding="utf-8"))
    settings["timeout"] = float(os.getenv("TASK_API_TIMEOUT", settings["timeout"]))
    if settings["timeout"] <= 0:
        raise ValueError("TASK_API_TIMEOUT must be greater than zero")
    return settings

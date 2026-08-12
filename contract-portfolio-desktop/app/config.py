# -*- coding: utf-8 -*-
"""Basit JSON yapılandırma — son yüklenen dosyanın yolunu hatırlar."""
from __future__ import annotations

import json
import os

from paths import config_dir

_CONFIG_FILE = config_dir() / "config.json"


def load() -> dict:
    try:
        with open(_CONFIG_FILE, encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save(data: dict) -> None:
    try:
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # ayar yazılamazsa uygulama yine de çalışsın


def get_last_file() -> str | None:
    path = load().get("last_file")
    if path and os.path.isfile(path):
        return path
    return None


def set_last_file(path: str) -> None:
    data = load()
    data["last_file"] = os.path.abspath(path)
    save(data)

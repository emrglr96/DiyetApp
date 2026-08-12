# -*- coding: utf-8 -*-
"""Kaynak dosya yolları — hem geliştirme hem PyInstaller (donmuş) modunda çalışır."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


def base_dir() -> Path:
    """Uygulama kaynaklarının (assets/, templates/) kök dizini."""
    if getattr(sys, "frozen", False):
        # PyInstaller: onedir -> _MEIPASS, onefile -> geçici çıkarım dizini
        return Path(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)))
    # Geliştirme: bu dosya app/ içinde; kök bir üst dizin.
    return Path(__file__).resolve().parent.parent


def resource_path(*parts: str) -> Path:
    return base_dir().joinpath(*parts)


def assets_dir() -> Path:
    return resource_path("assets")


def templates_dir() -> Path:
    return resource_path("templates")


def file_uri(path: os.PathLike | str) -> str:
    """Verilen dosya için file:// URI (Windows/Unix uyumlu)."""
    return Path(path).resolve().as_uri()


def runtime_dir() -> Path:
    """Üretilen geçici HTML'lerin yazılacağı, yazılabilir dizin."""
    d = Path(tempfile.gettempdir()) / "sozlesme_portfoy_paneli"
    d.mkdir(parents=True, exist_ok=True)
    return d


def config_dir() -> Path:
    """Kullanıcı ayarlarının (son dosya vb.) saklandığı dizin."""
    if sys.platform.startswith("win"):
        root = os.environ.get("APPDATA") or str(Path.home())
    elif sys.platform == "darwin":
        root = str(Path.home() / "Library" / "Application Support")
    else:
        root = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    d = Path(root) / "SozlesmePortfoyPaneli"
    d.mkdir(parents=True, exist_ok=True)
    return d

# -*- coding: utf-8 -*-
"""
Uygulama girişi.

Öncelik pywebview (tek pencere, masaüstü hissi). pywebview yoksa ya da bu
ortamda bir GUI arka ucu başlatılamıyorsa otomatik olarak yerel Flask
sunucusuna düşer ve varsayılan tarayıcıda açar.
"""
from __future__ import annotations

import datetime as _dt
import os
import sys
import time

# app/ dizinini import yoluna ekle (donmuş ve geliştirme modunda çalışır).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config          # noqa: E402
import core            # noqa: E402
import parser as xparser  # noqa: E402
from paths import runtime_dir, file_uri  # noqa: E402
from render import render_dashboard, render_welcome  # noqa: E402

WINDOW_TITLE = "Sözleşme Portföy Paneli"


class Api:
    """pywebview JS köprüsü — önyüzden çağrılan yöntemler."""

    def __init__(self):
        self._window = None

    def bind(self, window):
        self._window = window

    # ---- dosya seçimi ----
    def open_file_dialog(self) -> str:
        import webview
        try:
            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=("Excel Dosyaları (*.xlsx)", "Tüm dosyalar (*.*)"),
            )
        except Exception as e:
            print("Dosya seçici hatası:", e)
            return ""
        if not result:
            return ""
        return result[0] if isinstance(result, (list, tuple)) else str(result)

    # ---- yükleme öncesi kolon denetimi ----
    def prepare(self, path: str) -> dict:
        return core.prepare(path)

    # ---- ayrıştır ve dashboard'u göster ----
    def load(self, path: str, accept_suggestions: bool) -> dict:
        try:
            res = core.load(path, bool(accept_suggestions))
        except xparser.ParseError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": f"Beklenmeyen hata: {e}"}
        today = _dt.date.today()
        html = render_dashboard(
            res.rows, os.path.basename(path), today,
            mode="pywebview", parse_dq=res.dq,
        )
        self._show(html, "dashboard")
        return {"ok": True}

    # ---- dashboard içindeki "Yeni dosya yükle" ----
    def new_file_from_dashboard(self) -> dict:
        html = render_welcome(
            mode="pywebview", last_file=config.get_last_file(), auto_open=True,
        )
        self._show(html, "welcome")
        return {"ok": True}

    def get_last_file(self) -> str:
        return config.get_last_file() or ""

    # ---- iç yardımcı: HTML'i geçici dosyaya yaz ve yükle ----
    def _show(self, html: str, name: str):
        out = runtime_dir() / f"{name}.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        # Önbelleği atlamak için sürüm parametresi ekle.
        self._window.load_url(file_uri(out) + f"?v={int(time.time()*1000)}")


def run_pywebview() -> bool:
    """pywebview ile başlat. Başarısızsa False döner (fallback için)."""
    try:
        import webview
    except ImportError:
        print("pywebview bulunamadı; Flask'a düşülüyor.")
        return False

    api = Api()
    welcome_html = render_welcome(mode="pywebview", last_file=config.get_last_file())
    out = runtime_dir() / "welcome.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(welcome_html)

    window = webview.create_window(
        WINDOW_TITLE,
        url=file_uri(out),
        js_api=api,
        width=1360,
        height=900,
        min_size=(900, 640),
    )
    api.bind(window)

    try:
        webview.start()  # arka ucu otomatik seçer; bloklar
        return True
    except Exception as e:
        print("pywebview başlatılamadı:", e)
        return False


def main():
    force_flask = os.environ.get("SPP_FORCE_FLASK") == "1"
    if not force_flask and run_pywebview():
        return
    # Fallback: Flask + tarayıcı
    import server
    server.run()


if __name__ == "__main__":
    main()

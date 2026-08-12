# -*- coding: utf-8 -*-
"""
Flask geri-dönüş (fallback) sunucusu.

pywebview başlatılamazsa çalışır: yerel bir HTTP sunucusu açar ve varsayılan
tarayıcıda gösterir. Yalnızca 127.0.0.1'e bağlanır (dışa kapalı).
"""
from __future__ import annotations

import datetime as _dt
import html as _html
import os
import socket
import threading
import webbrowser

from flask import Flask, request, redirect, send_from_directory, Response

import config
import core
import parser as xparser
from paths import assets_dir, runtime_dir
from render import render_dashboard, render_welcome

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64 MB üst sınır

_state: dict = {"dashboard_html": None}
_pending: dict = {"path": None}


# --------------------------------------------------------------------------- #
# Varlıklar (offline: Chart.js + fontlar)
# --------------------------------------------------------------------------- #
@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(str(assets_dir()), filename)


# --------------------------------------------------------------------------- #
# Sayfalar
# --------------------------------------------------------------------------- #
@app.route("/")
def index():
    err = request.args.get("e") or None
    return render_welcome(mode="flask", last_file=config.get_last_file(), error=err)


@app.route("/dashboard")
def dashboard():
    if _state["dashboard_html"]:
        return _state["dashboard_html"]
    return redirect("/")


def _process(path: str, accept: bool):
    """Ortak: prepare -> (gerekirse onay) -> load -> dashboard. Redirect döndürür."""
    prep = core.prepare(path)
    if not prep["ok"]:
        return redirect("/?e=" + _q(prep["error"]))
    if prep["needsConfirm"] and not accept:
        _pending["path"] = path
        return redirect("/confirm")
    try:
        res = core.load(path, accept_suggestions=True)
    except xparser.ParseError as e:
        return redirect("/?e=" + _q(str(e)))
    except Exception as e:
        return redirect("/?e=" + _q(f"Beklenmeyen hata: {e}"))
    today = _dt.date.today()
    _state["dashboard_html"] = render_dashboard(
        res.rows, os.path.basename(path), today, mode="flask", parse_dq=res.dq,
    )
    return redirect("/dashboard")


@app.route("/load", methods=["POST"])
def load():
    f = request.files.get("file")
    if not f or not f.filename:
        return redirect("/?e=" + _q("Dosya seçilmedi."))
    # Orijinal dosya adını koru (yol ayıraçlarını temizle, TR karakterleri bırak).
    safe = os.path.basename(f.filename).replace("\\", "_").replace("/", "_") or "yuklenen.xlsx"
    dest = runtime_dir() / safe
    f.save(str(dest))
    return _process(str(dest), accept=False)


@app.route("/reload")
def reload_last():
    path = config.get_last_file()
    if not path:
        return redirect("/?e=" + _q("Son dosya bulunamadı."))
    return _process(path, accept=False)


@app.route("/confirm")
def confirm():
    path = _pending.get("path")
    if not path:
        return redirect("/")
    prep = core.prepare(path)
    sugs = prep.get("suggestions", [])
    rows = "".join(
        f'<div style="padding:7px 0;border-bottom:1px solid #26303C">'
        f'<span style="font-family:monospace;color:#8A98A8">{_html.escape(str(s["found"]) or "(boş)")}</span>'
        f' &rarr; <span style="font-family:monospace">{_html.escape(s["expected"])}</span>'
        f' <span style="color:#5A6876;font-size:11px">(%{round(s["score"]*100)} benzerlik)</span></div>'
        for s in sugs
    )
    return Response(_CONFIRM_PAGE.replace("__ROWS__", rows), mimetype="text/html")


@app.route("/doload")
def doload():
    path = _pending.get("path")
    if not path:
        return redirect("/")
    return _process(path, accept=True)


def _q(text: str) -> str:
    from urllib.parse import quote
    return quote(text)


_CONFIRM_PAGE = """<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8">
<title>Kolon Onayı</title><style>
body{background:#10151C;color:#DEE6EE;font-family:system-ui,Segoe UI,sans-serif;
display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;padding:24px}
.card{background:#182029;border:1px solid #26303C;border-radius:14px;padding:26px 28px;max-width:520px;width:100%}
h1{font-size:17px;margin:0 0 8px}.sub{color:#8A98A8;font-size:13px;margin-bottom:16px}
.btns{display:flex;gap:10px;justify-content:flex-end;margin-top:22px}
a.btn{background:#4FA3D9;color:#0C1319;border-radius:9px;padding:11px 20px;font-weight:600;
text-decoration:none;font-size:14px}a.sec{background:none;border:1px solid #26303C;color:#DEE6EE}
</style></head><body><div class="card">
<h1>Kolon eşleşmesini onaylayın</h1>
<div class="sub">Bazı kolon adları şemayla birebir aynı değil. Aşağıdaki en yakın
eşleşmeleri kullanalım mı?</div>
__ROWS__
<div class="btns"><a class="btn sec" href="/">İptal</a>
<a class="btn" href="/doload">Onayla ve yükle</a></div>
</div></body></html>"""


# --------------------------------------------------------------------------- #
# Çalıştırma
# --------------------------------------------------------------------------- #
def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def run(open_browser: bool = True):
    port = int(os.environ.get("SPP_PORT", 0)) or _free_port()
    url = f"http://127.0.0.1:{port}/"
    print(f"Sözleşme Portföy Paneli (Flask modu): {url}")
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    run()

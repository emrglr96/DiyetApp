# -*- coding: utf-8 -*-
"""
HTML üretimi — şablonlardaki yer tutucuları gerçek veriyle doldurur.

HTML'deki hesaplama/grafik mantığına DOKUNULMAZ; yalnızca:
  __RAW_DATA__     -> satırların JSON'u
  __TODAY_ARGS__   -> bilgisayarın güncel tarihi (JS Date argümanları)
  __FONTS_CSS__ / __CHART_JS__ -> yerel varlık (offline)
  __SUBTITLE__ / __PARSE_DQ__ / __NEW_FILE_HANDLER__ / welcome köprüleri
yer tutucuları doldurulur.
"""
from __future__ import annotations

import datetime as _dt
import json
import html as _html

from paths import templates_dir, assets_dir, file_uri

_TR_MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz",
              "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def _read_template(name: str) -> str:
    with open(templates_dir() / name, encoding="utf-8") as f:
        return f.read()


def _asset_uris(mode: str = "pywebview") -> dict[str, str]:
    if mode == "flask":
        # Flask, /assets/ altından http üzerinden sunar (file:// http sayfada engellenir).
        return {"__FONTS_CSS__": "/assets/fonts.css", "__CHART_JS__": "/assets/chart.min.js"}
    return {
        "__FONTS_CSS__": file_uri(assets_dir() / "fonts.css"),
        "__CHART_JS__": file_uri(assets_dir() / "chart.min.js"),
    }


def _fmt_date_tr(d: _dt.date) -> str:
    return f"{d.day:02d}.{d.month:02d}.{d.year}"


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
def render_dashboard(
    rows: list[dict],
    source_name: str,
    today: _dt.date,
    mode: str = "pywebview",
    parse_dq: list[str] | None = None,
) -> str:
    tpl = _read_template("dashboard_template.html")
    parse_dq = parse_dq or []

    subtitle = (
        f"{len(rows)} sözleşme · Kaynak: {_html.escape(source_name)} · "
        f"Referans tarihi: {_fmt_date_tr(today)}"
    )

    if mode == "flask":
        new_file_handler = "window.location.href='/';"
    else:  # pywebview
        new_file_handler = (
            "try{ if(window.pywebview&&window.pywebview.api&&"
            "window.pywebview.api.new_file_from_dashboard){"
            "window.pywebview.api.new_file_from_dashboard(); } }"
            "catch(e){ console.error(e); }"
        )

    repl = {
        **_asset_uris(mode),
        "__SUBTITLE__": subtitle,
        "__RAW_DATA__": json.dumps(rows, ensure_ascii=False),
        "__TODAY_ARGS__": f"{today.year}, {today.month - 1}, {today.day}",
        "__NEW_FILE_HANDLER__": new_file_handler,
        "__PARSE_DQ__": json.dumps(parse_dq, ensure_ascii=False),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)
    return tpl


# --------------------------------------------------------------------------- #
# Welcome
# --------------------------------------------------------------------------- #
def render_welcome(
    mode: str = "pywebview",
    last_file: str | None = None,
    auto_open: bool = False,
    error: str | None = None,
) -> str:
    tpl = _read_template("welcome.html")

    # "Son dosyayı yeniden yükle" bloğu
    if last_file:
        disp = _html.escape(last_file)
        if mode == "flask":
            last_block = (
                '<button class="btn secondary" id="btnReloadLast">↻ Son dosyayı yeniden yükle</button>'
                f'<div class="last">Son yüklenen dosya:<div class="path">{disp}</div></div>'
            )
        else:
            last_block = (
                '<button class="btn secondary" id="btnReloadLast">↻ Son dosyayı yeniden yükle</button>'
                f'<div class="last">Son yüklenen dosya:<div class="path">{disp}</div></div>'
            )
    else:
        last_block = ""

    err_prefix = (
        f"const __ERRTXT__ = {json.dumps(error, ensure_ascii=False)};\n"
        "if(__ERRTXT__){ const e=document.getElementById('err');"
        " e.textContent=__ERRTXT__; e.classList.add('show'); }\n"
    )

    if mode == "flask":
        script = err_prefix + _WELCOME_FLASK_JS
    else:
        script = err_prefix + _WELCOME_PYWEBVIEW_JS
        script += (
            "\nfunction __autoOpen(){ setTimeout(()=>document.getElementById('btnLoad').click(), 80); }\n"
            + (
                "if(window.pywebview&&window.pywebview.api){ __autoOpen(); }"
                "else{ window.addEventListener('pywebviewready', __autoOpen); }\n"
                if auto_open else ""
            )
        )

    repl = {
        **_asset_uris(mode),
        "__LAST_FILE_BLOCK__": last_block,
        "__WELCOME_SCRIPT__": script,
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)
    return tpl


# --------------------------------------------------------------------------- #
# Mod bazlı welcome scriptleri
# --------------------------------------------------------------------------- #
_WELCOME_PYWEBVIEW_JS = r"""
const api = () => window.pywebview.api;
const $ = id => document.getElementById(id);
let pending = null;

function showErr(m){ $('err').textContent=m; $('err').classList.add('show'); }
function clearErr(){ $('err').classList.remove('show'); }
function busy(on){ $('busy').classList.toggle('show', on); }

async function startLoad(path){
  clearErr();
  if(!path) return;
  busy(true);
  let res;
  try{ res = await api().prepare(path); }
  catch(e){ busy(false); showErr('Beklenmeyen hata: '+e); return; }
  if(!res.ok){ busy(false); showErr(res.error); return; }
  if(res.needsConfirm){ busy(false); pending={path}; showModal(res.suggestions); return; }
  doLoad(path, false);
}
async function doLoad(path, accept){
  busy(true);
  try{ const res = await api().load(path, accept);
       if(res && !res.ok){ busy(false); showErr(res.error); } }
  catch(e){ busy(false); showErr('Beklenmeyen hata: '+e); }
}
function showModal(sugs){
  $('modalList').innerHTML = sugs.map(s=>
    `<div style="padding:7px 0;border-bottom:1px solid var(--line)">
       <span style="font-family:var(--mono);color:var(--muted)">${s.found||'(boş)'}</span>
       <span style="color:var(--faint)"> &rarr; </span>
       <span style="font-family:var(--mono)">${s.expected}</span>
       <span style="color:var(--faint);font-size:11px"> (%${Math.round((s.score||0)*100)} benzerlik)</span>
     </div>`).join('');
  $('modalBack').style.display='flex';
}
function hideModal(){ $('modalBack').style.display='none'; }

$('btnLoad').addEventListener('click', async ()=>{
  clearErr();
  let path='';
  try{ path = await api().open_file_dialog(); }
  catch(e){ showErr('Dosya seçici açılamadı: '+e); return; }
  if(path) startLoad(path);
});
$('modalOk').addEventListener('click', ()=>{ hideModal(); if(pending){ doLoad(pending.path, true); } });
$('modalCancel').addEventListener('click', ()=>{ hideModal(); pending=null; });

(function(){ const rl=$('btnReloadLast'); if(rl) rl.addEventListener('click', async ()=>{
  clearErr();
  try{ const p = await api().get_last_file(); if(p) startLoad(p); else showErr('Son dosya bulunamadı.'); }
  catch(e){ showErr('Beklenmeyen hata: '+e); }
}); })();
"""

_WELCOME_FLASK_JS = r"""
const $ = id => document.getElementById(id);
const form = document.createElement('form');
form.method='POST'; form.action='/load'; form.enctype='multipart/form-data'; form.style.display='none';
const input = document.createElement('input');
input.type='file'; input.name='file'; input.accept='.xlsx';
form.appendChild(input); document.body.appendChild(form);
$('btnLoad').addEventListener('click', ()=> input.click());
input.addEventListener('change', ()=>{ if(input.files.length){ $('busy').classList.add('show'); form.submit(); } });
(function(){ const rl=$('btnReloadLast'); if(rl) rl.addEventListener('click', ()=>{
  $('busy').classList.add('show'); window.location.href='/reload'; }); })();
"""

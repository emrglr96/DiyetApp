# -*- coding: utf-8 -*-
"""pywebview ve Flask önyüzlerinin ortak kullandığı yükleme mantığı."""
from __future__ import annotations

import datetime as _dt

import openpyxl

import config
import parser as xparser


def read_headers(path: str) -> list:
    """Yalnızca başlık satırını hızlıca oku."""
    try:
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    except Exception as e:
        raise xparser.ParseError(
            f"Excel dosyası açılamadı: {e}\n"
            "Dosyanın .xlsx biçiminde ve bozuk olmadığından emin olun."
        ) from e
    ws = wb.active
    headers = []
    for row in ws.iter_rows(min_row=1, max_row=1, values_only=True):
        headers = list(row)
        break
    wb.close()
    return headers


def prepare(path: str) -> dict:
    """
    Dosyayı yüklemeden önce kolon uyumunu denetle.
    Dönüş (UI için): {ok, error, needsConfirm, suggestions, missing}
    """
    try:
        headers = read_headers(path)
        plan = xparser.plan_columns(headers)
    except xparser.ParseError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        return {"ok": False, "error": f"Beklenmeyen hata: {e}"}

    if plan.missing_required:
        eksik = ", ".join(plan.missing_required)
        bulunan = ", ".join(h for h in plan.headers if h) or "(başlık yok)"
        return {
            "ok": False,
            "error": (
                "Zorunlu kolon(lar) bulunamadı:\n"
                f"  • {eksik}\n\n"
                f"Dosyadaki başlıklar:\n  {bulunan}"
            ),
        }

    return {
        "ok": True,
        "needsConfirm": plan.needs_confirmation,
        "suggestions": plan.suggestions,
        "missing": plan.missing_optional,
    }


def load(path: str, accept_suggestions: bool, today: _dt.date | None = None):
    """
    Dosyayı ayrıştır ve ParseResult döndür. Onay gereken ama onaylanmamış
    bulanık eşleşme varsa ParseError yükseltir.
    """
    if today is None:
        today = _dt.date.today()
    headers = read_headers(path)
    plan = xparser.plan_columns(headers)
    if plan.missing_required:
        raise xparser.ParseError(
            "Zorunlu kolon(lar) bulunamadı: " + ", ".join(plan.missing_required)
        )
    if plan.needs_confirmation and not accept_suggestions:
        raise xparser.ParseError(
            "Kolon eşleşmesi onayı gerekiyor (bulanık eşleşmeler var)."
        )
    result = xparser.parse_workbook(path, plan=plan, today=today)
    config.set_last_file(path)
    return result

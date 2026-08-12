# -*- coding: utf-8 -*-
"""
Şemaya uygun 10 satırlık örnek Excel üretir (kenar durumlar dahil):
 - TL cinsinden satır (₺)
 - '/' ve '.' tarih biçimleri + gerçek Excel datetime
 - 'x/o' gibi metin SM% değeri
 - Bitiş < Başlangıç (veri hatası)
 - Aynı Contract Number'ın iki satırı
 - Boş yıl kolonları
 - Yüzde-biçimli hücre (0.85 -> %85)
"""
import datetime as dt
import os

import openpyxl

HEADERS = [
    "Contract Number", "Müşteri", "Sözleşmenin Yıllık Bedeli", "(YTD) SM%",
    "(Fiscal Year) SM%", "Sözleşme Yenileme(Başlangıç) Tarihi",
    "Sözleşme Bitiş Tarihi", "Sözleşme Yenileme Period", "Sözleşme Bitiş Period",
    "(Son Sözleşme Dönemi) SM%", "1. Yıl", "2. Yıl", "3. Yıl", "4. Yıl", "5.yıl",
    "Sözleşmenin Toplam Bedeli", "Notlar",
]

# Her satır: 17 alan, HEADERS sırasıyla.
ROWS = [
    # normal, EUR, çok yıllı
    ["7083000306", "Acme A.Ş.", "€ 100,000.00", 78.42, 77.71, "01.01.2024",
     "31.12.2027", "2024", "2027", 71.68, "€ 73,600.00", "€ 88,000.00",
     "€ 88,000.00", "€ 88,000.00", None, "€ 337,600.00", ""],
    # kritik marj
    ["7083000453", "Beta Ltd.", "€ 120,000.00", 30.71, 22.85, "01.01.2024",
     "31.12.2026", "2024", "2026", 23.94, "€ 120,000.00", "€ 120,000.00",
     "€ 120,000.00", None, None, "€ 360,000.00", ""],
    # TL satır
    ["7083000567", "Ceyhan Enerji", "₺1,200,000.00", 78.82, 57.64, "07.01.2026",
     "06.01.2027", "2026", "2027", 63.69, "₺1,200,000.00", None, None, None,
     None, "₺1,200,000.00", "TL sözleşme"],
    # '/' tarih biçimi
    ["7083000515", "Delta Holding", "€ 120,000.00", 74.94, 60.78, "10/05/2022",
     "10/05/2027", "2022", "2027", 74.94, "€ 120,000.00", "€ 120,000.00",
     "€ 120,000.00", "€ 120,000.00", "€ 120,000.00", "€ 600,000.00", ""],
    # gerçek Excel datetime + yüzde-biçimli hücre (0.9 -> %90)
    ["7083000504", "Efes Gıda", "€ 133,000.00", 0.9080, 0.9019, dt.datetime(2024, 11, 21),
     dt.datetime(2027, 11, 20), "2024", "2027", 0.8915, "€ 133,000.00",
     "€ 133,000.00", "€ 133,000.00", None, None, "€ 399,000.00", ""],
    # 'x/o' metin SM% -> null + DQ
    ["7083000472", "Foça Tekstil", "€ 43,500.00", "x/o", "x/o", "25.01.2024",
     "24.01.2025", "2024", "2025", 27.59, "€ 43,500.00", None, None, None,
     None, "€ 43,500.00", "SM% girilmemiş"],
    # Bitiş < Başlangıç -> dataError
    ["7083000408", "Gemlik Kimya", "€ 93,000.00", 65.81, 77.45, "01.08.2026",
     "31.07.2026", "2026", "2026", 89.84, "€ 93,000.00", "€ 93,000.00",
     "€ 93,000.00", None, None, "€ 279,000.00", "Tarih hatası"],
    # aynı Contract Number - 1. satır
    ["7083000499", "Halic Lojistik", "€ 257,000.00", 39.91, 81.68, "16.03.2026",
     "15.03.2029", "2026", "2029", 89.42, "€ 257,000.00", "€ 257,000.00",
     "€ 257,000.00", None, None, "€ 771,000.00", "Çerçeve sözleşme"],
    # aynı Contract Number - 2. satır (birleştirme YOK)
    ["7083000499", "Halic Lojistik", "€ 116,000.00", 39.91, 81.68, "29.06.2026",
     "28.06.2029", "2026", "2029", 98.96, "€ 116,000.00", "€ 116,000.00",
     "€ 116,000.00", None, None, "€ 348,000.00", "Aynı no, ayrı kalem"],
    # '% 21.04%' karışık yüzde metni + süresi dolmuş
    ["7083000537", "İzmit Metal", "€ 23,800.00", "% 3.70%", "8.54%", "01.08.2024",
     "31.07.2025", "2024", "2025", "9.32%", "€ 23,800.00", None, None, None,
     None, "€ 23,800.00", "Marj düşük"],
]


def build(path: str):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sözleşmeler"
    ws.append(HEADERS)
    for r in ROWS:
        ws.append(r)
    # 5. satırdaki (index 4) SM% hücrelerini yüzde-biçimli yap: J,D,E kolonları
    # D=4 (YTD), E=5 (FY), J=10 (Son) — 1-tabanlı; veri satırı 6 (başlık=1).
    excel_row = 6
    for col in (4, 5, 10):
        ws.cell(row=excel_row, column=col).number_format = "0.00%"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    wb.save(path)
    print(f"Örnek dosya yazıldı: {path}  ({len(ROWS)} satır)")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    build(os.path.join(here, "ornek_veri.xlsx"))

# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller yapılandırması — tek klasör (onedir), taşınabilir (portable).

Üretim:
    pip install pyinstaller
    pyinstaller build.spec

Çıktı:  dist/SozlesmePortfoyPaneli/  (klasörün tamamını kopyalayın,
        SozlesmePortfoyPaneli.exe ile çalıştırın — kurulum/admin gerekmez)

Not: onedir modu, onefile'a göre antivirüs yanlış-pozitif riskini düşürür ve
     ilk açılışta geçici dizine çıkarım yapmadığı için daha hızlı başlar.
"""
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    # app/ içindeki yan modüller (main.py bunları sys.path ile içe aktarır)
    "config", "core", "parser", "render", "paths", "server",
    "openpyxl", "flask",
]
hiddenimports += collect_submodules("webview")

a = Analysis(
    ["app/main.py"],
    pathex=["app"],
    binaries=[],
    datas=[
        ("assets", "assets"),        # Chart.js + fontlar (offline)
        ("templates", "templates"),  # dashboard + welcome şablonları
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "pandas", "numpy", "matplotlib", "PyQt5", "PySide2"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SozlesmePortfoyPaneli",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,               # UPX kapalı -> AV yanlış-pozitif riski daha düşük
    console=False,           # pencereli uygulama (konsol yok)
    disable_windowed_traceback=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="SozlesmePortfoyPaneli",
)

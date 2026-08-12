@echo off
REM Uygulamayi kaynak koddan calistirir (Windows).
REM Ilk kullanimda bagimliliklari kurar.
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [HATA] Python bulunamadi. Python 3.11+ kurup PATH'e ekleyin.
  echo        https://www.python.org/downloads/
  pause
  exit /b 1
)

if not exist ".venv\" (
  echo Sanal ortam olusturuluyor...
  python -m venv .venv
  call .venv\Scripts\activate.bat
  echo Bagimliliklar kuruluyor...
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
) else (
  call .venv\Scripts\activate.bat
)

python app\main.py
endlocal

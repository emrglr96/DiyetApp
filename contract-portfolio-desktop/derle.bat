@echo off
REM Tasinabilir .exe uretir (Windows). Cikti: dist\SozlesmePortfoyPaneli\
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [HATA] Python bulunamadi. Python 3.11+ kurun.
  pause
  exit /b 1
)

if not exist ".venv\" (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

echo.
echo === PyInstaller calisiyor (onedir, tasinabilir) ===
pyinstaller --noconfirm build.spec

echo.
echo Tamamlandi. Ciktinizi burada bulacaksiniz:
echo   %cd%\dist\SozlesmePortfoyPaneli\
echo "SozlesmePortfoyPaneli.exe" ile calistirin. Klasorun tamamini kopyalayin.
pause
endlocal

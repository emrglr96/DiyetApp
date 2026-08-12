@echo off
REM ============================================================
REM  Kurulum sihirbazi (Setup.exe) uretir.
REM  1) PyInstaller ile portable .exe (dist\SozlesmePortfoyPaneli)
REM  2) Inno Setup ile SozlesmePortfoyPaneli_Setup.exe
REM  Cikti: installer\Output\SozlesmePortfoyPaneli_Setup.exe
REM ============================================================
setlocal EnableDelayedExpansion
cd /d "%~dp0"

REM --- Python kontrolu ---
where python >nul 2>nul
if errorlevel 1 (
  echo [HATA] Python bulunamadi. Python 3.11+ kurun: https://www.python.org/downloads/
  pause & exit /b 1
)

REM --- Sanal ortam + bagimliliklar ---
if not exist ".venv\" python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller pillow

REM --- Ikon yoksa uret ---
if not exist "assets\app.ico" python assets\make_icon.py

REM --- 1) PyInstaller: portable exe ---
echo.
echo === [1/2] PyInstaller calisiyor... ===
pyinstaller --noconfirm build.spec
if errorlevel 1 ( echo [HATA] PyInstaller basarisiz. & pause & exit /b 1 )

REM --- 2) Inno Setup Compiler (ISCC.exe) bul ---
echo.
echo === [2/2] Inno Setup ile kurulum paketleniyor... ===
set "ISCC="
for %%P in (
  "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
  "%ProgramFiles%\Inno Setup 6\ISCC.exe"
  "%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe"
) do if exist "%%~P" set "ISCC=%%~P"

if not defined ISCC (
  where iscc >nul 2>nul && for /f "delims=" %%I in ('where iscc') do set "ISCC=%%I"
)

if not defined ISCC (
  echo.
  echo [BILGI] Inno Setup bulunamadi. Ucretsizdir; sunlardan biriyle kurun:
  echo    winget install JRSoftware.InnoSetup
  echo    veya: https://jrsoftware.org/isdl.php
  echo.
  echo Kurduktan sonra bu script'i tekrar calistirin.
  echo Portable surum yine de hazir: dist\SozlesmePortfoyPaneli\
  pause & exit /b 1
)

"%ISCC%" "installer\installer.iss"
if errorlevel 1 ( echo [HATA] Inno Setup derlemesi basarisiz. & pause & exit /b 1 )

echo.
echo === TAMAMLANDI ===
echo Kurulum dosyasi: %cd%\installer\Output\SozlesmePortfoyPaneli_Setup.exe
echo Portable surum : %cd%\dist\SozlesmePortfoyPaneli\
pause
endlocal

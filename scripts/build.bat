@echo off
cd /d "%~dp0..\server"
echo.
echo  ✦ LUNA — Compilando ejecutable...
echo.
pyinstaller Luna.spec --noconfirm
if %errorlevel% equ 0 (
    if not exist "%~dp0..\dist" mkdir "%~dp0..\dist"
    copy /Y dist\Luna.exe "%~dp0..\dist\Luna.exe" >nul
    echo  ✓ Ejecutable creado en dist/
)
pause

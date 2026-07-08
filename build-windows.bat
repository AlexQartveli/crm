@echo off
setlocal
cd /d "%~dp0.."
powershell -ExecutionPolicy Bypass -File "scripts\build-windows.ps1"
pause

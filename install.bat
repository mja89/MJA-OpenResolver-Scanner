@echo off
echo 🚀 MJA OpenResolver Scanner - Installation

echo ========================================

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.7+
    echo.
    echo Download from: https://python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detected

:: Create necessary files
echo 📁 Creating required files...
type nul > client_resolvers.txt 2>nul
type nul > scan.log 2>nul

echo.
echo ✅ Installation complete!
echo.
echo 🚀 Run with: python run.py
echo.
echo 📖 Edit config.json for custom settings
pause

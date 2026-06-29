@echo off
echo 🚀 MJA OpenResolver Scanner - Installation
echo ========================================

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.7+
    pause
    exit /b 1
)

:: Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

:: Create necessary files
echo 📁 Creating required files...
type nul > client_resolvers.txt
type nul > scan.log

echo.
echo ✅ Installation complete!
echo.
echo 🚀 Run with: python run.py
echo.
echo 📖 Edit config.json for custom settings
pause

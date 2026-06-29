#!/bin/bash

# MJA OpenResolver Scanner Installer


echo "🚀 MJA OpenResolver Scanner - Installation"
echo "========================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.7+"
    exit 1
fi

echo "✅ Python detected"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Create necessary files
echo "📁 Creating required files..."
touch client_resolvers.txt
touch scan.log

# Set permissions
chmod +x run.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Run with: python3 run.py"
echo ""
echo "📖 Edit config.json for custom settings"

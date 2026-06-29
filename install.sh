### (برای لینوکس/مک)

```bash
#!/bin/bash

# MJA OpenResolver Scanner Installer

echo "🚀 MJA OpenResolver Scanner - Installation"
echo "========================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.7+"
    exit 1
fi

python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [ "$(echo "$python_version < 3.7" | bc)" -eq 1 ]; then
    echo "❌ Python 3.7+ required (found $python_version)"
    exit 1
fi

echo "✅ Python $python_version detected"

# Install pip if needed
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip3..."
    python3 -m ensurepip --upgrade
fi

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

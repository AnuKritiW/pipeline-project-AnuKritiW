#!/bin/bash

set -e  # Stop on error

echo "🔍 Checking if Python 3 is installed..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 is not installed. Please install it via Homebrew or python.org."
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment (venv)..."
  python3 -m venv venv
else
  echo "📦 Virtual environment already exists, skipping creation."
fi

echo "📂 Activating virtual environment..."
source venv/bin/activate

echo "🐍 Installing required Python packages..."
pip install --upgrade pip
pip install psutil

echo "✅ Setup complete!"
echo
echo "To run the project:"
echo "  source venv/bin/activate"
echo "  chmod +x scripts/sendstats.sh"
echo "  ./scripts/sendstats.sh"

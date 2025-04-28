#!/bin/bash

set -e  # Exit on any error

echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

echo "📂 Cloning Pimoroni Inky repository..."
git clone https://github.com/pimoroni/inky.git
cd inky

echo "🧪 Running Pimoroni's install.sh..."
./install.sh
cd ..

echo "📁 Cloning your project repository..."
git clone git@github.com:NCCA/pipeline-project-AnuKritiW.git

echo "🔧 Installing Vim editor..."
sudo apt install -y vim

# echo "📝 Setting up .vimrc with preferred settings..."
# cat << EOF > ~/.vimrc
# " Always show line numbers
# set number

# " Use 4 spaces instead of a real tab character
# set tabstop=4
# set shiftwidth=4
# set softtabstop=4
# set expandtab

# " Enable syntax highlighting
# syntax on

# " Remove trailing whitespace automatically on save
# autocmd BufWritePre * :%s/\\s\\+\$//e
# EOF

echo "📦 Installing required Python packages..."
source ~/.virtualenvs/pimoroni/bin/activate
pip install pytest
pip install pytest-cov
deactivate

echo "✅ Setup complete!"

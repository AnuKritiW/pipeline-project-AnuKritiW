#!/bin/bash

set -e  # Exit on any error

echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y expect

echo "🔧 Enabling SPI and I2C interfaces..."
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

cd ~
echo "📁 Now in $(pwd)"
if [ ! -d ~/inky ]; then
    echo "📂 Cloning Pimoroni Inky repository..."
    git clone https://github.com/pimoroni/inky.git
else
  echo "📂 Pimoroni Inky repository already exists, skipping clone."
fi
cd inky

echo "🧪 Running Pimoroni's install.sh..."
expect <<EOF
spawn ./install.sh
expect "Would you like us to create and/or use a default one?"
send "y\r"
expect "Would you like to copy examples"
send "y\r"
expect "Would you like to install example dependencies"
send "y\r"
expect eof
EOF
# y | ./install.sh
cd ..

# echo "🔧 Installing Vim editor..."
# sudo apt install -y vim

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
if [ -f ~/.virtualenvs/pimoroni/bin/activate ]; then
    source ~/.virtualenvs/pimoroni/bin/activate
else
  echo "❌ Pimoroni virtualenv not found!"
  exit 1
fi

pip install pytest pytest-cov
deactivate

echo "✅ Setup complete!"

echo "⚙️ Setting up systemd service..."

# Copy the service file
cd ~/pipeline-project-AnuKritiW
echo "📁 Now in $(pwd)"
sudo cp install/pipeline-project.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the service (auto-start on boot)
sudo systemctl enable pipeline-project.service

# Start the service right now
sudo systemctl start pipeline-project.service

echo "✅ Service installed and running!"
echo "Visit http://pi.local to see the web interface."
echo "You can control it with:"
echo "  sudo systemctl stop pipeline-project.service"
echo "  sudo systemctl start pipeline-project.service"
echo "  sudo systemctl restart pipeline-project.service"
echo "  sudo systemctl status pipeline-project.service"

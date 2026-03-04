#!/data/data/com.termux/files/usr/bin/bash

echo "[*] Updating Termux packages..."
pkg update -y && pkg upgrade -y

echo "[*] Checking Python..."

# Install Python if not installed
if ! command -v python >/dev/null 2>&1; then
    echo "[*] Python not found. Installing Python..."
    pkg install python -y
else
    echo "[*] Python already installed."
fi

echo "[*] Upgrading pip..."
python -m ensurepip --upgrade
python -m pip install --upgrade pip

echo "[*] Installing Python packages..."
python -m pip install \
requests \
psutil \
PyJWT \
urllib3 \
pytz \
aiohttp \
cfonts \
protobuf \
protobuf-decoder \
google \
pycryptodome \
httpx \
flask \
flask-cors \
flask-sock \
simple-websocket \
colorama \
google-play-scraper

echo "[✓] Installation completed successfully!"
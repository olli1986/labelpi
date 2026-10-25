#!/bin/bash
# LabelPi-Installation auf Raspberry Pi OS Lite.
# Ein-Befehl-Variante:  curl -fsSL https://raw.githubusercontent.com/olli1986/labelpi/main/install.sh | bash
set -e
REPO="${LABELPI_REPO:-https://github.com/olli1986/labelpi.git}"
if [ -f "$(dirname "$0")/app.py" ]; then
  cd "$(dirname "$0")"
else
  sudo apt update && sudo apt install -y git
  if [ -d "$HOME/labelpi/.git" ]; then git -C "$HOME/labelpi" pull; else git clone "$REPO" "$HOME/labelpi"; fi
  cd "$HOME/labelpi"
fi
DIR=$(pwd); U=${SUDO_USER:-$USER}
sudo apt update
sudo apt install -y python3-venv poppler-utils libusb-1.0-0 libopenjp2-7 libtiff6 libwebp7 libjpeg62-turbo liblcms2-2 libfreetype6 libharfbuzz0b libxcb1
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -r requirements.txt
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="04f9", MODE="0666"' | sudo tee /etc/udev/rules.d/99-brother-ql.rules >/dev/null
sudo udevadm control --reload-rules
echo "$U ALL=(root) NOPASSWD: /usr/bin/systemctl reboot, /usr/bin/systemctl poweroff" | sudo tee /etc/sudoers.d/labelpi >/dev/null
sudo chmod 440 /etc/sudoers.d/labelpi
sudo tee /etc/systemd/system/labelpi.service >/dev/null <<UNIT
[Unit]
Description=LabelPi Etikettendruck
After=network-online.target
[Service]
User=$U
WorkingDirectory=$DIR
ExecStart=$DIR/.venv/bin/python app.py
Restart=always
AmbientCapabilities=CAP_NET_BIND_SERVICE
[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable labelpi
sudo systemctl restart labelpi
echo "Fertig. Aufruf im Browser: http://$(hostname).local"

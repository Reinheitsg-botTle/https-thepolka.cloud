#!/usr/bin/env bash
set -e

TARGET="$HOME/thepolka.cloud/x.thepolka.cloud"
mkdir -p "$TARGET"
cp -r ./* "$TARGET"/ 2>/dev/null || true
cd "$TARGET"

python3 -m venv venv
./venv/bin/pip install -r requirements.txt

mkdir -p "$HOME/.config/systemd/user"
cp x-thepolka.service "$HOME/.config/systemd/user/x-thepolka.service"

systemctl --user daemon-reload
systemctl --user enable --now x-thepolka.service

echo ""
echo "Installed. Running on 127.0.0.1:8006"
echo "Point your Cloudflare tunnel ingress for x.thepolka.cloud -> http://localhost:8006"
echo "Check status: systemctl --user status x-thepolka.service"

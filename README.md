# ThePolka.Cloud

## Architecture

| App | Directory | Port |
|-----|-----------|------|
| thepolka.cloud | `~/thepolka.cloud/` | 8001 |
| resume-generator.thepolka.cloud | `~/thepolka.cloud/resume-generator.thepolka.cloud/` | 8002 |

Cloudflare Tunnel routes by hostname → `~/.cloudflared/config.yml`

---

## First-time setup

### Root app (Terminal 1)
```bash
cd ~/thepolka.cloud
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Resume Generator (Terminal 2)
```bash
cd ~/thepolka.cloud/resume-generator.thepolka.cloud
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Cloudflare Tunnel (Terminal 3)
```bash
cloudflared tunnel run thepolka-cloud
# config lives at ~/.cloudflared/config.yml
# copy cloudflare-tunnel.yml there if not already done
```

### Terminal 4 — maintenance / edits

---

## Daily workflow (after setup)

```bash
# Terminal 1 — root
cd ~/thepolka.cloud && source .venv/bin/activate && python app.py

# Terminal 2 — resume-generator
cd ~/thepolka.cloud/resume-generator.thepolka.cloud && source .venv/bin/activate && python app.py

# Terminal 3 — tunnel
cloudflared tunnel run thepolka-cloud
```

---

## Systemd (make persistent — no manual restart after reboot)

```bash
sudo cp thepolka.cloud.service /etc/systemd/system/
sudo cp resume-generator.thepolka.cloud/resume-generator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable thepolka.cloud resume-generator
sudo systemctl start thepolka.cloud resume-generator
```

---

## GitHub backup

```bash
cd ~/thepolka.cloud
git init  # first time only
git remote add origin https://github.com/Reinheitsg-botTle/https-thepolka.cloud
git add .
git commit -m "MVP: clean layout, global nav, resume-generator working"
git push -u origin main
```

---

## Key files

```
~/thepolka.cloud/
├── app.py                          ← root Flask (port 8001)
├── requirements.txt
├── cloudflare-tunnel.yml           ← copy to ~/.cloudflared/config.yml
├── thepolka.cloud.service          ← systemd
├── templates/
│   ├── layout.html                 ← GLOBAL nav + footer (shared)
│   ├── home.html                   ← #welcome
│   └── 404.html
├── static/
│   ├── css/site.css                ← all styles
│   └── js/script.js
└── resume-generator.thepolka.cloud/
    ├── app.py                      ← resume Flask (port 8002)
    ├── requirements.txt
    ├── resume-generator.service    ← systemd
    ├── templates/
    │   ├── layout.html             ← copy of shared layout
    │   ├── index.html              ← #resume form + JS
    │   └── 404.html
    ├── static/css/site.css
    ├── static/js/script.js
    └── resume_generator/           ← Python package (untouched)
        ├── normalize.py
        └── renderer/
            ├── html.py
            ├── markdown.py
            ├── pdf.py
            └── docx.py
```

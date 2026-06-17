# Resume Machine — thepolka.cloud

> One form. Four formats. Instant download.
> Live at: `resume-generator.thepolka.cloud`

---

## What this does

Fill in your resume information once — name, purpose statement, experience with
Action → Result → Impact bullets, volunteer work, certificates, awards, hobbies,
and contact info. Click **Generate**. Download a ZIP containing:

- `resume.md`   — Markdown (GitHub-ready, easy to version)
- `resume.html` — Polished, print-ready HTML (email-ready)
- `resume.pdf`  — PDF via WeasyPrint
- `resume.docx` — Word document via python-docx

---

## File structure

```
resume-generator/
├── app.py                        # Flask backend — one endpoint: POST /generate
├── requirements.txt
├── resume-generator.service      # systemd unit for Linux autostart
├── cloudflare-tunnel.yml         # Cloudflare tunnel config
├── templates/
│   └── index.html                # The full UI — self-contained, no build step
└── resume_generator/
    ├── __init__.py
    ├── normalize.py              # Canonical schema — all renderers read from this
    └── renderer/
        ├── __init__.py
        ├── markdown.py           # → .md
        ├── html.py               # → .html  (also used by PDF renderer)
        ├── pdf.py                # → .pdf   (WeasyPrint → reportlab fallback)
        └── docx.py               # → .docx  (python-docx)
```

---

## Linux setup (first time)

```bash
# 1. Clone and enter
git clone https://github.com/YOUR_USER/resume-generator.git
cd resume-generator

# 2. Create virtualenv
python3 -m venv venv
source venv/bin/activate

# 3. Install Python deps
pip install -r requirements.txt

# 4. Install WeasyPrint system deps (Debian/Ubuntu)
sudo apt install -y libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libffi-dev

# 5. Run locally to test
python app.py
# → open http://localhost:5000
```

---

## Deploy on your Linux server

```bash
# Copy files to server
sudo mkdir -p /opt/resume-generator
sudo cp -r . /opt/resume-generator
sudo chown -R www-data:www-data /opt/resume-generator

# Set up virtualenv on server
cd /opt/resume-generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt install -y libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# Install and start systemd service
sudo cp resume-generator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable resume-generator
sudo systemctl start resume-generator

# Check it's running
sudo systemctl status resume-generator
curl http://localhost:5000/health
```

---

## Cloudflare Tunnel (resume-generator.thepolka.cloud)

```bash
# Install cloudflared if not already
curl -L https://pkg.cloudflare.com/cloudflare-main.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloudflare-main.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update && sudo apt install cloudflared

# Authenticate (opens browser)
cloudflared tunnel login

# Create the tunnel
cloudflared tunnel create resume-generator

# Copy the config
mkdir -p ~/.cloudflared
cp cloudflare-tunnel.yml ~/.cloudflared/config.yml
# Edit config.yml: replace YOUR_USER with your Linux username

# Add DNS record (points resume-generator.thepolka.cloud → tunnel)
cloudflared tunnel route dns resume-generator resume-generator.thepolka.cloud

# Run tunnel (test)
cloudflared tunnel run resume-generator

# Run as service (permanent)
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

---

## GitHub setup (push the whole project)

```bash
cd resume-generator
git init
git add .
git commit -m "Initial commit — resume machine"
git remote add origin https://github.com/Reinheitsg-botTle/resume-generator.git
git push -u origin main
```

For updates (pull to server and restart):
```bash
cd /opt/resume-generator
git pull origin main
sudo systemctl restart resume-generator
```

---

## Embedding into thepolka.cloud homepage

Add a link or button on your homepage that points to the subdomain:

```html
<!-- On your main site homepage -->
<a href="https://resume-generator.thepolka.cloud#generate">
  Generate your resume →
</a>
```

Or embed it in an iframe on a dedicated page:
```html
<iframe
  src="https://resume-generator.thepolka.cloud"
  width="100%"
  height="900"
  frameborder="0"
  title="Resume Generator">
</iframe>
```

---

## The Action → Result → Impact format

Every entry in Experience, Volunteer, Certificates, and Awards follows this structure:

| Field  | What to write |
|--------|--------------|
| **Action** | What you did — a verb phrase. "Built chatbot pipeline in Python." |
| **Result** | What happened. "Deployed capstone project on Linux, hosted publicly." |
| **Impact** | Measurable outcome. "5 users/day generating resumes. 20 new files/day automated." |

This structure gives recruiters exactly what they need: proof of initiative, outcome, and scale.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| flask | Web server |
| flask-cors | Cross-origin support |
| weasyprint | HTML → PDF (preferred) |
| reportlab | PDF fallback if WeasyPrint unavailable |
| python-docx | Generate .docx files |

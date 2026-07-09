# Faire — fresh build

A glowing floating orb that lives on every page of thepolka.cloud, plus a
standalone page at faire.thepolka.cloud explaining what she is.

## 1. Wipe the old, messy version first

Your server has accumulated duplicate/nested folders and multiple stray
`app.py` processes from earlier iterations. Clean it out before installing
this:

```bash
# kill any leftover Faire processes
ps aux | grep app.py
kill <pid> <pid> ...   # for any python3 app.py running from a faire folder

# back up just in case, then remove the old faire folder entirely
mv ~/thepolka.cloud/faire.thepolka.cloud ~/thepolka.cloud/faire.thepolka.cloud.OLD_$(date +%s)
```

(Leave the unrelated `local-ai-os/faire-os` Vite/React project alone for
now — that's a separate thing from this Flask widget. We can fold it in
later if you want.)

## 2. Install this fresh copy

Unzip so you end up with exactly:

```
~/thepolka.cloud/faire.thepolka.cloud/
├── app.py
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   ├── faire.css
    │   └── faire-widget.css
    ├── js/
    │   └── faire-widget.js
    └── img/
        └── faire-icon.svg
```

```bash
unzip faire-fresh.zip -d ~/thepolka.cloud/
mv ~/thepolka.cloud/faire-fresh ~/thepolka.cloud/faire.thepolka.cloud
```

## 3. Install deps and run

```bash
cd ~/thepolka.cloud/faire.thepolka.cloud
pip3 install flask openai

# optional — to make Faire actually talk via OpenAI instead of stub replies:
export OPENAI_API_KEY="sk-..."

python3 app.py
```

Test:
```bash
curl -s http://localhost:8003/ | head -20
```
You should see `<title>Faire — your local AI, everywhere | thepolka.cloud</title>`.
Open `http://<server-ip>:8003` in a browser — you should see the glowing
orb pulsing in the bottom-right corner. Click it to open the chat panel.

### Keep OPENAI_API_KEY set across restarts

`export` only lasts for that shell session. For a persistent setup, put it
in a systemd service `Environment=` line, or a `.env` you load before
`python3 app.py`. Want a systemd unit file for this? Just ask.

## 4. Cloudflare tunnel + DNS

In `~/.cloudflared/config.yml`:
```yaml
ingress:
  - hostname: resume-generator.thepolka.cloud
    service: http://localhost:8001
  - hostname: faire.thepolka.cloud
    service: http://localhost:8003
  - service: http_status:404
```

```bash
cloudflared tunnel ingress validate
cloudflared tunnel route dns thepolka-home faire.thepolka.cloud
sudo systemctl restart cloudflared
```

## 5. Make Faire appear on EVERY page of thepolka.cloud

Copy this block into your main site's `templates/layout.html` (and any
other site's layout), right before `</body>`:

```html
<link rel="stylesheet" href="https://faire.thepolka.cloud/static/css/faire-widget.css">
<div id="faire-root"></div>
<script src="https://faire.thepolka.cloud/static/js/faire-widget.js" defer></script>
<script>
  window.addEventListener('DOMContentLoaded', () => {
    Faire.init({
      apiBase: 'https://faire.thepolka.cloud/api',
      title: 'Faire',
      subtitle: 'your local AI, everywhere'
    });
  });
</script>
```

Because the CSS/JS/API are all loaded from `faire.thepolka.cloud`, every
other subdomain (resume-generator, the main site, etc.) gets the exact
same orb, same brain, with zero file duplication. One source of truth.

Note: cross-origin requests from other subdomains to
`https://faire.thepolka.cloud/api/chat` will need CORS enabled. If you hit
a CORS error in the browser console once you wire this onto another
subdomain, tell me and I'll add `flask-cors` to `app.py`.

## 6. `#ai` / `#chat` auto-open

Linking to `https://faire.thepolka.cloud#ai` (or any page with the widget
loaded, `yoursite.com#ai`) will automatically pop the chat panel open on
load — matching the `#resume` pattern from resume-generator.

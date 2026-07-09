# Faire — faire.thepolka.cloud

A standalone subdomain page + a drop-in, dependency-free chat widget ("Faire")
you can later embed on **every** page of thepolka.cloud.

## File layout

```
faire.thepolka.cloud/
├── templates/
│   ├── layout.html          (you already have this)
│   └── index.html           (new — renders the page + mounts the widget)
└── static/
    ├── css/
    │   ├── faire.css         (page styles)
    │   └── faire-widget.css  (widget styles, scoped to #faire-widget-root)
    ├── js/
    │   └── faire-widget.js   (the widget itself — vanilla JS, no deps)
    └── img/
        └── faire-icon.svg
```

`index.html` was built standalone (not yet wired into your `layout.html`
inheritance) since I don't have your layout.html content. To integrate:

1. Open your real `templates/layout.html`.
2. Make sure it has a `{% block content %}{% endblock %}` (Flask/Jinja) or
   equivalent, and a place near `</body>` for scripts.
3. Move the `<main class="faire-page">...</main>` block from `index.html`
   into that content block, and the widget mount block
   (`<div id="faire-widget-root">` + the two `<script>`/`<link>` tags)
   into the scripts area of layout.html — that's what makes Faire "global"
   once you reuse the same layout.html across other subdomain sites.

## Going global (every page of thepolka.cloud)

Once happy with it here, copy this block into any page/layout across the
site:

```html
<link rel="stylesheet" href="https://faire.thepolka.cloud/static/css/faire-widget.css">
<div id="faire-widget-root"></div>
<script src="https://faire.thepolka.cloud/static/js/faire-widget.js" defer></script>
<script>
  window.addEventListener('DOMContentLoaded', () => {
    Faire.init({
      mount: '#faire-widget-root',
      apiBase: 'https://faire.thepolka.cloud/api',
      title: 'Faire',
      subtitle: 'local-ai-os'
    });
  });
</script>
```

Because the CSS/JS are referenced by absolute URL, every other subdomain
(resume-generator.thepolka.cloud, etc.) can pull the same widget without
duplicating files — one source of truth on faire.thepolka.cloud.

## Backend wiring (port 8003)

`faire-widget.js` currently POSTs to `${apiBase}/chat` expecting:

```json
// request
{ "message": "hello", "history": [{"role":"user","content":"..."}] }
// response
{ "reply": "..." }
```

Point `apiBase` at wherever your chatbot backend actually lives. If your
backend serves JSON at a different shape, edit the `sendMessage()` function
in `faire-widget.js` — that's the only place that talks to the network.

## Cloudflare tunnel (3rd port, 8003)

In your `cloudflared` config (e.g. `~/.cloudflared/config.yml`), add an
ingress rule alongside your existing two:

```yaml
ingress:
  - hostname: resume-generator.thepolka.cloud
    service: http://localhost:8001   # example, whatever you already have
  - hostname: some-other.thepolka.cloud
    service: http://localhost:8002   # example
  - hostname: faire.thepolka.cloud
    service: http://localhost:8003
  - service: http_status:404
```

Then in Cloudflare DNS, add a CNAME for `faire` pointing to your tunnel's
`<TUNNEL_ID>.cfargotunnel.com` (same pattern as your other subdomains), and
restart/reload `cloudflared`:

```bash
cloudflared tunnel ingress validate
sudo systemctl restart cloudflared   # or however you run it
```

Whatever process serves your chatbot needs to actually listen on
`localhost:8003` (FastAPI/Flask/Node/whatever you choose) — this scaffold
only ships the **frontend**. Once you know what's powering the bot, I can
wire up the `/api/chat` route to match it (FastAPI, Flask, Ollama-proxy,
etc.) — just paste/describe the backend and I'll connect `faire-widget.js`
and add a matching server route.

## Note on the URL fragment

You mentioned `https://faire.thepolka.cloud#ai` and the resume-generator's
`#resume` fragment — those are just URL fragments (anchors), not separate
routes; they don't need server-side handling. If `#resume` and `#ai` are
meant to trigger something in JS (e.g. auto-open the widget, or scroll to a
section), say so and I'll add a small `location.hash` check in
`faire-widget.js` (e.g. `#ai` → `startOpen: true`).

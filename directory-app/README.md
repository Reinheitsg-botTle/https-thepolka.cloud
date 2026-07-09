# Internal Directory Service (`directory.thepolka.cloud`)

Solves: many employees can share one **public-facing** address
(e.g. `michelle@amazon`), while HR/IT privately track *which* Michelle
is which and route her mail correctly — without the disambiguation tag
ever appearing in the visible address.

## Model

- **display_email** — what's printed everywhere public: business cards,
  email signatures, directory pages. Not unique on its own.
- **internal_anchor** — hidden key, e.g. `secure`, `privacy`, `kieckhefer`.
  Lives only in this database. Combined with `display_email` it's unique.
- **routing_target** — the real mailbox the message should land in.

The anchor is resolved **server-side only**, at the mail-routing layer
(e.g. inside a Cloudflare Email Worker, or your MTA's delivery hook),
never parsed out of the `To:` header a recipient sees.

## Quickstart

```bash
cd directory-app
python3 -m venv .venv && source .venv/bin/activate
pip install flask
export DIRECTORY_ADMIN_TOKEN="pick-something-real"
python app.py        # runs on :8005
```

## Wiring into your existing stack

- Same `ChoiceLoader` + shared `layout.html` pattern as `cad.thepolka.cloud`
  and `faire.thepolka.cloud` — just point it at
  `~/thepolka.cloud/shared_templates` (or drop in `layout_fallback.html`
  if you haven't broken that shared template out yet).
- Add a Cloudflare Email Routing rule / Worker in front of your real MTA
  that, for any address needing disambiguation, calls:
  `GET /route?display_email=michelle@amazon&anchor=secure`
  and delivers to whatever `routing_target` comes back.
- Add this app to the tunnel config (`thepolka-home`) on port 8005,
  same as the others.

## Example: three Michelles, one public address

```bash
curl -X POST http://localhost:8005/admin/employees \
  -H "X-Admin-Token: $DIRECTORY_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_email": "michelle@amazon",
    "internal_anchor": "secure",
    "real_name": "Michelle A.",
    "department": "Security",
    "routing_target": "michelle.a.internal@yourmailserver.com"
  }'

curl -X POST http://localhost:8005/admin/employees \
  -H "X-Admin-Token: $DIRECTORY_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_email": "michelle@amazon",
    "internal_anchor": "privacy",
    "real_name": "Michelle B.",
    "department": "Compliance",
    "routing_target": "michelle.b.internal@yourmailserver.com"
  }'
```

Both show up externally as `michelle@amazon`. Internally, `/route` tells
you exactly which mailbox each message belongs in.

## Security notes before this touches real data

- Swap the shared-secret header for real auth (session login, SSO, or at
  minimum a properly rotated secret in a vault, not an env var default).
- `internal_anchor` and `real_name` are sensitive HR-adjacent fields —
  make sure the DB file and backups are encrypted at rest, and that this
  service is never exposed on the public internet without auth in front
  of it (not even through the Cloudflare tunnel without Access policies).
- Log access to `/admin/*` and `/route` for audit purposes.

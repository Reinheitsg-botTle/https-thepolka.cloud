# Barbie Agents

Small, local-first agents that share one base model (the **Naked Barbie**) and add focused wardrobes such as Security, Weather, Finance, or Resume.

## Start here

```bash
cd ~/thepolka.cloud/agent.thepolka.cloud
cp .env.example .env
python3 app.py scan --target https://agent.thepolka.cloud
python3 app.py serve
```

Open `http://127.0.0.1:8080`. Reports are written to `reports/output/` and scan history to `data/barbie.db`.

## Security boundary

The Security Barbie only scans hosts listed in `ALLOWED_TARGETS`. It uses safe, unauthenticated checks: TLS certificate metadata, DNS, response headers, robots/security.txt discovery, and optional local dependency manifests. It does not attack, brute force, enumerate ports, or run active vulnerability payloads.

## Daily schedule

```bash
crontab -e
# 15 minutes after 7 AM every day
15 7 * * * cd /home/bball_1181/thepolka.cloud/agent.thepolka.cloud && /usr/bin/python3 app.py daily >> logs/daily.log 2>&1
```

## Add a wardrobe

Create `agents/weather_agent.py`, subclass `BaseBarbie`, and register it in `agents/registry.py`. The base agent supplies configuration, auditable runs, report storage, and the dashboard data contract.

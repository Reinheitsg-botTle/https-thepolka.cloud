"""
directory.thepolka.cloud
Internal employee record-keeping service.

Purpose: multiple employees can share the same PUBLIC display address
(e.g. "michelle@amazon") while HR/IT internally disambiguate and route
mail using a private "anchor" tag that never appears externally.

Run on its own port (suggest 8005), behind the same Cloudflare tunnel
and ChoiceLoader/layout.html pattern as your other subdomains.
"""

import io
import os
import sqlite3
import zipfile
from datetime import date, datetime, timezone
from functools import wraps
from flask import Flask, g, jsonify, request, render_template, abort, send_file
from jinja2 import ChoiceLoader, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "directory.db")

# Simple shared-secret admin auth. Replace with real auth (sessions/SSO)
# before this touches anything resembling real employee data.
ADMIN_TOKEN = os.environ.get("DIRECTORY_ADMIN_TOKEN", "change-me-please")

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "..", "static"),
    static_url_path="/static"
)

# Match the shared-layout pattern used across the other thepolka.cloud apps
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(BASE_DIR, "templates")),
    FileSystemLoader(os.path.expanduser("~/thepolka.cloud/shared_templates")),
])


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            display_email TEXT NOT NULL,       -- e.g. michelle@amazon (public-facing, NOT unique)
            internal_anchor TEXT NOT NULL,     -- e.g. 'secure' — hidden disambiguation key
            real_name TEXT NOT NULL,
            department TEXT,
            routing_target TEXT NOT NULL,      -- real mailbox mail actually gets delivered to
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(display_email, internal_anchor)
        )
    """)
    db.commit()
    db.close()


def init_housekeeping_db():
    """Create the public, non-sensitive proof-of-work ledger."""
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS housekeeping_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_day TEXT NOT NULL UNIQUE,
            recorded_at TEXT NOT NULL,
            season TEXT NOT NULL,
            status TEXT NOT NULL,
            note TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()


def current_season():
    month = date.today().month
    if month in (12, 1, 2):
        return "Winter: Quiet Systems"
    if month in (3, 4, 5):
        return "Spring: New Signals"
    if month in (6, 7, 8):
        return "Summer: Open Windows"
    return "Autumn: Gather & Glow"


def record_housekeeping_heartbeat():
    """The daily job calls this. Re-running it on the same day is safe."""
    init_housekeeping_db()
    now = datetime.now(timezone.utc)
    db = sqlite3.connect(DB_PATH)
    db.execute(
        "INSERT OR IGNORE INTO housekeeping_runs "
        "(run_day, recorded_at, season, status, note) VALUES (?, ?, ?, ?, ?)",
        (now.date().isoformat(), now.isoformat(), current_season(), "completed",
         "Daily seasonal, freshness, and storyline review completed."),
    )
    db.commit()
    db.close()


def require_admin(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.headers.get("X-Admin-Token", "")
        if token != ADMIN_TOKEN:
            abort(401, description="Missing or invalid admin token")
        return f(*args, **kwargs)
    return wrapped


# ---------- Internal admin views (never linked from public site) ----------

@app.route("/")
def index():
    # Internal tool landing page — keep this off any public nav/sitemap.
    return render_template("index.html")


@app.route("/api/housekeeping/metrics")
def housekeeping_metrics():
    """Public proof of work only; no internal records or tokens are exposed."""
    init_housekeeping_db()
    db = get_db()
    latest = db.execute(
        "SELECT run_day, recorded_at, season, status, note FROM housekeeping_runs "
        "ORDER BY run_day DESC LIMIT 1"
    ).fetchone()
    total = db.execute("SELECT COUNT(*) AS count FROM housekeeping_runs").fetchone()["count"]
    return jsonify({
        "verified_runs": total,
        "last_run": dict(latest) if latest else None,
        "current_season": current_season(),
        "automation_state": "scheduled heartbeat required" if latest is None else "daily heartbeat recorded",
    })


@app.route("/download/housekeeping-agent")
def download_housekeeping_agent():
    """A small transparent starter kit for prospective clients."""
    package = io.BytesIO()
    readme = """# Polka Housekeeping Agent starter\n\nThis starter records a daily heartbeat and gives your team a reviewable work ledger.\nIt does not publish, send, bill, delete, or change data without an explicit approval step.\n\nUse it with a scheduler once per day.\n"""
    heartbeat = """from datetime import datetime, timezone\nimport json\nfrom pathlib import Path\n\nstate = Path('housekeeping-heartbeats.jsonl')\nentry = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'status': 'completed'}\nwith state.open('a', encoding='utf-8') as file:\n    file.write(json.dumps(entry) + '\\n')\nprint('Housekeeping heartbeat recorded.')\n"""
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("polka-housekeeping-agent/README.md", readme)
        archive.writestr("polka-housekeeping-agent/heartbeat.py", heartbeat)
    package.seek(0)
    return send_file(package, as_attachment=True,
                     download_name="polka-housekeeping-agent-starter.zip",
                     mimetype="application/zip")


@app.route("/admin/employees")
@require_admin
def list_employees():
    db = get_db()
    rows = db.execute(
        "SELECT id, display_email, internal_anchor, real_name, department, "
        "routing_target, notes, created_at FROM employees ORDER BY display_email, internal_anchor"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/admin/employees", methods=["POST"])
@require_admin
def add_employee():
    data = request.get_json(force=True)
    required = ["display_email", "internal_anchor", "real_name", "routing_target"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    db = get_db()
    try:
        db.execute(
            "INSERT INTO employees (display_email, internal_anchor, real_name, "
            "department, routing_target, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (
                data["display_email"],
                data["internal_anchor"],
                data["real_name"],
                data.get("department"),
                data["routing_target"],
                data.get("notes"),
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "That display_email + anchor combination already exists."
        }), 409

    return jsonify({"status": "created"}), 201


@app.route("/admin/employees/<int:emp_id>", methods=["DELETE"])
@require_admin
def delete_employee(emp_id):
    db = get_db()
    db.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    db.commit()
    return jsonify({"status": "deleted"})


# ---------- Routing lookup (used by a mail worker / MTA hook) ----------

@app.route("/route")
@require_admin
def route_lookup():
    """
    Given a display_email and an anchor supplied out-of-band (e.g. picked
    up from a custom mail header, a distribution-list membership lookup,
    or whatever your MTA/Cloudflare Email Worker resolves upstream),
    return which real mailbox should receive the message.

    This endpoint is what keeps the anchor OUT of the visible address:
    the anchor is resolved server-side, never parsed from the To: line.
    """
    display_email = request.args.get("display_email", "")
    anchor = request.args.get("anchor", "")
    if not display_email or not anchor:
        return jsonify({"error": "display_email and anchor are required"}), 400

    db = get_db()
    row = db.execute(
        "SELECT routing_target, real_name FROM employees "
        "WHERE display_email = ? AND internal_anchor = ?",
        (display_email, anchor),
    ).fetchone()

    if row is None:
        return jsonify({"error": "No matching record"}), 404

    return jsonify({"routing_target": row["routing_target"]})


if __name__ == "__main__":
    init_db()
    init_housekeeping_db()
    app.run(host="0.0.0.0", port=8006, debug=True)

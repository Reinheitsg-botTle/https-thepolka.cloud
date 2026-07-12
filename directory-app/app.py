"""
directory.thepolka.cloud
Internal employee record-keeping service.

Purpose: multiple employees can share the same PUBLIC display address
(e.g. "michelle@amazon") while HR/IT internally disambiguate and route
mail using a private "anchor" tag that never appears externally.

Run on its own port (suggest 8005), behind the same Cloudflare tunnel
and ChoiceLoader/layout.html pattern as your other subdomains.
"""

import os
import sqlite3
from functools import wraps
from flask import Flask, g, jsonify, request, render_template, abort
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
    app.run(host="0.0.0.0", port=8005, debug=True)

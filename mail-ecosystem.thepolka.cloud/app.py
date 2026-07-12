"""
mail-ecosystem.thepolka.cloud — Flask backend
Port: 8006 (adjust PORT env var if needed to avoid clashing with 8001-8005)
Run: source .venv/bin/activate && python3 app.py

Storage: SQLite file db.sqlite3, created and seeded automatically on first run.
No external DB service required — this fixes the "Error connecting to Python
service" issue from before, since there's no separate backend dependency to wire up.
"""
import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, request, jsonify, render_template, g
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


SEED_CONTACTS = [
    ("andy@alight",              "Andy",     "Active"),
    ("alex@ x",                  "Alex",     "Active"),
    ("ericka@northwesternmutual","Ericka",   "Active"),
    ("michelle@amazon",          "Michelle", "Active"),
    ("robert@ibm",               "Robert",   "Active"),
    ("katie@lyft",               "Katie",    "Active"),
    ("sevi@bankofamerica",       "Sevi",     "Active"),
    ("jordan@salesforce",        "Jordan",   "Active"),
    ("pia@netflix",              "Pia",      "Active"),
    ("marcus@intuit",            "Marcus",   "Active"),
    ("lena@stripe",              "Lena",     "Active"),
    ("Amy@adp",                  "Amy",      "Active"),
    ("david@gruberlawoffices",   "David",    "Active")
]


def init_db():
    fresh = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mailboxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL DEFAULT '',
            body TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            read INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            detail TEXT
        )
    """)
    conn.commit()

    if fresh:
        conn.executemany(
            "INSERT OR IGNORE INTO mailboxes (address, display_name, status) VALUES (?, ?, ?)",
            SEED_CONTACTS,
        )
        conn.execute(
            "INSERT INTO activity_log (timestamp, action, sender, recipient, subject, detail) VALUES (?,?,?,?,?,?)",
            (now_iso(), "system", None, None, None, f"Ecosystem initialized with {len(SEED_CONTACTS)} mailboxes."),
        )
        conn.commit()
    conn.close()


init_db()

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/mailboxes")
def list_mailboxes():
    db = get_db()
    rows = db.execute("SELECT address, display_name, status FROM mailboxes ORDER BY address").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/inbox/<path:address>")
def inbox(address):
    db = get_db()
    exists = db.execute("SELECT 1 FROM mailboxes WHERE address = ?", (address,)).fetchone()
    if not exists:
        return jsonify({"error": f"No mailbox found for {address}"}), 404
    rows = db.execute(
        "SELECT id, sender, recipient, subject, body, created_at, read "
        "FROM messages WHERE recipient = ? ORDER BY created_at DESC",
        (address,),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/sent/<path:address>")
def sent(address):
    db = get_db()
    rows = db.execute(
        "SELECT id, sender, recipient, subject, body, created_at "
        "FROM messages WHERE sender = ? ORDER BY created_at DESC",
        (address,),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/activity")
def activity():
    db = get_db()
    rows = db.execute(
        "SELECT timestamp, action, sender, recipient, subject, detail "
        "FROM activity_log ORDER BY id DESC LIMIT 50"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/send", methods=["POST"])
def send_message():
    payload = request.get_json(force=True, silent=True) or {}
    sender = (payload.get("sender") or "").strip()
    recipient = (payload.get("recipient") or "").strip()
    subject = (payload.get("subject") or "").strip()
    body = (payload.get("body") or "").strip()

    if not sender or not recipient:
        return jsonify({"error": "Both sender and recipient addresses are required."}), 400

    db = get_db()

    sender_exists = db.execute("SELECT 1 FROM mailboxes WHERE address = ?", (sender,)).fetchone()
    if not sender_exists:
        return jsonify({"error": f"Unknown sender mailbox: {sender}"}), 400

    recipient_exists = db.execute("SELECT 1 FROM mailboxes WHERE address = ?", (recipient,)).fetchone()
    if not recipient_exists:
        db.execute(
            "INSERT INTO activity_log (timestamp, action, sender, recipient, subject, detail) VALUES (?,?,?,?,?,?)",
            (now_iso(), "bounce", sender, recipient, subject, f"No such mailbox: {recipient}"),
        )
        db.commit()
        return jsonify({"error": f"Recipient mailbox does not exist: {recipient}"}), 400

    ts = now_iso()
    db.execute(
        "INSERT INTO messages (sender, recipient, subject, body, created_at, read) VALUES (?,?,?,?,?,0)",
        (sender, recipient, subject, body, ts),
    )
    db.execute(
        "INSERT INTO activity_log (timestamp, action, sender, recipient, subject, detail) VALUES (?,?,?,?,?,?)",
        (ts, "delivered", sender, recipient, subject, "Message routed to recipient inbox."),
    )
    db.commit()

    return jsonify({"status": "delivered", "sender": sender, "recipient": recipient, "timestamp": ts})


@app.route("/api/read/<int:message_id>", methods=["POST"])
def mark_read(message_id):
    db = get_db()
    row = db.execute("SELECT sender, recipient, subject FROM messages WHERE id = ?", (message_id,)).fetchone()
    if not row:
        return jsonify({"error": "Message not found"}), 404
    db.execute("UPDATE messages SET read = 1 WHERE id = ?", (message_id,))
    db.execute(
        "INSERT INTO activity_log (timestamp, action, sender, recipient, subject, detail) VALUES (?,?,?,?,?,?)",
        (now_iso(), "read", row["sender"], row["recipient"], row["subject"], "Recipient opened message."),
    )
    db.commit()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8009))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

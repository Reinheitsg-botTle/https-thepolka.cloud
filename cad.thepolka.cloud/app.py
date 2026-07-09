"""
CAD.thepolka.cloud
-------------------
Standalone Flask app -- self-contained, no dependency on the main site's
layout.html or shared templates. Same independent-process pattern as
faire.thepolka.cloud: its own app.py, its own templates/, its own static/.

Run:
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python3 app.py

Serves on port 8004 by default (matches: main=8001, resume-generator=8002,
faire=8003, cad=8004).
"""

from flask import Flask, render_template

app = Flask(__name__)  # uses default ./static and ./templates folders


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def not_found(e):
    return (
        "<div style='font-family:monospace;background:#0c2138;color:#eef3f7;"
        "height:100vh;display:flex;align-items:center;justify-content:center;"
        "flex-direction:column;gap:12px;'>"
        "<h1 style='margin:0;'>404</h1>"
        "<p><a href='/' style='color:#8fd1e8;'>&larr; back to CAD Experience</a></p>"
        "</div>",
        404,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004, debug=True)

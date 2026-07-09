"""
Faire — minimal server
Serves templates/index.html at "/" and static/ at "/static/...",
plus a stub /api/chat endpoint so the widget has something to talk to
until the real local-ai-os backend is wired in.

Run:
    python3 app.py

Requires:
    pip install flask
"""
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    # ---- STUB REPLY ----
    # Replace this block with a call to your real local-ai-os backend
    # (e.g. forward `message` + `history` to Ollama, a local LLM server,
    # or whatever serves the chatbot you mentioned).
    reply = f"(stub) Faire received: {message!r}. Backend not wired up yet."

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)

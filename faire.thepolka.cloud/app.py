"""
Faire — server
Serves templates/index.html at "/", static/ at "/static/...",
and a real chat endpoint at /api/chat.

If OPENAI_API_KEY is set in the environment, Faire calls OpenAI.
Otherwise it falls back to a stub reply so the widget still works
while you wire up a real backend (OpenAI, local-ai-os, Ollama, etc).

Run:
    pip3 install flask openai
    export OPENAI_API_KEY="sk-..."     # optional, omit to use stub mode
    python3 app.py
"""
import os
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, template_folder="templates", static_folder="static")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
FAIRE_SYSTEM_PROMPT = (
    "You are Faire, a warm, concise AI companion that lives as a floating "
    "orb on thepolka.cloud. Keep replies short and conversational unless "
    "asked for more detail."
)

@app.route('/demo')
def demo():
    return render_template('demo.html')

client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        print("openai package not installed — run: pip3 install openai")
        client = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/shared/<path:filename>')
def shared_static(filename):
    root_static = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(root_static, filename)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    history = data.get("history", [])

    if client is not None:
        try:
            messages = [{"role": "system", "content": FAIRE_SYSTEM_PROMPT}]
            # keep last few turns of history for context
            for turn in history[-10:]:
                role = turn.get("role")
                content = turn.get("content")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
            if not history or history[-1].get("content") != message:
                messages.append({"role": "user", "content": message})

            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            reply = completion.choices[0].message.content
        except Exception as e:
            reply = f"Faire hit an error talking to OpenAI: {e}"
    else:
        reply = (
            f"(stub mode — no OPENAI_API_KEY set) You said: {message!r}. "
            "Set OPENAI_API_KEY to make me actually talk."
        )

    return jsonify({"reply": reply})

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)

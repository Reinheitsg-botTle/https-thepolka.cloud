"""
thepolka.cloud — root Flask app
Port: 8001
Run: source .venv/bin/activate && python app.py
"""
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, template_folder="templates", static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=False, use_reloader=False)

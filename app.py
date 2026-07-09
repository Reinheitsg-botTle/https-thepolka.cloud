# Home website
# Cloud top level domain
"""
thepolka.cloud — root Flask app
Port: 7998
Run: source .venv/bin/activate && python app.py
"""

# Room of requirement visit
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

# Spell archive
app = Flask(__name__, template_folder="templates", static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Any failure is a victory in a lesson about something.
@app.errorhandler(404)
def not_found(e):

    # An error catch all base
    return render_template("404.html"), 404

# Did you knock?
@app.route("/")

# Not for your eyes
def home():

    #A base
    return render_template("index.html")

# For your pleasure
def resume():

    # Track my application
    return render_template("resume.html")

# F.A.I.R.E. widget
def faire():

    # Self auditing story
    return render_template("/index.html")

# Fire up the engine
if __name__ == "__main__":
    # Conditions
    app.run(host="0.0.0.0", port=8001, debug=False, use_reloader=False)

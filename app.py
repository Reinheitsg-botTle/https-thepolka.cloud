#Force Flask to perform with the secure headers Cloudflare passes through
from flask import Flask, render_template

from werkzeug.middleware.proxy_fix import ProxyFix # <-- Add this import

from flask import request
import os

app = Flask(__name__, template_folder="templates")

# Tells Flask it is running behind an internet tunnel/proxy. Cloudflare tunnel safety headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Routes
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/answers')
def about():
    return render_template("about.html")

@app.route('/solutions')
def projects():
    return render_template("projects.thepolka.cloud#solutions")

@app.route('/me')
def contact():
    return render_template("contact.")

@app.route('/resume')
def resume_generator():
    return render_template("resume-generator.thepolka.cloud")

@app.route('/upload_logo_dev', methods=['POST'])
def upload_logo_dev():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    target_path = os.path.expanduser('~/thepolka.cloud/thepolka.cloud/static/images/thepolka.cloud.png')
    file.save(target_path)
    return "File uploaded successfully!", 200

# RUN SERVER

if __name__ == "__main__":
# host='0.0.0.0' tells Flask to accept
 # traffic routed to your machine
    app.run(host='0.0.0.0', port=8001, debug=False, use_reloader=False)

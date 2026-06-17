#Force Flask to perform with the secure headers Cloudflare passes through
from flask import Flask,
from werkzeug.middleware.proxy_fix import ProxyFix # <-- Add this import

app = Flask(__name__, template_folder="../shared/templates", static_folder="../static")

# Tells Flask it is running behind an internet tunnel/proxy. Cloudflare tunnel safety headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Routes

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/projects')
def projects():
    return render_template("projects.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/résumé-generator')
def résumé_generator():
    return render_template("résumé.html")

from flask import request
import os

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

"""
resume-generator.thepolka.cloud — Flask backend
Port: 8002
Run: source .venv/bin/activate && python3 app.py
"""
import io
import os
import zipfile
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from resume_generator.normalize import normalize
from resume_generator.renderer.markdown import render_markdown
from resume_generator.renderer.html import render_html
from resume_generator.renderer.pdf import render_pdf
from resume_generator.renderer.docx import render_docx

app = Flask(__name__, template_folder="templates", static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
CORS(app)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/resume-generator", methods=["POST"])
def generate():
    try:
        raw = request.get_json(force=True)
        if not raw:
            return jsonify({"error": "No JSON body received"}), 400

        data = normalize(raw)
        name_slug = (data["name"].replace(" ", "_").replace("/", "-") or "resume")

        md_bytes   = render_markdown(data).encode("utf-8")
        html_bytes = render_html(data).encode("utf-8")
        pdf_bytes  = render_pdf(data)
        docx_bytes = render_docx(data)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{name_slug}_resume.md",   md_bytes)
            zf.writestr(f"{name_slug}_resume.html", html_bytes)
            zf.writestr(f"{name_slug}_resume.pdf",  pdf_bytes)
            zf.writestr(f"{name_slug}_resume.docx", docx_bytes)
        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{name_slug}_resume_bundle.zip",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# GNU nano 8.7.1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       app.py
"""
Resume Generator — Flask backend
Receives JSON from the form, returns a ZIP with .md, .html, .pdf, .docx
"""

import io
import os
import zipfile
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from resume_generator.normalize import normalize

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS

from resume_generator.renderer.markdown import render_markdown
from resume_generator.renderer.html import render_html
from resume_generator.renderer.pdf import render_pdf
from resume_generator.renderer.docx import render_docx

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/resume-generator", methods=["GET"])
def resume_page():
    return render_template("resume-generator.thepolka.cloud/templates/index.html")

@app.route("/api/resume-generator.thepolka.cloud/templates/index.html", methods=["POST"])
def generate():
    """
    Accepts JSON body matching the normalize() schema.
    Returns a ZIP file containing all 4 resume formats.
    """
    try:
        raw = request.get_json(force=True)
        if not raw:
            return jsonify({"error": "No JSON body received"}), 400

        data = normalize(raw)
        name_slug = data["name"].replace(" ", "_").replace("/", "-") or "resume"

        # Build each format in memory
        md_bytes = render_markdown(data).encode("utf-8")
        html_bytes = render_html(data).encode("utf-8")
        pdf_bytes = render_pdf(data)        # returns bytes
        docx_bytes = render_docx(data)      # returns bytes

        # Pack into a ZIP
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


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    app.run(host="0.0.0.0", port=port, debug=False)












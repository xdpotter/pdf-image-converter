import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
from werkzeug.utils import secure_filename

UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)  # allow all origins for now

ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg"}
ALLOWED_PDF_EXT = {"pdf"}

def allowed_filename(filename, allowed):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/pdf-to-jpg", methods=["POST"])
def pdf_to_jpg():
    if "file" not in request.files:
        return jsonify({"error": "no file"}), 400
    f = request.files["file"]
    if f.filename == "" or not allowed_filename(f.filename, ALLOWED_PDF_EXT):
        return jsonify({"error": "invalid file"}), 400

    data = f.read()
    try:
        images = convert_from_bytes(data, dpi=200)
    except Exception as e:
        return jsonify({"error": "conversion failed", "details": str(e)}), 500

    urls = []
    for i, img in enumerate(images, start=1):
        fname = f"{uuid.uuid4().hex}_page_{i}.jpg"
        path = os.path.join(UPLOAD_DIR, fname)
        img.save(path, "JPEG")
        urls.append(f"/uploads/{fname}")
    return jsonify({"images": urls})

@app.route("/ocr", methods=["POST"])
def ocr():
    if "file" not in request.files:
        return jsonify({"error": "no file"}), 400
    f = request.files["file"]
    if f.filename == "" or not allowed_filename(f.filename, ALLOWED_IMAGE_EXT):
        return jsonify({"error": "invalid image file"}), 400

    fname = secure_filename(f.filename)
    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{fname}")
    f.save(path)
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
    except Exception as e:
        return jsonify({"error": "ocr failed", "details": str(e)}), 500
    return jsonify({"text": text})

@app.route("/jpg-to-png", methods=["POST"])
def jpg_to_png():
    if "file" not in request.files:
        return jsonify({"error": "no file"}), 400
    f = request.files["file"]
    if f.filename == "" or not allowed_filename(f.filename, ALLOWED_IMAGE_EXT):
        return jsonify({"error": "invalid image file"}), 400

    fname = secure_filename(f.filename)
    in_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{fname}")
    f.save(in_path)
    base, _ = os.path.splitext(fname)
    out_fname = f"{uuid.uuid4().hex}_{base}.png"
    out_path = os.path.join(UPLOAD_DIR, out_fname)
    try:
        img = Image.open(in_path).convert("RGBA")
        img.save(out_path, "PNG")
    except Exception as e:
        return jsonify({"error": "conversion failed", "details": str(e)}), 500
    return jsonify({"png_url": f"/uploads/{out_fname}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)

from flask import Flask, render_template, request, jsonify
import os
import fitz  # PyMuPDF

app = Flask(__name__)

# =====================
# CONFIG
# =====================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

PDF_TEXT = ""   # global pdf content


# =====================
# HOME PAGE
# =====================
@app.route("/")
def index():
    return render_template("index.html")


# =====================
# HEALTH CHECK (RENDER NEEDS THIS)
# =====================
@app.route("/healthz")
def health():
    return "OK", 200


# =====================
# PDF UPLOAD
# =====================
@app.route("/upload", methods=["POST"])
def upload_pdf():
    global PDF_TEXT
    PDF_TEXT = ""

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files allowed"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Read PDF safely
    try:
        doc = fitz.open(filepath)
        for page in doc:
            PDF_TEXT += page.get_text()
        doc.close()
    except Exception as e:
        return jsonify({"error": f"PDF read failed: {str(e)}"}), 500

    return jsonify({"message": "PDF uploaded and processed successfully"})


# =====================
# CHAT WITH PDF (BASIC AI LOGIC)
# =====================
@app.route("/chat", methods=["POST"])
def chat():
    global PDF_TEXT

    if not PDF_TEXT:
        return jsonify({"answer": "Please upload a PDF first."})

    data = request.get_json()
    question = data.get("question", "").lower()

    if not question:
        return jsonify({"answer": "Please ask a question."})

    # Simple keyword-based answer (safe for deployment)
    if question in PDF_TEXT.lower():
        return jsonify({"answer": "Yes, this topic is mentioned in the PDF."})

    return jsonify({
        "answer": "I could not find an exact answer in the PDF. Please ask another question."
    })


# =====================
# START APP (RENDER SAFE)
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

import os
from flask import Flask, render_template, request
import fitz  # PyMuPDF

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

pdf_text = ""


@app.route("/", methods=["GET", "POST"])
def index():
    global pdf_text
    answer = ""

    if request.method == "POST":

        # PDF upload
        if "pdf" in request.files:
            file = request.files["pdf"]
            if file.filename.endswith(".pdf"):
                path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(path)

                pdf_text = ""
                doc = fitz.open(path)
                for page in doc:
                    pdf_text += page.get_text()

        # Question asked
        if "question" in request.form:
            question = request.form["question"]
            if pdf_text:
                # SIMPLE answer logic (safe for deploy)
                answer = f"PDF ke base par answer:\n\n{pdf_text[:800]}"
            else:
                answer = "Pehle PDF upload karo."

    return render_template("index.html", answer=answer)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

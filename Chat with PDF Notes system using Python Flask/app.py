import os
os.environ["LANGCHAIN_DISABLE_LANGUAGE_PARSERS"] = "true"

from flask import Flask, render_template, request
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
VECTOR_DB = "faiss_index"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# GLOBAL VARIABLE
vectorstore = None

@app.route("/", methods=["GET", "POST"])
def index():
    global vectorstore
    answer = ""

    # ---------- PDF UPLOAD ----------
    if request.method == "POST" and "pdf" in request.files:
        pdf = request.files["pdf"]
        if pdf.filename != "":
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)
            pdf.save(pdf_path)

            # Load PDF
            loader = PyMuPDFLoader(pdf_path)
            pages = loader.load()

            # Split text
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            docs = splitter.split_documents(pages)

            # Embeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

            # Vector store
            vectorstore = FAISS.from_documents(docs, embeddings)
            vectorstore.save_local(VECTOR_DB)

            answer = "✅ PDF uploaded and processed with AI successfully."

    # ---------- QUESTION ----------
    if request.method == "POST" and "question" in request.form:
        question = request.form["question"]

        if vectorstore is None:
            answer = "❌ Please upload a PDF first."
        else:
            docs = vectorstore.similarity_search(question, k=2)
            answer = docs[0].page_content

    return render_template("index.html", answer=answer)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

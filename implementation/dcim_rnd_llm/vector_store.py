import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

PDF_DIR = "/home/infra/rnd_llm/pdf"
DB_PATH = "/home/infra/rnd_llm/faiss_db"

splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100
)

all_chunks = []

for file in os.listdir(PDF_DIR):
    if not file.endswith(".pdf"):
        continue

    loader = PyPDFLoader(os.path.join(PDF_DIR, file))
    docs = loader.load()

    chunks = splitter.split_documents(docs)

    for i, c in enumerate(chunks):
        c.metadata.update({
            "filename": file,
            "chunk_id": i,
            "category": "company_docs"
        })

    all_chunks.extend(chunks)

print(f"Total chunks: {len(all_chunks)}")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_documents(all_chunks, embeddings)

os.makedirs(DB_PATH, exist_ok=True)
db.save_local(DB_PATH)

print("✅ FAISS multi-file DB saved")

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

PDF_DIR = "/home/infra/rnd_llm/pdf"

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
    all_chunks.extend(chunks)

print(f"Total chunks: {len(all_chunks)}")
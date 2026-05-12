from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

DB_PATH = "/home/infra/rnd_llm/faiss_db"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.load_local(
    DB_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

query = "jelaskan apapun tentang vdi yang dikerjakan tim falah?"

docs = db.similarity_search(query, k=3)
context = "\n\n".join(doc.page_content for doc in docs)

prompt = f"""
Kamu adalah AI assistant profesional di bidang infrastruktur dan dokumentasi perusahaan.
Jawab HANYA berdasarkan konteks berikut.
Gunakan Bahasa Indonesia yang formal dan jelas.
Jika informasi tidak tersedia, katakan dengan jujur bahwa data tidak ditemukan.

KONTEKS:
{context}

PERTANYAAN:
{query}

JAWABAN:
"""

llm = OllamaLLM(
    model="gpt-oss:20b",
    temperature=0.2
)

response = llm.invoke(prompt)

print("\n===== JAWABAN =====\n")
print(response)

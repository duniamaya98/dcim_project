from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

# =============================
# INIT APP
# =============================
app = FastAPI(
    title="Internal RAG API",
    description="RAG berbasis FAISS + Mistral 7B (Ollama)",
    version="1.0.0"
)

# =============================
# LOAD EMBEDDING & DB (ONCE)
# =============================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.load_local(
    "/home/infra/rnd_llm/faiss_db",
    embeddings,
    allow_dangerous_deserialization=True
)

llm = OllamaLLM(
    model="gpt-oss:20b",
    temperature=0.05
)

# =============================
# REQUEST MODEL
# =============================
class QueryRequest(BaseModel):
    question: str
    top_k: int = 2

# =============================
# ENDPOINT
# =============================
@app.post("/ask")
def ask_ai(req: QueryRequest):
    docs = db.similarity_search(req.question, k=req.top_k)
    context = "\n\n".join(doc.page_content for doc in docs)
    

    prompt = f"""
Kamu adalah AI assistant internal perusahaan.
ATURAN WAJIB:
- Jawab HANYA berdasarkan konteks
- Gunakan Bahasa Indonesia formal
- Jangan menambah atau menginterpretasi
- Jika tidak ada di konteks, jawab: "Informasi tersebut tidak tercantum dalam dokumen."

KONTEKS:
{context}

PERTANYAAN:
{req.question}

JAWABAN:
"""

    answer = llm.invoke(prompt)

    return {
        "question": req.question,
        "answer": answer
    }
# =============================
# OPENAI COMPATIBLE ENDPOINTS
# =============================

@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "internal-rag-mistral",
                "object": "model",
                "owned_by": "internal"
            }
        ]
    }


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]


@app.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest):
    user_question = req.messages[-1].content

    docs = db.similarity_search(user_question, k=2)
    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
Kamu adalah AI assistant internal perusahaan.
ATURAN WAJIB:
- Jawab HANYA berdasarkan konteks
- Gunakan Bahasa Indonesia formal
- Jangan menambah atau menginterpretasi
- Jika tidak ada di konteks, jawab: "Informasi tersebut tidak tercantum dalam dokumen."

KONTEKS:
{context}

PERTANYAAN:
{user_question}

JAWABAN:
"""

    answer = llm.invoke(prompt)

    return {
        "id": "chatcmpl-internal",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer
                },
                "finish_reason": "stop"
            }
        ]
    }
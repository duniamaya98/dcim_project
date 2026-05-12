import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

class RAGSystem:
    def __init__(self, collection_name: str = "dcim_history"):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.client = QdrantClient(url=self.qdrant_url)
        self.collection_name = collection_name
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize collection if not exists
        try:
            self._ensure_collection()
        except Exception as e:
            print(f"Warning: Could not connect to Qdrant: {e}")

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
        except Exception as e:
            raise ConnectionError(f"Qdrant connection failed: {e}")

    def index_document(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        vector = self.model.encode(text).tolist()
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload={"text": text, **metadata}
                )
            ]
        )

    def search(self, query: str, limit: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        try:
            query_vector = self.model.encode(query).tolist()
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True
            )
            return [res.payload for res in results]
        except Exception as e:
            print(f"Search failed: {e}")
            return []

# API Endpoint for RAG
from fastapi import FastAPI, Depends
app_rag = FastAPI()

@app_rag.post("/rag/query")
async def query_rag(query: str, rag: RAGSystem = Depends(RAGSystem)):
    results = rag.search(query)
    return {"results": results}

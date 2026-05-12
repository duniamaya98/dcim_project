from typing import Optional, List
from pydantic import BaseModel
from dcim_ai.prompting.manager import PromptManager, PromptTemplate
from dcim_ai.rag.engine import RAGSystem
import httpx
import os

class QueryRequest(BaseModel):
    user_query: str
    session_id: Optional[str] = None

class ContextualEngine:
    def __init__(self):
        self.prompt_manager = PromptManager()
        self.rag = RAGSystem()
        self.llm_api_url = os.getenv("LLM_API_URL", "http://localhost:8080/llm/inference")

    async def understand_intent(self, query: str) -> str:
        # Simple rule-based or LLM-based intent extraction
        if "anomaly" in query.lower():
            return "anomaly_explanation"
        if "root cause" in query.lower() or "rca" in query.lower():
            return "rca_reasoning"
        return "general_query"

    async def get_dcim_context(self, intent: str) -> dict:
        # This would interface with the existing DCIM system APIs
        # Mock data for demonstration
        return {
            "anomaly_ratio": 0.92,
            "drift_ratio": 0.15,
            "domain": "Power Distribution",
            "metrics": ["PDU-01 Current", "PDU-02 Voltage"],
            "domain_persistence": "High (persistent for 15 mins)",
            "correlation_score": 0.88,
            "rca_confidence": 0.95
        }

    async def process_query(self, request: QueryRequest):
        intent = await self.understand_intent(request.user_query)
        
        # 1. Retrieve history from RAG
        knowledge = self.rag.search(request.user_query, limit=2)
        knowledge_text = "\n".join([doc["text"] for doc in knowledge])
        
        # 2. Get real-time system context
        sys_context = await self.get_dcim_context(intent)
        
        # 3. Choose prompt and render
        if intent == "anomaly_explanation":
            prompt = self.prompt_manager.render(PromptTemplate.ANOMALY_EXPLANATION, **sys_context)
        elif intent == "rca_reasoning":
            prompt = self.prompt_manager.render(PromptTemplate.RCA_REASONING, 
                                               evidence=f"Historical match: {knowledge_text}", 
                                               **sys_context)
        else:
            prompt = f"User is asking: {request.user_query}\nContext: {knowledge_text}"

        # 4. Call LLM
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.llm_api_url, json={"prompt": prompt})
            resp.raise_for_status()
            result = resp.json()
            
        return {"answer": result["text"], "intent": intent, "context_used": sys_context}

# API for Contextual Query
from fastapi import FastAPI
app_query = FastAPI()
engine = ContextualEngine()

@app_query.post("/dcim/query")
async def dcim_query(request: QueryRequest):
    return await engine.process_query(request)

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dcim-llm-platform")

app = FastAPI(title="DCIM Private LLM Platform API")

# vLLM Server details (assuming it runs on port 8000 internally)
VLLM_API_URL = os.getenv("VLLM_API_URL", "http://localhost:8000/v1")

class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.2
    top_p: float = 0.95

class InferenceResponse(BaseModel):
    text: str
    usage: dict

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/llm/inference")
async def inference(request: InferenceRequest):
    """
    Unified inference endpoint for DCIM AI components.
    Proxies requests to the internal vLLM instance with Llama-3-8B-AWQ.
    """
    logger.info(f"Received inference request: {request.prompt[:50]}...")
    
    payload = {
        "model": "casperhansen/llama-3-8b-instruct-awq",
        "messages": [{"role": "user", "content": request.prompt}],
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(f"{VLLM_API_URL}/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            
            result = data["choices"][0]["message"]["content"]
            usage = data["usage"]
            
            logger.info("Inference successful")
            return InferenceResponse(text=result, usage=usage)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"vLLM server error: {e}")
            raise HTTPException(status_code=500, detail="Inference engine error")
        except Exception as e:
            logger.error(f"Internal error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

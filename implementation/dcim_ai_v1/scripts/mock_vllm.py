from fastapi import FastAPI, Request
import uvicorn
import json

app = FastAPI()

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    data = await request.json()
    print(f"Received request for model: {data.get('model')}")
    
    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "This is a MOCK LLM response for DCIM analysis. The system suggests checking the PDU capacity as requested."
            }
        }],
        "usage": {"total_tokens": 42}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

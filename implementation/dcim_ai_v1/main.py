from fastapi import FastAPI
import logging
import uvicorn
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dcim-platform")

# Mock RAG if database is missing
try:
    from dcim_ai.query_engine.server import engine, QueryRequest
    from dcim_ai.simulation.engine import sim_engine, SimulationConfig
except Exception as e:
    logger.error(f"Startup error: {e}")
    raise

app = FastAPI(title="DCIM AI Platform Consolidated API")

@app.post("/dcim/query")
async def dcim_query(request: QueryRequest):
    try:
        return await engine.process_query(request)
    except Exception as e:
        logger.error(f"Query error: {e}")
        return {"error": "Query engine failed (is Qdrant running?)", "details": str(e)}

@app.post("/simulation/run")
async def run_simulation(config: SimulationConfig):
    return await sim_engine.run_simulation(config)

if __name__ == "__main__":
    os.environ["LLM_API_URL"] = "http://localhost:8080/llm/inference"
    uvicorn.run(app, host="0.0.0.0", port=8090)

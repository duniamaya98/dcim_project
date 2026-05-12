import numpy as np
from typing import Dict, List, Any
from pydantic import BaseModel
import httpx
import os

class SimulationConfig(BaseModel):
    scenario: str  # e.g., "cooling_failure", "pdu_overload"
    severity: float # 0.0 to 1.0
    duration_minutes: int = 30

class WhatIfEngine:
    def __init__(self):
        self.llm_api_url = os.getenv("LLM_API_URL", "http://localhost:8080/llm/inference")

    def generate_synthetic_metrics(self, config: SimulationConfig) -> Dict[str, List[float]]:
        # Simulate data center metrics based on scenario
        # Example: if cooling_failure, temp rises linearly
        time_steps = config.duration_minutes
        if config.scenario == "cooling_failure":
            base_temp = 22.0
            noise = np.random.normal(0, 0.5, time_steps)
            trend = np.linspace(0, 15 * config.severity, time_steps)
            return {"temperature": (base_temp + trend + noise).tolist()}
        
        return {"general_metric": np.random.normal(50, 5, time_steps).tolist()}

    async def run_simulation(self, config: SimulationConfig):
        # 1. Generate data
        data = self.generate_synthetic_metrics(config)
        
        # 2. Compute predicted impacts (mock logic for pipeline)
        anomaly_ratio = min(1.0, config.severity * 1.5)
        escalation_risk = "High" if config.severity > 0.7 else "Low"
        
        # 3. LLM Explanation of Impact
        prompt = f"""
        Simulation Scenario: {config.scenario}
        Severity: {config.severity}
        Resulting Anomaly Ratio: {anomaly_ratio}
        Escalation Risk: {escalation_risk}
        
        Analyze this simulation and explain:
        1. Potential cascades in the infrastructure.
        2. Mitigation steps to prevent this from becoming a critical incident.
        3. Which domains are most at risk.
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.llm_api_url, json={"prompt": prompt})
            resp.raise_for_status()
            llm_analysis = resp.json()["text"]
            
        return {
            "scenario": config.scenario,
            "predicted_metrics": data,
            "analysis": llm_analysis,
            "risk_assessment": {
                "anomaly_ratio": anomaly_ratio,
                "escalation_risk": escalation_risk
            }
        }

from fastapi import FastAPI
app_sim = FastAPI()
sim_engine = WhatIfEngine()

@app_sim.post("/simulation/run")
async def run_simulation(config: SimulationConfig):
    return await sim_engine.run_simulation(config)

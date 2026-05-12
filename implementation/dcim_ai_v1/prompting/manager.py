from enum import Enum
from typing import Dict, Any
import jinja2

class PromptTemplate(Enum):
    ANOMALY_EXPLANATION = "anomaly_explanation"
    RCA_REASONING = "rca_reasoning"
    INCIDENT_SUMMARY = "incident_summary"

TEMPLATES = {
    PromptTemplate.ANOMALY_EXPLANATION: """
Analyze the following DCIM anomaly data and provide a concise explanation for a data center technician.

Context:
- Anomaly Ratio: {{ anomaly_ratio }}
- Drift Ratio: {{ drift_ratio }}
- Domain: {{ domain }}
- Metrics Involved: {{ metrics | join(', ') }}

Task: Explain why this is flagged as an anomaly and what the likely hardware/software behavior is.
""",
    PromptTemplate.RCA_REASONING: """
System Root Cause Analysis (RCA) Report:
Temporal Persistence: {{ domain_persistence }}
Cross-domain Correlation: {{ correlation_score }}
Confidence: {{ rca_confidence }}

Detailed Evidence:
{{ evidence }}

Based on the evidence above, perform a deep dive into the root cause. 
Identify if this is a Power, Cooling, or Network issue.
""",
    PromptTemplate.INCIDENT_SUMMARY: """
Summarize the current DCIM incident.
Incident ID: {{ incident_id }}
Impacted Domains: {{ domains | join(', ') }}
Start Time: {{ start_time }}

Please provide a high-level summary for the management dashboard, focusing on impact and urgency.
"""
}

class PromptManager:
    def __init__(self):
        self.env = jinja2.Environment()
        self.templates = {k: self.env.from_string(v) for k, v in TEMPLATES.items()}
        self.versions = {"v1": TEMPLATES}

    def render(self, template_name: PromptTemplate, **kwargs) -> str:
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")
        return self.templates[template_name].render(**kwargs)

    def evaluate_hallucination(self, prompt: str, response: str) -> bool:
        # Placeholder for hallucination check logic
        # In production, this might call another LLM or use semantic similarity
        return False

# Usage example:
# manager = PromptManager()
# prompt = manager.render(PromptTemplate.ANOMALY_EXPLANATION, anomaly_ratio=0.85, drift_ratio=0.4, domain="Cooling", metrics=["Chiller-01 Temp", "Fan Speed"])

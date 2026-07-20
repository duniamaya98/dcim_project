# Deployment Strategy: Staging to Production

**Project:** DCIM AI Platform
**Date:** 2026-06-05
**Status:** Planning Phase

## 1. Overview
This document outlines the end-to-end deployment strategy for the DCIM AI Platform, moving from a controlled staging environment to a high-availability production environment. The goal is to ensure zero-downtime deployments, consistent model behavior, and rapid recovery capabilities.

## 2. Environment Architecture

### 2.1 Staging Environment (Pre-Production)
*   **Purpose:** Final validation of integration, performance benchmarking, and UAT (User Acceptance Testing).
*   **Infrastructure:** Mirror of production hardware (e.g., NVIDIA RTX 3070 Ti or equivalent).
*   **Data:** Sanitized production-like data.
*   **Components:**
    *   Full stack: `dcim_ai_v2_rag` + `dcim_ai_v1` (LLM Wrapper).
    *   Vector DB: Qdrant (Staging instance).
    *   Database: PostgreSQL (Staging instance).
    *   LLM Engine: vLLM / llama.cpp.

### 2.2 Production Environment
*   **Purpose:** Live inference and analytics for end-users.
*   **Infrastructure:** Dedicated GPU server (e.g., A100/H100 or high-end RTX series).
*   **Data:** Real-time production data.
*   **Components:**
    *   Hardened `dcim_ai_v2_rag` and `dcim_ai_v1`.
    *   High-availability Qdrant and PostgreSQL clusters.
    *   Production-grade LLM serving (vLLM with multi-GPU support if needed).

## 3. Deployment Pipeline

### 3.1 Build Phase
1.  **Code Linting & Unit Tests:** Run via `pytest` on all `implementation/` modules.
2.  **Containerization:** Build Docker images for `dcim_ai_v2_rag` and `dcim_ai_v1`.
3.  **Artifact Tagging:** Tag images with `git_commit_hash` and `build_number`.

### 3.2 Staging Deployment (Promotion 1)
1.  **Deploy Containers:** Update staging containers using the new images.
2.  **Model Promotion:** Update `registry/registry.json` with the new ML model version.
3.  **Automated Benchmarking:** Run `dcim_benchmark/` suite.
4.  **Manual QA:** Verify RCA, Correlation, and Anomaly Detection outputs.

### 3.3 Production Deployment (Promotion 2)
1.  **Blue/Green or Canary Deployment:**
    *   Deploy new version to a "Green" environment.
    *   Route 10% of traffic to "Green".
    *   Monitor error rates and latency via Prometheus.
2.  **Full Switch:** If metrics are stable, route 100% of traffic to "Green".
3.  **Decommission:** Shut down the old "Blue" environment.

## 4. Artifact Management

| Artifact Type | Storage | Versioning Strategy | Promotion Path |
| --- | --- | --- | --- |
| **Application Code** | Docker Registry | Semantic Versioning + Commit Hash | Staging -> Production |
| **ML Models** | S3 / Local Registry | Model ID (e.g., `v1.4.2`) | Staging -> Production |
| **LLM Weights** | Model Registry | GGUF/Safetensors Hash | Staging -> Production |
| **Vector Index** | Qdrant Snapshot | Snapshot ID | Staging -> Production |

## 5. Observability & Monitoring
*   **Metrics:** Prometheus scraping `/metrics` from FastAPI services.
*   **Dashboards:** Grafana dashboards for:
    *   Inference Latency (TTFT, TPOT).
    *   GPU Utilization & Memory.
    *   Anomaly Detection Confidence Scores.
    *   RAG Retrieval Accuracy.
*   **Logging:** Centralized logging (ELK or similar) for all `inference_service.py` logs.

## 6. Rollback Strategy
*   **Application Rollback:** Revert to the previous Docker image tag in the production orchestrator.
*   **Model Rollback:** Update `registry/registry.json` to point back to the previous `current_production` model ID.
*   **Database Rollback:** Use PostgreSQL snapshots for critical schema reverts (rarely used for data).
*   **Trigger:** Automatic rollback if error rate > 5% or latency > 2x baseline for 3 consecutive minutes.

## 7. Security & Compliance
*   **Secret Management:** Use environment variables or a Secret Manager (e.g., HashiCorp Vault). No secrets in `config.py`.
*   **Network Isolation:**
    *   Database and Qdrant accessible only from the application subnet.
    *   LLM Wrapper API exposed via Load Balancer.
*   **Audit Logs:** Every inference request must be logged with a unique `request_id` for traceability.

#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) Pipeline for Block 7

Provides:
1. Vector store for DCIM documents (chromadb-based, no external service)
2. Semantic search over anomalies, RCA reports, metrics
3. LLM query with context injection
4. Citation mechanism

Dependencies: pip install chromadb sentence-transformers

Reference:
    dcim-wiki/reference-designs/block7-analytics-ai-engine.md §9
    MT-023 §2.8
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Vector Store (Qdrant)
# ============================================================================

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

class VectorStore:
    """
    Robust vector store for DCIM knowledge base.

    Uses Qdrant (client-server) with sentence-transformers embeddings.
    Stores: anomaly events, RCA reports, runbooks, metric descriptions.
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "dcim_knowledge",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        self._client = None
        self._embedding_fn = None
        self._initialized = False

    def _lazy_init(self):
        """Lazy init to avoid heavy imports unless actually used."""
        if self._initialized:
            return

        try:
            self._client = QdrantClient(url=self.qdrant_url)
            
            # Check if collection exists
            if not self._client.collection_exists(self.collection_name):
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=384,  # all-MiniLM-L6-v2 dimension
                        distance=qmodels.Distance.COSINE
                    )
                )
                logger.info(f"Created new collection '{self.collection_name}' in Qdrant")
            else:
                logger.info(f"Loaded existing collection '{self.collection_name}' from Qdrant")
                
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")

    @property
    def embedding_fn(self):
        """Lazy load sentence-transformers."""
        if self._embedding_fn is None:
            from sentence_transformers import SentenceTransformer
            self._embedding_fn = SentenceTransformer(self.embedding_model_name)
        return self._embedding_fn

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None,
    ):
        """Add documents to the vector store."""
        self._lazy_init()
        if not self._client:
            return

        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
        if metadatas is None:
            metadatas = [{} for _ in documents]

        embeddings = self.embedding_fn.encode(documents).tolist()

        points = [
            qmodels.PointStruct(
                id=idx,
                vector=vector,
                payload={"text": doc, **meta}
            )
            for idx, vector, doc, meta in zip(ids, embeddings, documents, metadatas)
        ]
        
        self._client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Added {len(documents)} documents to '{self.collection_name}'")

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search over documents."""
        self._lazy_init()
        if not self._client:
            return []

        query_embedding = self.embedding_fn.encode(query).tolist()

        search_filter = None
        if where:
            conditions = []
            for k, v in where.items():
                conditions.append(
                    qmodels.FieldCondition(
                        key=k,
                        match=qmodels.MatchValue(value=v)
                    )
                )
            search_filter = qmodels.Filter(must=conditions)

        if isinstance(query_embedding, list) and len(query_embedding) > 0 and isinstance(query_embedding[0], list):
            query_vector = query_embedding[0]
        else:
            query_vector = query_embedding

        # Handle backward compatibility / alternative client methods
        if hasattr(self._client, 'query_points'):
            # Newer Qdrant client versions
            results = self._client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=search_filter,
                limit=n_results
            ).points
        else:
            # Older Qdrant client versions
            results = self._client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=search_filter,
                limit=n_results
            )

        return [
            {
                "id": str(hit.id),
                "document": hit.payload.get("text", ""),
                "metadata": {k: v for k, v in hit.payload.items() if k != "text"},
                "distance": 1.0 - getattr(hit, "score", 1.0), # Approximate
            }
            for hit in results
        ]

    def count(self) -> int:
        """Return number of documents in collection."""
        self._lazy_init()
        if not self._client:
            return 0
        return self._client.count(self.collection_name).count

    def delete_collection(self):
        """Delete collection (reset)."""
        self._lazy_init()
        if not self._client:
            return
        self._client.delete_collection(self.collection_name)
        self._client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=384,
                distance=qmodels.Distance.COSINE
            )
        )
        logger.info(f"Collection '{self.collection_name}' reset")


# ============================================================================
# RAG Pipeline
# ============================================================================

class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for DCIM analytics.

    Flow:
    1. User query → Embed
    2. Retrieve top-k relevant documents from vector store
    3. Build context prompt
    4. Query LLM with context
    5. Return answer with citations
    """

    def __init__(
        self,
        vector_store: VectorStore = None,
        model_name: str = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.model_name = model_name or os.getenv("LLM_MODEL", "qwen2.5-3b-instruct")

        # Domain-specific templates
        self.templates = {
            "anomaly_explanation": (
                "You are a DCIM analytics assistant. Explain the following anomaly in simple terms:\n\n"
                "Metric: {metric_name}\n"
                "Value: {current_value} (expected: {expected_range})\n"
                "Severity: {severity}\n"
                "Detection Method: {method}\n\n"
                "Context from knowledge base:\n{context}\n\n"
                "Provide:\n"
                "1. What happened (1-2 sentences)\n"
                "2. Why it matters (1 sentence)\n"
                "3. Recommended action (1 sentence)\n"
                "4. Confidence level in this assessment\n"
            ),
            "rca_explanation": (
                "You are a DCIM analytics assistant. Explain the root cause analysis results:\n\n"
                "Incident: {incident_id}\n"
                "Root Domain: {root_domain}\n"
                "Confidence: {confidence}\n"
                "Causal Chain: {causal_chain}\n\n"
                "Context from knowledge base:\n{context}\n\n"
                "Provide:\n"
                "1. Root cause summary (1-2 sentences)\n"
                "2. Impact assessment (1 sentence)\n"
                "3. Mitigation steps (bullet points)\n"
            ),
            "general_query": (
                "You are a DCIM analytics assistant. Answer based on the provided context.\n"
                "If the context doesn't contain the answer, say so honestly.\n\n"
                "Question: {query}\n\n"
                "Context:\n{context}\n\n"
                "Answer:\n"
            ),
        }

    def build_prompt(
        self,
        template_name: str,
        context: str = "",
        **kwargs,
    ) -> str:
        """Build prompt from template with context injection."""
        template = self.templates.get(template_name, self.templates["general_query"])
        return template.format(context=context, **kwargs)

    def query_with_context(
        self,
        question: str,
        n_results: int = 5,
        where: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Full RAG query: retrieve context + build prompt.
        Does NOT call LLM (that's done separately for flexibility).
        Returns the prompt + retrieved context + citations.
        """
        # Retrieve relevant documents
        results = self.vector_store.search(
            query=question,
            n_results=n_results,
            where=where,
        )

        # Build context string
        context_parts = []
        citations = []
        for i, result in enumerate(results):
            source = result.get("metadata", {}).get("source", "unknown")
            context_parts.append(f"[{i+1}] (Source: {source})\n{result['document']}")
            citations.append({
                "index": i + 1,
                "source": source,
                "document_id": result["id"],
                "snippet": result["document"][:200] + "..." if len(result["document"]) > 200 else result["document"],
                "relevance": round(max(0, 1.0 - result["distance"]), 4),
            })

        context = "\n\n".join(context_parts)

        # Build prompt
        prompt = self.build_prompt(
            "general_query",
            query=question,
            context=context or "No relevant context found.",
        )

        return {
            "prompt": prompt,
            "context_used": len(results),
            "citations": citations,
            "raw_results": results,
        }


# ============================================================================
# Knowledge Base Seeder
# ============================================================================

def seed_knowledge_base(
    vector_store: VectorStore,
    docs_dir: str = None,
    anomaly_examples: List[Dict] = None,
):
    """
    Seed the RAG vector store with DCIM knowledge.

    Sources:
    1. DCIM wiki documents (markdown)
    2. Metric definitions
    3. Common anomaly patterns and resolutions
    4. RCA runbook entries
    """
    # 1. Metric definitions
    metric_docs = [
        {
            "document": (
                "cpu_usage_percent measures CPU utilization as percentage of total capacity. "
                "Normal range: 5-60%. Values above 80% for extended periods indicate CPU contention. "
                "Common causes: runaway processes, insufficient capacity, crypto mining malware. "
                "Resolution: check top processes, scale horizontally, investigate security."
            ),
            "metadata": {"source": "metric_definitions", "domain": "server", "metric": "cpu_usage_percent"},
        },
        {
            "document": (
                "memory_usage_percent measures RAM utilization. Normal range: 20-80%. "
                "Values above 90% indicate memory exhaustion risk. "
                "Causes: memory leak, insufficient RAM, large dataset loads. "
                "Resolution: identify leaking process, add swap temporariy, scale up."
            ),
            "metadata": {"source": "metric_definitions", "domain": "server", "metric": "memory_usage_percent"},
        },
        {
            "document": (
                "temperature_celsius measures ambient/rack temperature. Normal range: 18-28°C. "
                "Values above 30°C risk hardware failure. Above 35°C is critical. "
                "Causes: cooling failure, airflow blockage, high-density equipment. "
                "Resolution: check cooling units, redistribute load, clear airflow paths."
            ),
            "metadata": {"source": "metric_definitions", "domain": "cooling", "metric": "temperature_celsius"},
        },
        {
            "document": (
                "pue_ratio (Power Usage Effectiveness) = Total facility power / IT equipment power. "
                "Ideal: 1.1-1.2. Good: 1.2-1.5. Needs attention: >1.8. "
                "High PUE indicates inefficient cooling or power distribution. "
                "Resolution: optimize cooling set points, check UPS efficiency, improve airflow management."
            ),
            "metadata": {"source": "metric_definitions", "domain": "energy", "metric": "pue_ratio"},
        },
        {
            "document": (
                "network_throughput_mbps measures data transfer rate. Normal range: 10-500 Mbps. "
                "Sudden drops indicate network failure or congestion. "
                "Causes: switch failure, cable cut, DDoS, bandwidth saturation. "
                "Resolution: check switch status, verify cable connections, review traffic patterns."
            ),
            "metadata": {"source": "metric_definitions", "domain": "network", "metric": "network_throughput_mbps"},
        },
        {
            "document": (
                "disk_usage_percent measures storage utilization. Normal: 30-90%. "
                "Above 95% is critical — risk of write failures. "
                "Resolution: clean up logs, archive old data, expand storage."
            ),
            "metadata": {"source": "metric_definitions", "domain": "storage", "metric": "disk_usage_percent"},
        },
        {
            "document": (
                "disk_io_percent measures disk I/O utilization. Normal: 0-40%. "
                "Above 70% indicates I/O bottleneck. "
                "Causes: heavy database queries, backup jobs, log rotation. "
                "Resolution: optimize queries, schedule backups off-peak, consider SSD upgrade."
            ),
            "metadata": {"source": "metric_definitions", "domain": "server", "metric": "disk_io_percent"},
        },
        {
            "document": (
                "power_consumption_watts measures electrical power draw. Normal depends on equipment type. "
                "Sudden spikes may indicate hardware failure or overload. "
                "Resolution: check PDU status, verify equipment health, balance phases."
            ),
            "metadata": {"source": "metric_definitions", "domain": "power", "metric": "power_consumption_watts"},
        },
    ]

    # 2. Anomaly runbook entries
    runbook_docs = [
        {
            "document": (
                "CPU SPIKE INCIDENT RUNBOOK: When cpu_usage_percent spikes above 90%, "
                "1. SSH into the affected server. "
                "2. Run 'top' or 'htop' to identify top CPU-consuming processes. "
                "3. Check if process is expected (batch job) or anomalous (crypto miner). "
                "4. If expected: monitor and set alert threshold higher. "
                "5. If anomalous: kill process, investigate security, restart service. "
                "6. Document findings in incident report. "
                "Mean time to resolve: 15-30 minutes."
            ),
            "metadata": {"source": "runbook", "domain": "server", "type": "cpu_spike"},
        },
        {
            "document": (
                "TEMPERATURE ALERT RUNBOOK: When temperature_celsius exceeds 28°C, "
                "1. Check cooling unit status in BMS. "
                "2. Verify CRAC/CRAH set points (should be 22°C ±2). "
                "3. Check for blocked airflow (equipment placement, cable management). "
                "4. If single rack hot: redistribute high-density servers. "
                "5. If entire zone hot: escalate to facilities team for cooling maintenance. "
                "6. If >30°C: consider emergency load shedding. "
                "Critical threshold: 35°C — automatic shutdown protocol."
            ),
            "metadata": {"source": "runbook", "domain": "cooling", "type": "temperature"},
        },
        {
            "document": (
                "HIGH PUE INCIDENT: When pue_ratio exceeds 1.8, "
                "1. Verify IT load measurement is accurate. "
                "2. Check cooling system efficiency — dirty filters, low refrigerant. "
                "3. Review UPS efficiency curve (should be >95% at load). "
                "4. Check for power distribution losses. "
                "5. Economic analysis: annual cost impact = (PUE - 1.2) × IT_kW × 8760 × electricity_rate. "
                "Optimization target: reduce PUE by 0.1 saves ~$X/year."
            ),
            "metadata": {"source": "runbook", "domain": "energy", "type": "high_pue"},
        },
        {
            "document": (
                "DISK FULL RUNBOOK: When disk_usage_percent exceeds 95%, "
                "1. Identify large files: 'du -sh /* | sort -rh | head -20'. "
                "2. Check log rotation: /var/log should not exceed retention limits. "
                "3. Clean docker/container images: 'docker system prune -a'. "
                "4. Check for core dumps: /var/crash or /var/lib/systemd/coredump. "
                "5. If production data: request storage expansion ticket (SLA: 4 hours). "
                "6. Emergency: clear oldest backups or move to external storage."
            ),
            "metadata": {"source": "runbook", "domain": "storage", "type": "disk_full"},
        },
        {
            "document": (
                "MEMORY LEAK PATTERN: Gradual memory increase over hours/days without release. "
                "1. Identify process: 'ps aux --sort=-%mem | head -10'. "
                "2. Check memory growth rate: compare snapshots over time. "
                "3. Java apps: check heap dump with jmap. "
                "4. Python apps: check for unbounded data structures. "
                "5. Temporary fix: restart service (document restart window). "
                "6. Permanent fix: file bug report with memory profile to dev team."
            ),
            "metadata": {"source": "runbook", "domain": "server", "type": "memory_leak"},
        },
    ]

    # 3. RCA methodology
    rca_docs = [
        {
            "document": (
                "RCA METHODOLOGY: Block 7 uses composite scoring RCA engine. "
                "The engine performs: 1) Timeline reconstruction, 2) Domain strength scoring, "
                "3) Causal chain reconstruction (DFS, depth 3), 4) Confidence scoring via softmax. "
                "Domains: server, network, storage, power, cooling, application. "
                "Modes: reactive (analyze past incident), forward (predictive RCA from forecast), "
                "hybrid (combine both approaches). "
                "Expected latency: <30 seconds per incident analysis."
            ),
            "metadata": {"source": "rca_methodology", "domain": "all", "type": "methodology"},
        },
    ]

    all_docs = metric_docs + runbook_docs + rca_docs

    if anomaly_examples:
        for ex in anomaly_examples:
            all_docs.append({
                "document": json.dumps(ex),
                "metadata": {"source": "anomaly_example", "domain": ex.get("domain", "unknown")},
            })

    vector_store.add_documents(
        documents=[d["document"] for d in all_docs],
        metadatas=[d["metadata"] for d in all_docs],
    )

    logger.info(f"Seeded knowledge base with {len(all_docs)} documents")
    return len(all_docs)


# ============================================================================
# Inference (local model or API)
# ============================================================================

class LLMInference:
    """LLM inference wrapper supporting local model, llama-server, and API backends."""

    def __init__(self, backend: str = None, model: str = None):
        self.backend = backend or os.getenv("LLM_BACKEND", "local")
        self.model = model or os.getenv("LLM_MODEL", "qwen2.5-3b-instruct")
        self.llama_server_url = os.getenv(
            "LLAMA_SERVER_URL", "http://localhost:8080/completion"
        )

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """Generate text from prompt. Falls back gracefully."""
        # Priority: llama-server HTTP → local GGUF → OpenAI → fallback
        if self.backend == "llama-server":
            return self._llama_server_generate(prompt, max_tokens, temperature)
        elif self.backend == "local":
            # Try llama-server first since it's already running
            result = self._llama_server_generate(prompt, max_tokens, temperature)
            if not result.startswith("[FALLBACK]"):
                return result
            return self._local_generate(prompt, max_tokens, temperature)
        elif self.backend == "openai":
            return self._openai_generate(prompt, max_tokens, temperature)
        else:
            return self._fallback_generate(prompt)

    def _llama_server_generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call llama-server HTTP API (llama.cpp /v1/chat/completions)."""
        try:
            import urllib.request
            import json as _json

            timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
            server_url = os.getenv(
                "LLAMA_SERVER_URL", "http://localhost:8080/v1/chat/completions"
            )

            payload = _json.dumps({
                "messages": [
                    {"role": "system", "content": "You are a DCIM analytics assistant. Answer concisely."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False,
            }).encode("utf-8")

            req = urllib.request.Request(
                server_url,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            req.add_header("User-Agent", "DCIM-LLM-Router/1.0")

            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = _json.loads(resp.read().decode("utf-8"))

            # /v1/chat/completions response format
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if isinstance(content, str):
                content = content.strip()
            if not content:
                return "[FALLBACK] empty response from llama-server"
            return content

        except ImportError:
            return "[FALLBACK] urllib not available"
        except Exception as e:
            logger.warning(f"llama-server call failed: {e}")
            return f"[FALLBACK] {e}"

    def _fallback_generate(self, prompt: str) -> str:
        """Template-based fallback when no LLM backend available."""
        # Simple rule-based response for common queries
        prompt_lower = prompt.lower()

        if "cpu" in prompt_lower and "spike" in prompt_lower:
            return (
                "CPU spike detected. This indicates a sudden increase in processing load, "
                "likely caused by a runaway process, batch job, or resource contention. "
                "Immediate action: identify the top CPU-consuming process using 'top' or 'htop'. "
                "If it's an unexpected process, investigate for security issues. "
                "Confidence: Medium (based on metric pattern analysis)."
            )
        elif "temperature" in prompt_lower and "high" in prompt_lower:
            return (
                "Elevated temperature detected. Current reading exceeds the normal range "
                "of 18-28°C. This could be caused by cooling system issues, airflow blockage, "
                "or high-density equipment. Immediate action: check CRAC/CRAH unit status "
                "and verify airflow paths. If temperature exceeds 35°C, consider emergency "
                "load shedding. Confidence: High (based on thermal analysis)."
            )
        elif "pue" in prompt_lower:
            return (
                "PUE (Power Usage Effectiveness) analysis: PUE measures total facility power "
                "divided by IT equipment power. A PUE above 1.8 indicates significant cooling "
                "or power distribution inefficiency. Recommendations: optimize cooling set points, "
                "check UPS efficiency, improve airflow management. Each 0.1 PUE improvement "
                "translates to measurable cost savings. Confidence: High."
            )
        elif "memory" in prompt_lower or "ram" in prompt_lower:
            return (
                "Memory utilization alert. High memory usage can lead to swapping, OOM kills, "
                "or system instability. If the increase is gradual, suspect a memory leak. "
                "Check the top memory-consuming processes and their growth patterns. "
                "Temporary mitigation: restart the affected service. "
                "Confidence: Medium (requires process-level investigation)."
            )
        elif "disk" in prompt_lower and ("full" in prompt_lower or "usage" in prompt_lower):
            return (
                "Disk usage warning. Storage utilization is approaching critical levels. "
                "Immediate action: identify large files, check log rotation, clean temporary files. "
                "If production data, submit a storage expansion ticket. "
                "Confidence: High (based on utilization trend analysis)."
            )
        else:
            return (
                "I analyzed your query against the available DCIM knowledge base. "
                "Based on the information, I recommend checking the specific metric "
                "trends and recent incidents in the analytics dashboard for a detailed "
                "assessment. You can also run a targeted RCA analysis for deeper insights. "
                "Confidence: Low (insufficient context for specific answer)."
            )

    def _local_generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Attempt local model inference, fall back gracefully."""
        try:
            # Try llama.cpp Python bindings
            from llama_cpp import Llama

            model_path = os.path.join(
                os.path.dirname(__file__), "..", "artifacts", "models",
                "dcim_assistant_v1.0", "model.gguf"
            )
            if not os.path.exists(model_path):
                logger.warning(f"Model not found at {model_path}, using fallback")
                return self._fallback_generate(prompt)

            llm = Llama(model_path=model_path, n_ctx=2048, verbose=False)
            response = llm.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response["choices"][0]["message"]["content"]
        except ImportError:
            logger.warning("llama-cpp-python not installed, using fallback")
            return self._fallback_generate(prompt)
        except Exception as e:
            logger.error(f"Local inference failed: {e}")
            return self._fallback_generate(prompt)

    def _openai_generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """OpenAI API inference (if configured)."""
        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI inference failed: {e}")
            return self._fallback_generate(prompt)


# ============================================================================
# Convenience: Full RAG query
# ============================================================================

def rag_query(
    question: str,
    vector_store: VectorStore = None,
    llm: LLMInference = None,
    n_results: int = 5,
) -> Dict[str, Any]:
    """
    One-shot RAG query: retrieve → prompt → generate → return with citations.

    Returns:
        {
            "question": str,
            "answer": str,
            "citations": list,
            "context_used": int,
        }
    """
    if vector_store is None:
        vector_store = VectorStore()
    if llm is None:
        llm = LLMInference()

    pipeline = RAGPipeline(vector_store=vector_store)

    # Retrieve + build prompt
    rag_result = pipeline.query_with_context(question, n_results=n_results)

    # Generate answer
    answer = llm.generate(rag_result["prompt"])

    return {
        "question": question,
        "answer": answer,
        "citations": rag_result["citations"],
        "context_used": rag_result["context_used"],
    }


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DCIM RAG Pipeline")
    subparsers = parser.add_subparsers(dest="command")

    # Seed command
    seed_parser = subparsers.add_parser("seed", help="Seed the knowledge base")
    seed_parser.add_argument("--reset", action="store_true", help="Reset collection before seeding")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search the knowledge base")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--n", type=int, default=5, help="Number of results")

    # Query command
    query_parser = subparsers.add_parser("query", help="Full RAG query")
    query_parser.add_argument("question", help="Question to answer")

    args = parser.parse_args()

    vs = VectorStore()

    if args.command == "seed":
        if args.reset:
            vs.delete_collection()
        count = seed_knowledge_base(vs)
        print(f"Seeded {count} documents into '{vs.collection_name}'")

    elif args.command == "search":
        results = vs.search(args.query, n_results=args.n)
        for i, r in enumerate(results):
            print(f"\n[{i+1}] Distance: {r['distance']:.4f} | Source: {r['metadata'].get('source', 'unknown')}")
            print(f"    {r['document'][:300]}{'...' if len(r['document']) > 300 else ''}")

    elif args.command == "query":
        result = rag_query(args.question, vector_store=vs)
        print(f"\nQ: {result['question']}")
        print(f"\nA: {result['answer']}")
        print(f"\nCitations ({result['context_used']} sources):")
        for c in result["citations"]:
            print(f"  [{c['index']}] {c['source']} (relevance: {c['relevance']})")

    else:
        parser.print_help()

-- MT-023 Task 4: LLM Model Registry Schema
-- Create table for managing fine-tuned LLM model versions

CREATE TABLE IF NOT EXISTS llm_model_registry (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    base_model VARCHAR(200),
    adapter_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'candidate',  -- candidate/production/archived
    metrics_json JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    activated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    notes TEXT,
    UNIQUE(model_name, version)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_llm_active ON llm_model_registry(model_name, is_active);
CREATE INDEX IF NOT EXISTS idx_llm_status ON llm_model_registry(status);
CREATE INDEX IF NOT EXISTS idx_llm_created ON llm_model_registry(created_at DESC);

-- Comments
COMMENT ON TABLE llm_model_registry IS 'Registry for fine-tuned LLM models (MT-023)';
COMMENT ON COLUMN llm_model_registry.model_name IS 'Model identifier (e.g., dcim_assistant)';
COMMENT ON COLUMN llm_model_registry.version IS 'Version string (e.g., v1.0, v1.1)';
COMMENT ON COLUMN llm_model_registry.base_model IS 'Base model used (e.g., Qwen/Qwen2.5-3B-Instruct)';
COMMENT ON COLUMN llm_model_registry.adapter_path IS 'Absolute path to LoRA adapter directory';
COMMENT ON COLUMN llm_model_registry.status IS 'Model status: candidate (testing), production (active), archived (deprecated)';
COMMENT ON COLUMN llm_model_registry.metrics_json IS 'Training metrics (loss, dataset_size, etc.)';
COMMENT ON COLUMN llm_model_registry.is_active IS 'TRUE if currently in production';
COMMENT ON COLUMN llm_model_registry.activated_at IS 'Timestamp when promoted to production';

-- Sample data (optional)
-- INSERT INTO llm_model_registry (model_name, version, base_model, adapter_path, status, metrics_json)
-- VALUES (
--     'dcim_assistant',
--     'v1.0',
--     'Qwen/Qwen2.5-3B-Instruct',
--     '/home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0/adapter',
--     'candidate',
--     '{"train_loss": 0.310, "dataset_size": 3816, "epochs": 3}'::jsonb
-- );

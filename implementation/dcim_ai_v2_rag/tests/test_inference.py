import pandas as pd
from sqlalchemy import create_engine
from dcim_ai.services.anomaly_service import AnomalyService

DB_URL = "postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai"

engine = create_engine(DB_URL)

query = """
SELECT *
FROM server_metrics
ORDER BY time DESC
LIMIT 200;
"""

df_live = pd.read_sql(query, engine)

service = AnomalyService(
    model_path="dcim_ai/artifacts/isolation_forest_v1.0_baseline.pkl",
    pipeline_path="dcim_ai/artifacts/feature_pipeline_v1.0_baseline.pkl",
    baseline_stats_path="dcim_ai/artifacts/feature_stats_v1.0_baseline.json"
)

print("Live mean:")
print(df_live.describe().T[["mean"]])
result = service.predict(df_live)

print(result)

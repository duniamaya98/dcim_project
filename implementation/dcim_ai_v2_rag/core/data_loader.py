import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()



# ======================================================
# DATABASE CONNECTION
# ======================================================

def get_db_engine():
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASS", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "dcim")

    connection_string = (
        f"postgresql+psycopg2://{db_user}:{db_pass}"
        f"@{db_host}:{db_port}/{db_name}"
    )

    return create_engine(connection_string)


# ======================================================
# LOAD TRAINING DATA
# ======================================================

def load_training_data(window: str = "last_30_minutes"):
    """
    Load telemetry data from server_metrics table
    """

    engine = get_db_engine()
    now = datetime.utcnow()

    if window == "last_30_minutes":
        start_time = now - timedelta(minutes=30)
    elif window == "last_1_hour":
        start_time = now - timedelta(hours=1)
    elif window == "last_6_hours":
        start_time = now - timedelta(hours=6)
    elif window == "last_24_hours":
        start_time = now - timedelta(hours=24)
    elif window == "all":
        start_time = datetime(1970, 1, 1)
    else:
        raise ValueError(f"Unsupported window: {window}")

    query = f"""
        SELECT *
        FROM server_metrics
        WHERE time >= '{start_time.isoformat()}'
        ORDER BY time ASC
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        raise ValueError("No training data found for selected window.")

    # ======================================================
    # CLEANING
    # ======================================================

    # Drop non-feature columns
    drop_cols = ["time", "hostname"]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns])

    # Remove null rows
    df = df.dropna()

    if df.empty:
        raise ValueError("All rows dropped after cleaning (null removal).")

    return df
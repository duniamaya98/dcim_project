import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class FeaturePipeline:

    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_columns = None

    def _clean_dataframe(self, df: pd.DataFrame):

        # Drop non-feature columns
        df = df.drop(columns=["time", "hostname"], errors="ignore")

        # Drop NA
        df = df.dropna()

        # Keep only numeric columns
        df = df.select_dtypes(include=[np.number])

        return df

    def fit(self, df: pd.DataFrame):

        df_clean = self._clean_dataframe(df)

        # Remove low variance features
        variance = df_clean.var()
        low_variance_cols = variance[variance < 1e-3].index.tolist()

        df_clean = df_clean.drop(columns=low_variance_cols)

        self.feature_columns = df_clean.columns.tolist()

        X = df_clean.values

        self.scaler.fit(X)

    def transform(self, df: pd.DataFrame):

        df_clean = self._clean_dataframe(df)

        # Keep only trained features
        df_clean = df_clean[self.feature_columns]

        X = df_clean.values

        return self.scaler.transform(X)

    def save(self, path):
        joblib.dump(self, path)

    @staticmethod
    def load(path):
        return joblib.load(path)
    
    def get_baseline_stats(self):
        return {
            "features": self.feature_columns,
            "mean": self.scaler.mean_.tolist(),
            "std": np.sqrt(self.scaler.var_).tolist()
        }

        

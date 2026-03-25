from sklearn.ensemble import IsolationForest
import pandas as pd
from sklearn.preprocessing import StandardScaler

def detect_anomalies(df):
    df_copy = df.copy()

    # Only expenses
    df_copy = df_copy[df_copy["debit"] > 0]

    if df_copy.empty or len(df_copy) < 10:
        return pd.DataFrame()

    # Feature engineering
    df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce")
    df_copy["day"] = df_copy["date"].dt.day
    df_copy["month"] = df_copy["date"].dt.month

    # Features for model
    features = df_copy[["debit", "day", "month"]]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # Train model
    model = IsolationForest(
        n_estimators=200,
        contamination=0.03,
        random_state=42
    )

    # ✅ fit first, then use both methods on the same fitted model
    model.fit(features_scaled)
    df_copy["anomaly"] = model.predict(features_scaled)
    df_copy["anomaly"] = df_copy["anomaly"].map({1: 0, -1: 1})
    df_copy["anomaly_score"] = -model.score_samples(features_scaled)

    return df_copy

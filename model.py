import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

FEATURES = ["pressure_1", "pressure_2", "flow_1", "flow_2", "pump_status"]

def make_demo_dataset(n=1600, seed=42):
    """Synthetic data for software demonstration only; not field-validated data."""
    rng = np.random.default_rng(seed)
    labels = rng.choice([0, 1], size=n, p=[0.65, 0.35])
    p1 = rng.normal(2.8, 0.18, n)
    p2 = p1 - rng.normal(0.15, 0.08, n)
    f1 = rng.normal(8.0, 0.55, n)
    f2 = f1 - rng.normal(0.10, 0.18, n)
    pump = rng.choice([0, 1], size=n, p=[0.2, 0.8])
    # Simulated leak signatures: pressure drop and flow imbalance.
    leak = labels == 1
    p2[leak] -= rng.uniform(0.35, 1.0, leak.sum())
    f1[leak] += rng.uniform(0.15, 0.8, leak.sum())
    f2[leak] -= rng.uniform(0.3, 1.2, leak.sum())
    return pd.DataFrame({
        "pressure_1": np.clip(p1, 0.1, None),
        "pressure_2": np.clip(p2, 0.1, None),
        "flow_1": np.clip(f1, 0.0, None),
        "flow_2": np.clip(f2, 0.0, None),
        "pump_status": pump.astype(int),
        "label": labels
    })

def train_demo_model():
    df = make_demo_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        df[FEATURES], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
    )
    model = RandomForestClassifier(n_estimators=160, max_depth=10, random_state=42,
                                   class_weight="balanced")
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred, zero_division=0),
        "recall": recall_score(y_test, pred, zero_division=0),
        "f1": f1_score(y_test, pred, zero_division=0),
        "confusion": confusion_matrix(y_test, pred).tolist()
    }
    return model, metrics

def predict_status(model, row):
    x = pd.DataFrame([{k: float(row[k]) for k in FEATURES}])
    probability = float(model.predict_proba(x)[0][1])
    if probability >= 0.70:
        status = "LEAK SUSPECTED"
    elif probability >= 0.40:
        status = "WARNING"
    else:
        status = "NORMAL"
    return status, probability

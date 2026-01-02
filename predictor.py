from typing import List, Dict
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
from utils import get_logger

logger = get_logger("predictor")

def compute_features(price_df: pd.DataFrame) -> pd.DataFrame:
    df = price_df.copy()
    df = df.sort_index()
    df["ret_1d"] = df["Close"].pct_change()
    df["ret_3d"] = df["Close"].pct_change(3)
    df["vol_5d"] = df["Close"].rolling(5).std()
    df["target_next_1d"] = df["Close"].shift(-1).pct_change().apply(lambda x: 1 if x > 0 else 0)
    df = df.dropna()
    return df

def build_training_set(price_dfs: Dict[str, pd.DataFrame], sentiment_features: Dict[str, float]) -> pd.DataFrame:
    rows = []
    for symbol, df in price_dfs.items():
        if df is None or df.empty:
            continue
        feats = compute_features(df)
        feats = feats.copy()
        feats["sentiment"] = sentiment_features.get(symbol, 0.0)
        feats["symbol"] = symbol
        rows.append(feats[["symbol", "ret_1d", "ret_3d", "vol_5d", "sentiment", "target_next_1d"]])
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=False)

def train_model(df: pd.DataFrame, persist_path: str = "models/model.joblib"):
    if df is None or df.empty:
        logger.warning("Empty training set")
        return None
    X = df[["ret_1d", "ret_3d", "vol_5d", "sentiment"]]
    y = df["target_next_1d"]
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X.fillna(0))
    X_train, X_test, y_train, y_test = train_test_split(Xs, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    bundle = {"model": clf, "scaler": scaler, "accuracy": acc}
    os.makedirs(os.path.dirname(persist_path), exist_ok=True)
    joblib.dump(bundle, persist_path)
    return bundle

def load_model(persist_path: str = "models/model.joblib"):
    """Load a trained model bundle from disk."""
    try:
        return joblib.load(persist_path)
    except Exception as e:
        logger.error(f"Failed to load model from {persist_path}: {e}")
        return None

def predict_for_symbols(model_bundle, df: pd.DataFrame) -> Dict[str, float]:
    """
    Generate predictions for each symbol in the dataframe.
    Returns a dictionary of {symbol: probability_of_up_movement}.
    """
    if model_bundle is None:
        logger.warning("No model bundle provided")
        return {}
    
    clf = model_bundle.get("model")
    scaler = model_bundle.get("scaler")
    
    if clf is None or scaler is None:
        logger.warning("Invalid model bundle")
        return {}
    
    preds_dict = {}
    if df is None or df.empty:
        return preds_dict
    
    # Group by symbol and get predictions
    for symbol in df["symbol"].unique():
        symbol_data = df[df["symbol"] == symbol]
        if symbol_data.empty:
            continue
        
        X = symbol_data[["ret_1d", "ret_3d", "vol_5d", "sentiment"]].fillna(0)
        Xs = scaler.transform(X)
        
        # Get probability of class 1 (up movement)
        probs = clf.predict_proba(Xs)[:, 1]
        preds_dict[symbol] = float(np.mean(probs)) if len(probs) > 0 else 0.5
    
    return preds_dict

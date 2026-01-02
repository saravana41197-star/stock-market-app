import os
import pandas as pd
import numpy as np
from sentiment_analysis import analyze_headlines
from predictor import compute_features, train_model, build_training_set, predict_for_symbols
from utils import get_logger

# Initialize logger
logger = get_logger("smoke_test")

def make_dummy_price(symbol: str) -> pd.DataFrame:
    """
    Create a dummy price DataFrame for testing.
    Generates 30 business days of synthetic closing prices.
    """
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30, freq="B")
    close = np.cumsum(np.random.randn(len(dates))) + 100
    df = pd.DataFrame({"Close": close}, index=dates)
    return df

def run():
    logger.info("Starting smoke test")

    # Example headlines for sentiment analysis
    headlines = [
        "Stocks rally as markets cheer positive earnings",
        "Investors cautious amid inflation fears"
    ]
    sent = analyze_headlines(headlines)

    # Example symbols
    symbols = ["AAA.NS", "BBB.NS"]

    # Generate dummy price data
    price_dfs = {s: make_dummy_price(s) for s in symbols}

    # Example sentiment mapping (normally from analysis)
    sent_map = {"AAA.NS": 0.2, "BBB.NS": -0.1}

    # Build training set
    train_df = build_training_set(price_dfs, sent_map)

    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)

    # Train model and persist
    model_bundle = train_model(train_df, persist_path="models/test_model.joblib")

    # Predict for symbols
    preds = predict_for_symbols(model_bundle, train_df)

    logger.info("Smoke test completed successfully. Predictions: %s", preds)

if __name__ == "__main__":
    run()
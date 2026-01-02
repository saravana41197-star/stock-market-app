from data_fetcher import fetch_market_news, fetch_multiple_prices
from sentiment_analysis import analyze_headlines
from predictor import build_training_set, train_model, predict_for_symbols, load_model
from utils import get_logger
import json

logger = get_logger("main")

def run_pipeline(watchlist, model_path: str = "models/model.joblib"):
    news = fetch_market_news()
    combined = []
    for src, hs in news.items():
        combined += hs
    sentiments = analyze_headlines(combined)
    symbols = watchlist
    prices = fetch_multiple_prices(symbols, period="1y")
    sent_map = {s: 0.0 for s in symbols}
    for rec in sentiments:
        t = rec["text"].lower()
        for s in symbols:
            base = s.split(".")[0].lower()
            if base in t:
                sent_map[s] += rec.get("compound", 0.0)
    train_df = build_training_set(prices, sent_map)
    model = None
    if train_df is None or train_df.empty:
        model = load_model(model_path)
    else:
        model = train_model(train_df, persist_path=model_path)
    preds = predict_for_symbols(model, train_df) if model else {}
    ranked = sorted(preds.items(), key=lambda x: x[1], reverse=True)
    out = {"news_count": sum(len(v) for v in news.values()), "preds": preds, "ranked": ranked, "sentiment_map": sent_map}
    with open("pipeline_output.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out

if __name__ == "__main__":
    # Example watchlist
    watchlist = [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "ITC.NS",
        "ADANIENT.NS"
    ]
    
    logger.info(f"Starting pipeline with watchlist: {watchlist}")
    result = run_pipeline(watchlist)
    logger.info(f"Pipeline completed. Output written to pipeline_output.json")
    logger.info(f"Predictions: {result.get('ranked', [])}")

from typing import Dict
from utils import get_logger
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize logger
logger = get_logger("sentiment_analysis")

# Ensure VADER lexicon is available
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except Exception:
    nltk.download("vader_lexicon")

# Initialize VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Try to initialize transformer pipeline if available
_transformer_pipeline = None
try:
    from transformers import pipeline
    _transformer_pipeline = pipeline("sentiment-analysis")
except Exception:
    pass

def score_text(text: str, use_transformer: bool = False) -> Dict[str, float]:
    """
    Score a text string for sentiment.
    If use_transformer=True and transformers pipeline is available, use that.
    Otherwise fall back to VADER sentiment analysis.
    Returns a dictionary with neg/neu/pos/compound scores.
    """
    try:
        if use_transformer and _transformer_pipeline is not None:
            t = _transformer_pipeline(text[:512])
            if isinstance(t, list) and t:
                lab = t[0].get("label", "")
                sc = float(t[0].get("score", 0.0))
                if lab.upper().startswith("POS"):
                    return {"neg": 0.0, "neu": 1 - sc, "pos": sc, "compound": sc}
                else:
                    return {"neg": sc, "neu": 1 - sc, "pos": 0.0, "compound": -sc}
        # Default to VADER
        return sia.polarity_scores(text)
    except Exception:
        return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}

def analyze_headlines(headlines: list, use_transformer: bool = False) -> list:
    """
    Analyze a list of headlines for sentiment.
    Returns a list of dictionaries with text and sentiment scores.
    """
    results = []
    for headline in headlines:
        scores = score_text(headline, use_transformer=use_transformer)
        results.append({
            "text": headline,
            "neg": scores.get("neg", 0.0),
            "neu": scores.get("neu", 0.0),
            "pos": scores.get("pos", 0.0),
            "compound": scores.get("compound", 0.0)
        })
    return results
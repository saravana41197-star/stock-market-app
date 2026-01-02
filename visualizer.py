import matplotlib.pyplot as plt
import io
import base64
from utils import get_logger
import pandas as pd

logger = get_logger("visualizer")

def plot_sentiment_bar(sentiment_scores: dict, title: str = "Sentiment Scores") -> str:
    names = list(sentiment_scores.keys())
    vals = [sentiment_scores[k] for k in names]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(names, vals, color="tab:blue")
    ax.set_title(title)
    ax.set_ylabel("Compound Sentiment")
    plt.xticks(rotation=45, ha="right")
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return f"data:image/png;base64,{b64}"

def plot_price_trend(df: pd.DataFrame, title: str = "Price Trend") -> str:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df["Close"], label="Close")
    ax.set_title(title)
    ax.legend()
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return f"data:image/png;base64,{b64}"


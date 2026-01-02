"""Fetch news and price data for Indian stocks/indices."""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from utils import get_logger

# Try to import yfinance; if not available, provide mock
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None

logger = get_logger("data_fetcher")

NEWS_SOURCES = {
    "moneycontrol": "https://www.moneycontrol.com/news/",
    "economictimes": "https://economictimes.indiatimes.com/markets",
    "business_standard": "https://www.business-standard.com/markets",
    "nse": "https://www.nseindia.com",
    "bse": "https://www.bseindia.com",
}

def fetch_page_headlines(url: str, css_select: str = "h2, h3, a") -> List[str]:
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        elems = soup.select(css_select)
        headlines = []
        for e in elems:
            txt = e.get_text(strip=True)
            if txt and len(txt) > 20:
                headlines.append(txt)
        logger.info("Fetched %d headlines from %s", len(headlines), url)
        return headlines
    except Exception as e:
        logger.exception("Error fetching %s: %s", url, e)
        return []

def fetch_market_news() -> Dict[str, List[str]]:
    out = {}
    for name, url in NEWS_SOURCES.items():
        try:
            if name == "moneycontrol":
                headlines = fetch_page_headlines(url, css_select=".srchResult, .clearfix h2, h3 a")
            elif name == "economictimes":
                headlines = fetch_page_headlines(url, css_select=".title, a, h2, h3")
            elif name == "business_standard":
                headlines = fetch_page_headlines(url, css_select="h2, h3, a")
            else:
                headlines = fetch_page_headlines(url)
            out[name] = headlines[:60]
        except Exception:
            out[name] = []
    return out

def fetch_price(symbol: str, period: str = "1y", interval: str = "1d"):
    if not YFINANCE_AVAILABLE:
        logger.warning("yfinance not installed; returning None for %s", symbol)
        return None
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            logger.warning("No data for %s", symbol)
        return df
    except Exception as e:
        logger.exception("Error fetching price for %s: %s", symbol, e)
        return None

def fetch_multiple_prices(symbols: List[str], period: str = "1y"):
    data = {}
    for s in symbols:
        data[s] = fetch_price(s, period=period)
    return data


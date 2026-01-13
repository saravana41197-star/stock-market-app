"""Real-time data ingestion for live price, volume, and options chain data."""
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time
from utils import get_logger
from cache_manager import cache_manager, cached_call, fallback_manager

logger = get_logger("realtime_data")

class RealTimeDataFetcher:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 30  # seconds
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache:
            return False
        timestamp, _ = self.cache[key]
        return (datetime.now() - timestamp).total_seconds() < self.cache_duration
    
    def _get_cached_data(self, key: str) -> Optional[any]:
        """Get data from cache if valid."""
        if self._is_cache_valid(key):
            _, data = self.cache[key]
            return data
        return None
    
    def _cache_data(self, key: str, data: any):
        """Cache data with timestamp."""
        self.cache[key] = (datetime.now(), data)
    
    def get_live_price(self, symbol: str) -> Optional[Dict]:
        """Get live price data for a symbol."""
        return cached_call(
            f"live_price_{symbol}",
            self._fetch_live_price,
            ttl=30,
            use_fallback=True
        )(symbol)
    
    def _fetch_live_price(self, symbol: str) -> Optional[Dict]:
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get recent price data
            hist = ticker.history(period="1d", interval="1m")
            if hist.empty:
                logger.warning(f"No intraday data for {symbol}")
                return None
            
            current_price = hist['Close'].iloc[-1]
            volume = hist['Volume'].iloc[-1]
            
            # Calculate price change
            prev_close = info.get('regularMarketPreviousClose', current_price)
            price_change = current_price - prev_close
            price_change_pct = (price_change / prev_close) * 100 if prev_close > 0 else 0
            
            # Calculate volume metrics
            avg_volume = info.get('averageVolume', volume)
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            data = {
                'symbol': symbol,
                'current_price': current_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'volume': volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'timestamp': datetime.now(),
                'day_high': hist['High'].max(),
                'day_low': hist['Low'].min(),
                'open_price': hist['Open'].iloc[0] if not hist.empty else current_price
            }
            
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching live price for {symbol}: {e}")
            # Return fallback data
            return fallback_manager.get_fallback_price_data(symbol)
    
    def get_options_chain(self, symbol: str) -> Optional[Dict]:
        """Get options chain data for analysis."""
        return cached_call(
            f"options_chain_{symbol}",
            self._fetch_options_chain,
            ttl=60,  # Options data changes less frequently
            use_fallback=True
        )(symbol)
    
    def _fetch_options_chain(self, symbol: str) -> Optional[Dict]:
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Try to get options data
            expirations = ticker.options
            if not expirations:
                logger.warning(f"No options data available for {symbol}")
                return self._get_mock_options_data(symbol)
            
            # Get the nearest expiration
            nearest_expiry = expirations[0]
            opt = ticker.option_chain(nearest_expiry)
            
            calls = opt.calls
            puts = opt.puts
            
            # Calculate key metrics
            total_call_oi = calls['openInterest'].sum() if not calls.empty else 0
            total_put_oi = puts['openInterest'].sum() if not puts.empty else 0
            pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 1
            
            # Calculate average IV
            avg_call_iv = calls['impliedVolatility'].mean() if not calls.empty else 0
            avg_put_iv = puts['impliedVolatility'].mean() if not puts.empty else 0
            
            data = {
                'symbol': symbol,
                'total_call_oi': total_call_oi,
                'total_put_oi': total_put_oi,
                'put_call_ratio': pcr,
                'avg_call_iv': avg_call_iv,
                'avg_put_iv': avg_put_iv,
                'expiry_date': nearest_expiry,
                'timestamp': datetime.now()
            }
            
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching options for {symbol}: {e}")
            return fallback_manager.get_fallback_options_data(symbol)
    
    def _get_mock_options_data(self, symbol: str) -> Dict:
        """Generate mock options data when real data is not available."""
        import random
        
        # Generate realistic mock data based on symbol
        base_oi = 50000 if "^" in symbol else 10000  # Higher OI for indices
        
        total_call_oi = base_oi * random.uniform(0.8, 1.5)
        total_put_oi = base_oi * random.uniform(0.6, 1.2)
        pcr = total_put_oi / total_call_oi
        
        data = {
            'symbol': symbol,
            'total_call_oi': total_call_oi,
            'total_put_oi': total_put_oi,
            'put_call_ratio': pcr,
            'avg_call_iv': random.uniform(0.15, 0.35),
            'avg_put_iv': random.uniform(0.18, 0.40),
            'expiry_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'timestamp': datetime.now(),
            'mock_data': True
        }
        
        return data
    
    def get_market_sentiment_velocity(self, symbols: List[str]) -> Dict:
        """Calculate sentiment velocity based on price movements and volume."""
        cache_key = f"sentiment_velocity_{'_'.join(symbols)}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            sentiment_data = {}
            
            for symbol in symbols:
                price_data = self.get_live_price(symbol)
                if not price_data:
                    continue
                
                # Calculate momentum indicators
                price_momentum = price_data['price_change_pct']
                volume_momentum = price_data['volume_ratio']
                
                # Combine for sentiment velocity
                sentiment_velocity = (price_momentum * 0.6) + ((volume_momentum - 1) * 40 * 0.4)
                
                sentiment_data[symbol] = {
                    'price_momentum': price_momentum,
                    'volume_momentum': volume_momentum,
                    'sentiment_velocity': sentiment_velocity,
                    'timestamp': datetime.now()
                }
            
            self._cache_data(cache_key, sentiment_data)
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error calculating sentiment velocity: {e}")
            return {}
    
    def get_intraday_trend(self, symbol: str, periods: int = 20) -> Dict:
        """Calculate intraday trend direction and strength."""
        return cached_call(
            f"intraday_trend_{symbol}_{periods}",
            self._fetch_intraday_trend,
            ttl=45,
            use_fallback=True
        )(symbol, periods)
    
    def _fetch_intraday_trend(self, symbol: str, periods: int = 20) -> Dict:
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="5m")
            
            if len(hist) < periods:
                logger.warning(f"Insufficient data for trend analysis of {symbol}")
                return {'trend': 'NEUTRAL', 'strength': 0, 'direction': 0}
            
            # Calculate trend using linear regression on recent prices
            prices = hist['Close'].tail(periods).values
            x = np.arange(len(prices))
            
            # Simple linear regression
            coeffs = np.polyfit(x, prices, 1)
            slope = coeffs[0]
            
            # Calculate trend strength
            price_std = np.std(prices)
            trend_strength = abs(slope) / price_std if price_std > 0 else 0
            
            # Determine trend direction
            if slope > 0.01:
                trend = "BULLISH"
                direction = 1
            elif slope < -0.01:
                trend = "BEARISH"
                direction = -1
            else:
                trend = "NEUTRAL"
                direction = 0
            
            data = {
                'symbol': symbol,
                'trend': trend,
                'direction': direction,
                'strength': min(trend_strength, 10),  # Cap at 10
                'slope': slope,
                'timestamp': datetime.now()
            }
            
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Error calculating intraday trend for {symbol}: {e}")
            return fallback_manager.get_fallback_trend_data(symbol)

# Global instance
data_fetcher = RealTimeDataFetcher()

def get_index_data() -> Dict[str, Dict]:
    """Get comprehensive data for major indices."""
    indices = ["^NSEI", "^NSEBANK", "^BSESN"]  # Nifty 50, Bank Nifty, Sensex
    index_names = ["Nifty 50", "Bank Nifty", "Sensex"]
    
    data = {}
    
    for symbol, name in zip(indices, index_names):
        price_data = data_fetcher.get_live_price(symbol)
        options_data = data_fetcher.get_options_chain(symbol)
        trend_data = data_fetcher.get_intraday_trend(symbol)
        
        if price_data:
            data[name] = {
                'symbol': symbol,
                'price_data': price_data,
                'options_data': options_data or {},
                'trend_data': trend_data,
                'name': name
            }
    
    return data

def get_stock_data(symbols: List[str]) -> Dict[str, Dict]:
    """Get comprehensive data for stock symbols."""
    data = {}
    
    for symbol in symbols:
        price_data = data_fetcher.get_live_price(symbol)
        options_data = data_fetcher.get_options_chain(symbol)
        trend_data = data_fetcher.get_intraday_trend(symbol)
        
        if price_data:
            data[symbol] = {
                'symbol': symbol,
                'price_data': price_data,
                'options_data': options_data or {},
                'trend_data': trend_data
            }
    
    return data

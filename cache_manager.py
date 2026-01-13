"""Caching and fallback mechanism for real-time data."""
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from utils import get_logger

logger = get_logger("cache_manager")

class CacheManager:
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 30):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl  # seconds
        self.memory_cache = {}
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_file_path(self, key: str) -> str:
        """Get file path for cached data."""
        safe_key = key.replace("/", "_").replace("\\", "_")
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def _is_expired(self, timestamp: datetime, ttl: int) -> bool:
        """Check if cached data is expired."""
        return (datetime.now() - timestamp).total_seconds() > ttl
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """Get data from cache (memory first, then file)."""
        ttl = ttl or self.default_ttl
        
        # Check memory cache first
        if key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if not self._is_expired(timestamp, ttl):
                logger.debug(f"Cache hit (memory): {key}")
                return data
            else:
                # Remove expired memory cache
                del self.memory_cache[key]
        
        # Check file cache
        cache_file = self._get_cache_file_path(key)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                timestamp = datetime.fromisoformat(cached_data.get('timestamp', '1970-01-01'))
                if not self._is_expired(timestamp, ttl):
                    logger.debug(f"Cache hit (file): {key}")
                    # Store in memory for faster access
                    self.memory_cache[key] = (cached_data['data'], timestamp)
                    return cached_data['data']
                else:
                    # Remove expired file cache
                    os.remove(cache_file)
                    logger.debug(f"Removed expired cache file: {key}")
                    
            except Exception as e:
                logger.error(f"Error reading cache file {key}: {e}")
                # Remove corrupted cache file
                try:
                    os.remove(cache_file)
                except:
                    pass
        
        logger.debug(f"Cache miss: {key}")
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Store data in cache (both memory and file)."""
        ttl = ttl or self.default_ttl
        timestamp = datetime.now()
        
        # Store in memory
        self.memory_cache[key] = (data, timestamp)
        
        # Store in file
        cache_file = self._get_cache_file_path(key)
        try:
            cached_data = {
                'data': data,
                'timestamp': timestamp.isoformat(),
                'ttl': ttl
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f, indent=2, default=str)
                
            logger.debug(f"Cached data: {key}")
            
        except Exception as e:
            logger.error(f"Error writing cache file {key}: {e}")
    
    def clear(self, pattern: Optional[str] = None) -> None:
        """Clear cache entries."""
        if pattern:
            # Clear specific pattern
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.memory_cache[key]
            
            # Clear matching files
            for filename in os.listdir(self.cache_dir):
                if pattern in filename:
                    try:
                        os.remove(os.path.join(self.cache_dir, filename))
                    except:
                        pass
        else:
            # Clear all
            self.memory_cache.clear()
            try:
                for filename in os.listdir(self.cache_dir):
                    os.remove(os.path.join(self.cache_dir, filename))
            except:
                pass
        
        logger.info(f"Cleared cache: {pattern or 'all'}")
    
    def cleanup_expired(self) -> None:
        """Remove all expired cache entries."""
        current_time = datetime.now()
        
        # Clean memory cache
        expired_keys = []
        for key, (data, timestamp) in self.memory_cache.items():
            if self._is_expired(timestamp, self.default_ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Clean file cache
        try:
            for filename in os.listdir(self.cache_dir):
                cache_file = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                    
                    timestamp = datetime.fromisoformat(cached_data.get('timestamp', '1970-01-01'))
                    ttl = cached_data.get('ttl', self.default_ttl)
                    
                    if self._is_expired(timestamp, ttl):
                        os.remove(cache_file)
                        
                except:
                    # Remove corrupted files
                    try:
                        os.remove(cache_file)
                    except:
                        pass
        except:
            pass
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

class FallbackManager:
    """Fallback data provider when real-time data is not available."""
    
    def __init__(self):
        self.fallback_data = {}
    
    def get_fallback_price_data(self, symbol: str) -> Dict:
        """Get fallback price data when real data fails."""
        import random
        
        # Generate realistic fallback data
        base_prices = {
            "^NSEI": 23500,      # Nifty 50
            "^NSEBANK": 60000,   # Bank Nifty  
            "^BSESN": 78000,     # Sensex
            "RELIANCE.NS": 2800,
            "TCS.NS": 3800,
            "INFY.NS": 1600,
            "HDFCBANK.NS": 1700,
            "ICICIBANK.NS": 1000
        }
        
        base_price = base_prices.get(symbol, 1000)
        
        # Add some random variation
        variation = random.uniform(-0.02, 0.02)  # ±2%
        current_price = base_price * (1 + variation)
        price_change = (current_price - base_price) / base_price * 100
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'price_change': price_change * base_price / 100,
            'price_change_pct': price_change,
            'volume': random.randint(1000000, 10000000),
            'avg_volume': random.randint(2000000, 8000000),
            'volume_ratio': random.uniform(0.5, 2.0),
            'timestamp': datetime.now(),
            'day_high': current_price * random.uniform(1.0, 1.03),
            'day_low': current_price * random.uniform(0.97, 1.0),
            'open_price': base_price,
            'fallback': True,
            'fallback_reason': 'Real-time data unavailable'
        }
    
    def get_fallback_options_data(self, symbol: str) -> Dict:
        """Get fallback options data."""
        import random
        
        base_oi = 50000 if "^" in symbol else 10000
        
        return {
            'symbol': symbol,
            'total_call_oi': base_oi * random.uniform(0.8, 1.5),
            'total_put_oi': base_oi * random.uniform(0.6, 1.2),
            'put_call_ratio': random.uniform(0.7, 1.3),
            'avg_call_iv': random.uniform(0.15, 0.35),
            'avg_put_iv': random.uniform(0.18, 0.40),
            'expiry_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'timestamp': datetime.now(),
            'fallback': True,
            'fallback_reason': 'Options data unavailable'
        }
    
    def get_fallback_trend_data(self, symbol: str) -> Dict:
        """Get fallback trend data."""
        import random
        
        direction = random.choice([-1, 0, 1])
        strength = random.uniform(0, 5)
        
        trend_map = {1: "BULLISH", -1: "BEARISH", 0: "NEUTRAL"}
        
        return {
            'symbol': symbol,
            'trend': trend_map[direction],
            'direction': direction,
            'strength': strength,
            'slope': direction * random.uniform(0, 0.1),
            'timestamp': datetime.now(),
            'fallback': True,
            'fallback_reason': 'Trend analysis unavailable'
        }

# Global instances
cache_manager = CacheManager()
fallback_manager = FallbackManager()

def cached_call(key: str, func, ttl: Optional[int] = None, use_fallback: bool = True):
    """Decorator/function to cache expensive function calls."""
    def wrapper(*args, **kwargs):
        cache_key = f"{key}_{hash(str(args) + str(kwargs))}"
        
        # Try to get from cache
        result = cache_manager.get(cache_key, ttl)
        if result is not None:
            return result
        
        # Call the function
        try:
            result = func(*args, **kwargs)
            if result is not None:
                cache_manager.set(cache_key, result, ttl)
            return result
        except Exception as e:
            logger.error(f"Error in cached call {key}: {e}")
            
            # Return fallback if available
            if use_fallback:
                if 'price' in key.lower():
                    return fallback_manager.get_fallback_price_data(args[0] if args else 'UNKNOWN')
                elif 'options' in key.lower():
                    return fallback_manager.get_fallback_options_data(args[0] if args else 'UNKNOWN')
                elif 'trend' in key.lower():
                    return fallback_manager.get_fallback_trend_data(args[0] if args else 'UNKNOWN')
            
            return None
    
    return wrapper

def cleanup_cache():
    """Clean up expired cache entries."""
    cache_manager.cleanup_expired()

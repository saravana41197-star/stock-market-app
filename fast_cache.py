"""Fast caching system for optimized loading times."""
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from utils import get_logger

logger = get_logger("fast_cache")

class FastCache:
    def __init__(self, cache_dir: str = "fast_cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def get(self, key: str, max_age_hours: int = 24) -> Optional[Any]:
        """Get cached data if available and not too old."""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check age
            cache_time = datetime.fromisoformat(cache_data.get('timestamp', '1970-01-01'))
            age = datetime.now() - cache_time
            
            if age > timedelta(hours=max_age_hours):
                logger.info(f"Cache expired for {key}")
                os.remove(cache_file)
                return None
            
            logger.debug(f"Cache hit for {key}")
            return cache_data['data']
            
        except Exception as e:
            logger.error(f"Error reading cache {key}: {e}")
            try:
                os.remove(cache_file)
            except:
                pass
            return None
    
    def set(self, key: str, data: Any) -> None:
        """Set data in cache."""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        try:
            cache_data = {
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'key': key
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            logger.debug(f"Cached data for {key}")
            
        except Exception as e:
            logger.error(f"Error writing cache {key}: {e}")
    
    def clear(self, pattern: Optional[str] = None) -> None:
        """Clear cache entries."""
        try:
            for filename in os.listdir(self.cache_dir):
                if pattern is None or pattern in filename:
                    os.remove(os.path.join(self.cache_dir, filename))
            
            logger.info(f"Cleared cache: {pattern or 'all'}")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

# Global cache instance
fast_cache = FastCache()

def cached_fetch(key: str, fetch_func, max_age_hours: int = 1, *args, **kwargs):
    """Generic cached fetch function."""
    # Try to get from cache
    cached_data = fast_cache.get(key, max_age_hours)
    if cached_data is not None:
        return cached_data
    
    # Fetch fresh data
    try:
        fresh_data = fetch_func(*args, **kwargs)
        fast_cache.set(key, fresh_data)
        return fresh_data
    except Exception as e:
        logger.error(f"Error in cached_fetch for {key}: {e}")
        return None

# Predefined cache keys
CACHE_KEYS = {
    'market_news': 'market_news',
    'index_predictions': 'index_predictions',
    'stock_predictions': 'stock_predictions',
    'news_sentiment': 'news_sentiment',
    'market_summary': 'market_summary'
}

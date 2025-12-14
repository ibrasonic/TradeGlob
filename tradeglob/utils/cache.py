"""Caching system for market data"""

import pickle
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any
import pandas as pd

logger = logging.getLogger(__name__)


class DataCache:
    """
    Local file-based cache for market data
    
    Features:
    - Automatic expiration based on age
    - Separate cache per symbol/exchange/interval
    - Cache invalidation and cleanup
    """
    
    def __init__(self, cache_dir: str = '.cache', enabled: bool = True):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory for cache files
            enabled: Enable/disable caching
        """
        self.enabled = enabled
        self.cache_dir = Path(cache_dir)
        
        if self.enabled:
            self.cache_dir.mkdir(exist_ok=True)
            logger.info(f"Cache initialized at {self.cache_dir.absolute()}")
        else:
            logger.info("Cache disabled")
    
    def _get_cache_key(self, symbol: str, exchange: str, interval: str, n_bars: int) -> str:
        """Generate cache filename"""
        return f"{exchange}_{symbol}_{interval}_{n_bars}.pkl"
    
    def get(
        self, 
        symbol: str, 
        exchange: str, 
        interval: str, 
        n_bars: int, 
        max_age_hours: int = 24
    ) -> Optional[pd.DataFrame]:
        """
        Get cached data if available and fresh
        
        Args:
            symbol: Stock symbol
            exchange: Exchange code
            interval: Time interval
            n_bars: Number of bars
            max_age_hours: Maximum age in hours before expiration
            
        Returns:
            DataFrame if cached and fresh, None otherwise
        """
        if not self.enabled:
            return None
        
        cache_file = self.cache_dir / self._get_cache_key(symbol, exchange, interval, n_bars)
        
        if not cache_file.exists():
            return None
        
        # Check age
        try:
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            age = datetime.now() - file_time
            
            if age > timedelta(hours=max_age_hours):
                logger.debug(f"Cache expired for {symbol} (age: {age})")
                return None
            
            # Load cached data
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            logger.info(f"✓ Cache hit for {symbol} (age: {age.seconds//3600}h {(age.seconds//60)%60}m)")
            return data
            
        except Exception as e:
            logger.warning(f"Failed to load cache for {symbol}: {e}")
            # Delete corrupted cache file
            try:
                cache_file.unlink()
            except:
                pass
            return None
    
    def set(
        self, 
        symbol: str, 
        exchange: str, 
        interval: str, 
        n_bars: int, 
        data: pd.DataFrame
    ) -> bool:
        """
        Save data to cache
        
        Args:
            symbol: Stock symbol
            exchange: Exchange code
            interval: Time interval
            n_bars: Number of bars
            data: DataFrame to cache
            
        Returns:
            bool: True if saved successfully
        """
        if not self.enabled:
            return False
        
        if data is None or data.empty:
            return False
        
        cache_file = self.cache_dir / self._get_cache_key(symbol, exchange, interval, n_bars)
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug(f"Cached data for {symbol}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to cache data for {symbol}: {e}")
            return False
    
    def invalidate(self, symbol: Optional[str] = None, exchange: Optional[str] = None):
        """
        Invalidate cache for specific symbol or all
        
        Args:
            symbol: Symbol to invalidate (None = all)
            exchange: Exchange to invalidate (None = all)
        """
        if not self.enabled:
            return
        
        pattern = "*"
        if exchange and symbol:
            pattern = f"{exchange}_{symbol}_*.pkl"
        elif exchange:
            pattern = f"{exchange}_*.pkl"
        elif symbol:
            pattern = f"*_{symbol}_*.pkl"
        
        count = 0
        for file in self.cache_dir.glob(pattern):
            try:
                file.unlink()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to delete cache file {file}: {e}")
        
        if count > 0:
            logger.info(f"Invalidated {count} cache files")
    
    def clear(self):
        """Clear entire cache"""
        if not self.enabled:
            return
        
        count = 0
        for file in self.cache_dir.glob('*.pkl'):
            try:
                file.unlink()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to delete cache file {file}: {e}")
        
        logger.info(f"Cleared {count} cache files")
    
    def get_cache_info(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {'enabled': False}
        
        files = list(self.cache_dir.glob('*.pkl'))
        total_size = sum(f.stat().st_size for f in files)
        
        return {
            'enabled': True,
            'location': str(self.cache_dir.absolute()),
            'files': len(files),
            'size_mb': total_size / (1024 * 1024),
            'oldest': min((f.stat().st_mtime for f in files), default=None),
            'newest': max((f.stat().st_mtime for f in files), default=None)
        }

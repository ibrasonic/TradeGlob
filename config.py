"""Configuration classes for TradeGlob"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FetcherConfig:
    """
    Configuration for TradeGlobFetcher
    
    Attributes:
        retry_attempts: Number of retry attempts for failed requests
        retry_delay: Delay between retries in seconds
        retry_backoff: Backoff multiplier for exponential retry
        max_workers: Maximum parallel workers for concurrent fetching
        cache_enabled: Enable local caching
        cache_max_age_hours: Maximum cache age before expiration
        safety_buffer: Multiplier for n_bars calculation (e.g., 1.3 = 30% buffer)
        min_bars_daily: Minimum bars for Daily interval
        min_bars_weekly: Minimum bars for Weekly interval
        min_bars_monthly: Minimum bars for Monthly interval
        min_bars_intraday: Minimum bars for intraday intervals
        connection_timeout: Timeout for connections in seconds
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        validate_data: Enable data quality validation
        progress_bar: Show progress bars for multiple fetches
    """
    
    # Retry settings
    retry_attempts: int = 20
    retry_delay: float = 0.5
    retry_backoff: float = 1.0
    
    # Parallel processing
    max_workers: int = 5
    
    # Cache settings
    cache_enabled: bool = True
    cache_max_age_hours: int = 24
    
    # Data fetching
    safety_buffer: float = 1.3
    min_bars_daily: int = 100
    min_bars_weekly: int = 20
    min_bars_monthly: int = 6
    min_bars_intraday: int = 500
    
    # Connection
    connection_timeout: int = 60
    
    # Logging & Validation
    log_level: str = 'ERROR'
    validate_data: bool = True
    progress_bar: bool = True
    
    def __post_init__(self):
        """Validate configuration values"""
        if self.retry_attempts < 1:
            raise ValueError("retry_attempts must be >= 1")
        
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be >= 0")
        
        if self.max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        
        if self.safety_buffer < 1.0:
            raise ValueError("safety_buffer must be >= 1.0")
        
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError(f"Invalid log_level: {self.log_level}")


@dataclass
class MarketConfig:
    """
    Market-specific configuration and exchange definitions
    
    Provides organized access to supported exchanges by region/market type
    """
    
    # Exchange groups
    EGYPT: List[str] = field(default_factory=lambda: ['EGX'])
    
    US: List[str] = field(default_factory=lambda: ['NASDAQ', 'NYSE', 'AMEX', 'OTC'])
    
    EUROPE: List[str] = field(default_factory=lambda: [
        'LSE', 'EURONEXT', 'XETRA', 'BME', 'SIX', 'FWB', 'MIL'
    ])
    
    ASIA: List[str] = field(default_factory=lambda: [
        'TSE', 'HKEX', 'SSE', 'SZSE', 'BSE', 'NSE', 'KRX', 'SGX', 'TWSE'
    ])
    
    MIDDLE_EAST: List[str] = field(default_factory=lambda: [
        'TADAWUL', 'DFM', 'ADX', 'QSE', 'TASE', 'MSM', 'BHB'
    ])
    
    AFRICA: List[str] = field(default_factory=lambda: [
        'JSE', 'CASE', 'NSE', 'EGX'
    ])
    
    CRYPTO: List[str] = field(default_factory=lambda: [
        'BINANCE', 'COINBASE', 'KRAKEN', 'BITFINEX', 'BITSTAMP', 'HUOBI'
    ])
    
    FOREX: List[str] = field(default_factory=lambda: [
        'FX_IDC', 'OANDA', 'FXCM', 'FX'
    ])
    
    COMMODITIES: List[str] = field(default_factory=lambda: [
        'COMEX', 'TVC', 'CME', 'NYMEX', 'CBOT'
    ])
    
    def get_all_exchanges(self) -> List[str]:
        """Get list of all supported exchanges"""
        all_exchanges = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, list) and not attr_name.startswith('_'):
                all_exchanges.extend(attr)
        return list(set(all_exchanges))  # Remove duplicates
    
    def get_region_exchanges(self, region: str) -> List[str]:
        """
        Get exchanges for a specific region
        
        Args:
            region: Region name (e.g., 'US', 'EUROPE', 'ASIA')
            
        Returns:
            List of exchange codes
        """
        region = region.upper()
        if hasattr(self, region):
            return getattr(self, region)
        return []
    
    def find_exchange(self, exchange_code: str) -> Optional[str]:
        """
        Find which region an exchange belongs to
        
        Args:
            exchange_code: Exchange code to search for
            
        Returns:
            Region name or None if not found
        """
        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue
            attr = getattr(self, attr_name)
            if isinstance(attr, list) and exchange_code in attr:
                return attr_name
        return None

"""
Core TradeGlob data fetcher

Main class for fetching market data from TradingView with advanced features:
- Authentication support
- Parallel/concurrent fetching
- Smart caching
- Comprehensive error handling
- Data validation
- Progress indicators
"""

import logging
import pandas as pd
from datetime import date, datetime
from typing import List, Optional, Union, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from retry import retry
import holidays

# Import tvDatafeed
try:
    from tvDatafeed import TvDatafeedLive, TvDatafeed, Interval
except ImportError:
    raise ImportError(
        "tvDatafeed not found. Install with: pip install tvDatafeed"
    )

# Import TradeGlob components
from .config import FetcherConfig, MarketConfig
from .utils.cache import DataCache
from .utils.validators import validate_inputs, validate_data_quality
from .utils.exceptions import (
    TradeGlobError,
    ConnectionError as TGConnectionError,
    NoDataError,
    ValidationError,
    AuthenticationError
)

logger = logging.getLogger(__name__)


class TradeGlobFetcher:
    """
    Universal market data fetcher for 3.5+ million instruments
    
    Features:
    - Supports 70+ stock exchanges, crypto, forex, commodities
    - Optional authentication for better stability
    - Parallel fetching (5x faster for multiple symbols)
    - Smart caching with automatic expiration
    - Comprehensive error handling and validation
    - Progress indicators for long-running operations
    
    Example:
        >>> fetcher = TradeGlobFetcher(username='user@email.com', password='pass')
        >>> df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=100)
        >>> df_multi = fetcher.get_multiple(['AAPL', 'MSFT'], 'NASDAQ', 'Daily', 
        ...                                  start=date(2024,1,1), end=date(2024,12,31))
    """
    
    # Interval mapping
    _interval_map = {
        '1 Minute': Interval.in_1_minute,
        '3 Minute': Interval.in_3_minute,
        '5 Minute': Interval.in_5_minute,
        '15 Minute': Interval.in_15_minute,
        '30 Minute': Interval.in_30_minute,
        '45 Minute': Interval.in_45_minute,
        '1 Hour': Interval.in_1_hour,
        '2 Hour': Interval.in_2_hour,
        '3 Hour': Interval.in_3_hour,
        '4 Hour': Interval.in_4_hour,
        'Daily': Interval.in_daily,
        'Weekly': Interval.in_weekly,
        'Monthly': Interval.in_monthly
    }
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        config: Optional[FetcherConfig] = None
    ):
        """
        Initialize TradeGlob fetcher
        
        Args:
            username: TradingView username (None for anonymous, free account recommended)
            password: TradingView password
            config: FetcherConfig object for customization
        """
        # Configuration
        self.config = config or FetcherConfig()
        
        # Setup logging
        logging.basicConfig(
            level=self.config.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Suppress tvDatafeed warnings
        logging.getLogger('tvDatafeed.main').setLevel(logging.ERROR)
        
        # Initialize TradingView connection
        try:
            self.tv = TvDatafeedLive(username=username, password=password)
            
            # Check if authentication actually succeeded
            # tvDatafeed sets token to "unauthorized_user_token" if login fails
            self.authenticated = (
                username is not None and 
                hasattr(self.tv, 'token') and 
                self.tv.token != "unauthorized_user_token" and
                self.tv.token is not None
            )
            
            if username is not None and not self.authenticated:
                logger.warning(
                    "⚠ Authentication failed. Continuing in anonymous mode. "
                    "Check your credentials or network connection."
                )
            elif self.authenticated:
                logger.info("✓ Initialized with authentication (better stability)")
            else:
                logger.warning(
                    "⚠ Initialized in anonymous mode. "
                    "For better stability, create a free TradingView account."
                )
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize TradingView connection: {e}")
        
        # Initialize cache
        self.cache = DataCache(enabled=self.config.cache_enabled)
        
        # Market configuration
        self.markets = MarketConfig()
        
        logger.info(f"TradeGlob v1.0.0 initialized")
    
    def _get_interval(self, interval: str) -> Interval:
        """Convert string interval to Interval enum"""
        if interval not in self._interval_map:
            raise ValidationError(
                f"Invalid interval: {interval}. "
                f"Valid: {', '.join(self._interval_map.keys())}"
            )
        return self._interval_map[interval]
    
    def _create_retry_wrapper(self, func):
        """Create retry wrapper with config settings"""
        return retry(
            Exception,
            tries=self.config.retry_attempts,
            delay=self.config.retry_delay,
            backoff=self.config.retry_backoff,
            logger=logger
        )(func)
    
    def _fetch_single(
        self,
        symbol: str,
        exchange: str,
        interval: Interval,
        n_bars: int,
        fut_contract: Optional[int] = None,
        extended_session: bool = False
    ) -> pd.DataFrame:
        """
        Fetch single symbol with retry logic
        
        This is the core fetch function with retry mechanism
        """
        @self._create_retry_wrapper
        def _fetch():
            df = self.tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=n_bars,
                fut_contract=fut_contract,
                extended_session=extended_session,
                timeout=self.config.connection_timeout
            )
            
            if df is None or df.empty:
                raise NoDataError(f"No data returned for {symbol}")
            
            return df
        
        return _fetch()
    
    def _calculate_optimal_bars(
        self,
        start: date,
        end: date,
        interval: str,
        exchange: str = 'EGX'
    ) -> int:
        """
        Calculate optimal n_bars with safety buffer
        
        Args:
            start: Start date
            end: End date
            interval: Time interval
            exchange: Exchange code (for holiday calculation)
            
        Returns:
            Optimal number of bars to request
        """
        # Try to get country from exchange for holiday calculation
        country_map = {
            # Middle East & Africa
            'EGX': 'EG',           # Egypt
            'TADAWUL': 'SA',       # Saudi Arabia
            'DFM': 'AE',           # UAE - Dubai
            'ADX': 'AE',           # UAE - Abu Dhabi
            'QSE': 'QA',           # Qatar
            'TASE': 'IL',          # Israel
            'JSE': 'ZA',           # South Africa
            'NGX': 'NG',           # Nigeria
            
            # North America
            'NASDAQ': 'US',        # US
            'NYSE': 'US',          # US
            'AMEX': 'US',          # US
            'TSX': 'CA',           # Canada
            'TSXV': 'CA',          # Canada Venture
            'BMV': 'MX',           # Mexico
            
            # Europe
            'LSE': 'GB',           # UK - London
            'XETR': 'DE',          # Germany - Xetra
            'FWB': 'DE',           # Germany - Frankfurt
            'EURONEXT': 'FR',      # France/Multi
            'MIL': 'IT',           # Italy - Milan
            'BME': 'ES',           # Spain - Madrid
            'SIX': 'CH',           # Switzerland
            'AMS': 'NL',           # Netherlands
            'OMXSTO': 'SE',        # Sweden
            'OMXHEX': 'FI',        # Finland
            'OMXCOP': 'DK',        # Denmark
            'OMXICE': 'IS',        # Iceland
            'GPW': 'PL',           # Poland
            'MOEX': 'RU',          # Russia
            'BIST': 'TR',          # Turkey
            
            # Asia Pacific
            'NSE': 'IN',           # India - National
            'BSE': 'IN',           # India - Bombay
            'TSE': 'JP',           # Japan - Tokyo
            'JPX': 'JP',           # Japan Exchange
            'HKEX': 'HK',          # Hong Kong
            'SSE': 'CN',           # China - Shanghai
            'SZSE': 'CN',          # China - Shenzhen
            'KRX': 'KR',           # South Korea
            'KOSDAQ': 'KR',        # South Korea - KOSDAQ
            'SGX': 'SG',           # Singapore
            'ASX': 'AU',           # Australia
            'NZX': 'NZ',           # New Zealand
            'SET': 'TH',           # Thailand
            'IDX': 'ID',           # Indonesia
            'MYX': 'MY',           # Malaysia
            'PSE': 'PH',           # Philippines
            'TWSE': 'TW',          # Taiwan
            'VNX': 'VN',           # Vietnam
            
            # Latin America
            'BOVESPA': 'BR',       # Brazil
            'BCBA': 'AR',          # Argentina
            'BCS': 'CL',           # Chile
            'BVC': 'CO',           # Colombia
            'BVL': 'PE',           # Peru
        }
        
        country = country_map.get(exchange.upper(), 'US')
        
        try:
            hol = holidays.country_holidays(country)
            working_days = hol.get_working_days_count(start, end)
        except:
            # Fallback: estimate 5/7 of days as working days
            total_days = (end - start).days
            working_days = int(total_days * 5 / 7)
        
        # Set minimums based on interval
        if 'Minute' in interval or 'Hour' in interval:
            min_bars = self.config.min_bars_intraday
        elif interval == 'Daily':
            min_bars = self.config.min_bars_daily
        elif interval == 'Weekly':
            min_bars = self.config.min_bars_weekly
        elif interval == 'Monthly':
            min_bars = self.config.min_bars_monthly
        else:
            min_bars = 100
        
        # Apply minimum
        n_bars = max(working_days, min_bars)
        
        # Add safety buffer
        n_bars = int(n_bars * self.config.safety_buffer)
        
        # Cap at TradingView limit
        n_bars = min(n_bars, 5000)
        
        logger.debug(
            f"Calculated n_bars={n_bars} for {interval} "
            f"from {start} to {end} (working_days={working_days})"
        )
        
        return n_bars
    
    def get_ohlcv(
        self,
        symbol: str,
        exchange: str,
        interval: str,
        n_bars: int = 100,
        use_cache: bool = True,
        validate: bool = True
    ) -> pd.DataFrame:
        """
        Get OHLCV data for a single symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'COMI')
            exchange: Exchange code (e.g., 'NASDAQ', 'EGX')
            interval: Time interval ('Daily', 'Weekly', 'Monthly', '1 Minute', etc.)
            n_bars: Number of bars to fetch (max 5000)
            use_cache: Use cached data if available
            validate: Validate data quality
            
        Returns:
            DataFrame with columns: [symbol, open, high, low, close, volume]
            
        Raises:
            ValidationError: Invalid input parameters
            ConnectionError: Failed to connect to TradingView
            NoDataError: No data available for symbol
            
        Example:
            >>> df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=252)
            >>> print(df.tail())
        """
        # Validate inputs
        validate_inputs(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
        
        # Check cache
        if use_cache and self.cache.enabled:
            cached = self.cache.get(symbol, exchange, interval, n_bars)
            if cached is not None:
                return cached
        
        # Fetch data
        try:
            interval_enum = self._get_interval(interval)
            df = self._fetch_single(symbol, exchange, interval_enum, n_bars)
            
            logger.info(f"✓ Fetched {symbol}: {len(df)} rows")
            
            # Validate data quality
            if validate and self.config.validate_data:
                quality = validate_data_quality(df, symbol)
                if not quality['passed']:
                    logger.warning(f"{symbol} has quality issues: {quality['issues']}")
            
            # Cache the result
            if use_cache and self.cache.enabled:
                self.cache.set(symbol, exchange, interval, n_bars, df)
            
            return df
            
        except NoDataError:
            raise
        except Exception as e:
            logger.error(f"✗ Failed to fetch {symbol}: {str(e)}")
            raise TGConnectionError(f"Failed to fetch {symbol}: {str(e)}") from e
    
    def get_multiple(
        self,
        stock_list: List[str],
        exchange: str,
        interval: str,
        start: date,
        end: date,
        columns: Union[str, List[str]] = 'close',
        parallel: bool = True,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Get data for multiple symbols
        
        Args:
            stock_list: List of stock symbols
            exchange: Exchange code
            interval: Time interval
            start: Start date
            end: End date
            columns: Columns to return: 'close', 'all', or list like ['open', 'close']
            parallel: Use parallel fetching (faster)
            use_cache: Use cached data if available
            
        Returns:
            DataFrame with dates as index and stocks as columns
            If columns='all', returns MultiIndex columns (symbol, column)
            
        Example:
            >>> df = fetcher.get_multiple(
            ...     ['AAPL', 'MSFT', 'GOOGL'],
            ...     'NASDAQ',
            ...     'Daily',
            ...     date(2024, 1, 1),
            ...     date(2024, 12, 31)
            ... )
        """
        # Validate inputs
        validate_inputs(
            exchange=exchange,
            interval=interval,
            start=start,
            end=end,
            stock_list=stock_list
        )
        
        # Calculate optimal n_bars
        n_bars = self._calculate_optimal_bars(start, end, interval, exchange)
        
        logger.info(
            f"Fetching {len(stock_list)} symbols from {exchange} "
            f"({interval}, {start} to {end})"
        )
        
        # Fetch data
        if parallel and len(stock_list) > 1:
            results = self._fetch_parallel(
                stock_list, exchange, interval, n_bars, columns, use_cache
            )
        else:
            results = self._fetch_sequential(
                stock_list, exchange, interval, n_bars, columns, use_cache
            )
        
        if not results:
            raise NoDataError("Failed to fetch any symbols")
        
        # Combine results
        df = pd.concat(results, axis=1)
        
        # Ensure datetime index
        df.index = pd.to_datetime(df.index)
        df.index.name = 'Date'
        
        # Filter by date range
        df = df.loc[start:end]
        
        logger.info(f"✓ Combined data: {len(df)} rows, {len(df.columns)} columns")
        
        return df
    
    def _fetch_parallel(
        self,
        stock_list: List[str],
        exchange: str,
        interval: str,
        n_bars: int,
        columns: Union[str, List[str]],
        use_cache: bool
    ) -> Dict[str, pd.Series]:
        """Fetch multiple symbols in parallel"""
        results = {}
        failed = []
        
        interval_enum = self._get_interval(interval)
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_stock = {
                executor.submit(
                    self._fetch_single_cached,
                    stock, exchange, interval, interval_enum, n_bars, use_cache
                ): stock
                for stock in stock_list
            }
            
            # Process completions with optional progress bar
            if self.config.progress_bar:
                try:
                    from tqdm import tqdm
                    iterator = tqdm(
                        as_completed(future_to_stock),
                        total=len(stock_list),
                        desc="Fetching"
                    )
                except ImportError:
                    iterator = as_completed(future_to_stock)
            else:
                iterator = as_completed(future_to_stock)
            
            for future in iterator:
                stock = future_to_stock[future]
                try:
                    df = future.result(timeout=self.config.connection_timeout)
                    
                    # Extract requested columns
                    if columns == 'close':
                        results[stock] = df['close']
                    elif columns == 'all':
                        for col in ['open', 'high', 'low', 'close', 'volume']:
                            if col in df.columns:
                                results[(stock, col)] = df[col]
                    elif isinstance(columns, list):
                        for col in columns:
                            if col in df.columns:
                                results[(stock, col)] = df[col]
                    else:
                        results[stock] = df['close']
                    
                    logger.debug(f"✓ {stock}: {len(df)} rows")
                    
                except Exception as e:
                    failed.append(stock)
                    logger.error(f"✗ {stock}: {str(e)[:100]}")
        
        if failed:
            logger.warning(f"Failed to fetch {len(failed)}/{len(stock_list)} symbols: {failed}")
        
        return results
    
    def _fetch_sequential(
        self,
        stock_list: List[str],
        exchange: str,
        interval: str,
        n_bars: int,
        columns: Union[str, List[str]],
        use_cache: bool
    ) -> Dict[str, pd.Series]:
        """Fetch multiple symbols sequentially"""
        results = {}
        failed = []
        
        interval_enum = self._get_interval(interval)
        
        # Optional progress bar
        if self.config.progress_bar:
            try:
                from tqdm import tqdm
                iterator = tqdm(stock_list, desc="Fetching")
            except ImportError:
                iterator = stock_list
        else:
            iterator = stock_list
        
        for stock in iterator:
            try:
                df = self._fetch_single_cached(
                    stock, exchange, interval, interval_enum, n_bars, use_cache
                )
                
                # Extract requested columns
                if columns == 'close':
                    results[stock] = df['close']
                elif columns == 'all':
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        if col in df.columns:
                            results[(stock, col)] = df[col]
                elif isinstance(columns, list):
                    for col in columns:
                        if col in df.columns:
                            results[(stock, col)] = df[col]
                else:
                    results[stock] = df['close']
                
                logger.debug(f"✓ {stock}: {len(df)} rows")
                
            except Exception as e:
                failed.append(stock)
                logger.error(f"✗ {stock}: {str(e)[:100]}")
        
        if failed:
            logger.warning(f"Failed to fetch {len(failed)}/{len(stock_list)} symbols: {failed}")
        
        return results
    
    def _fetch_single_cached(
        self,
        symbol: str,
        exchange: str,
        interval: str,
        interval_enum: Interval,
        n_bars: int,
        use_cache: bool
    ) -> pd.DataFrame:
        """Fetch single symbol with cache check"""
        # Check cache
        if use_cache and self.cache.enabled:
            cached = self.cache.get(symbol, exchange, interval, n_bars)
            if cached is not None:
                return cached
        
        # Fetch data
        df = self._fetch_single(symbol, exchange, interval_enum, n_bars)
        
        # Cache the result
        if use_cache and self.cache.enabled:
            self.cache.set(symbol, exchange, interval, n_bars, df)
        
        return df
    
    def search_symbol(self, text: str, exchange: str = '') -> List[dict]:
        """
        Search for symbols on TradingView
        
        Args:
            text: Search text (e.g., 'apple', 'aramco')
            exchange: Filter by exchange (optional)
            
        Returns:
            List of matching symbols with details
            
        Example:
            >>> results = fetcher.search_symbol('apple', 'NASDAQ')
            >>> print(results[0]['symbol'])  # 'AAPL'
        """
        try:
            return self.tv.search_symbol(text, exchange)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_cache_info(self) -> dict:
        """Get cache statistics"""
        return self.cache.get_cache_info()
    
    def clear_cache(self, symbol: Optional[str] = None, exchange: Optional[str] = None):
        """
        Clear cache
        
        Args:
            symbol: Clear specific symbol (None = all)
            exchange: Clear specific exchange (None = all)
        """
        if symbol or exchange:
            self.cache.invalidate(symbol, exchange)
        else:
            self.cache.clear()

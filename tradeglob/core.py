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
import requests
import json
from datetime import date, datetime
from typing import List, Optional, Union, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from retry import retry
import holidays

# Import fixed tvDatafeed (vendored, Selenium 4.x compatible)
from ._vendor.main import TvDatafeed as TvDatafeedLive, Interval

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
        auth: bool = False,
        config: Optional[FetcherConfig] = None
    ):
        """
        Initialize TradeGlob fetcher
        
        Args:
            username: TradingView username (None for anonymous, free account recommended)
            password: TradingView password
            auth: If True, opens browser for authentication immediately (fast auto-login)
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
            # Only create connection if credentials provided
            if username is not None:
                self.tv = TvDatafeedLive(username=username, password=password)
                
                # Check if authentication actually succeeded
                self.authenticated = (
                    hasattr(self.tv, 'token') and 
                    self.tv.token != "unauthorized_user_token" and
                    self.tv.token is not None
                )
                
                if not self.authenticated:
                    logger.warning(
                        "⚠ Authentication failed. Continuing in anonymous mode. "
                        "Check your credentials or network connection."
                    )
                else:
                    logger.info("✓ Initialized with authentication")
            elif auth:
                # Browser-based authentication requested
                self.tv = TvDatafeedLive(username=username, password=password, auto_login=False)
                
                # Check if authentication succeeded
                self.authenticated = (
                    hasattr(self.tv, 'token') and 
                    self.tv.token != "unauthorized_user_token" and
                    self.tv.token is not None
                )
                
                if self.authenticated:
                    logger.info("✓ Initialized with browser authentication")
                else:
                    logger.warning("⚠ Browser authentication failed, using anonymous mode")
            else:
                # Start in lazy mode - don't create connection until needed
                self.tv = None
                self.authenticated = False
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize TradingView connection: {e}")
        
        # Initialize cache
        self.cache = DataCache(enabled=self.config.cache_enabled)
        
        # Market configuration
        self.markets = MarketConfig()
        
        logger.info(f"TradeGlob v1.0.0 initialized")
    
    def authenticate(self, username: str = None, password: str = None, force_new: bool = False) -> bool:
        """
        Authenticate with TradingView account
        
        Opens Chrome browser for manual login - fast and automatic detection.
        
        Args:
            username: TradingView username/email (optional)
            password: TradingView password (optional)
            force_new: If True, clears cached token and forces new login
            
        Returns:
            bool: True if authentication successful
        """
        try:
            # Clear cached token if requested
            if force_new:
                import os
                token_file = os.path.join(os.path.expanduser("~"), ".tv_datafeed", "token")
                if os.path.exists(token_file):
                    os.remove(token_file)
            
            # Create or replace connection with authenticated one
            self.tv = TvDatafeedLive(username=username, password=password, auto_login=False)
            
            # Check authentication status
            self.authenticated = (
                hasattr(self.tv, 'token') and 
                self.tv.token != "unauthorized_user_token" and
                self.tv.token is not None
            )
            
            return self.authenticated
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            self.authenticated = False
            return False
    
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
    
    def _ensure_connection(self):
        """Ensure tv connection exists (lazy initialization)"""
        if self.tv is None:
            self.tv = TvDatafeedLive()
            self.authenticated = False
    
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
        
        Ensures connection is initialized before fetching.
        
        This is the core fetch function with retry mechanism
        """
        self._ensure_connection()
        
        @self._create_retry_wrapper
        def _fetch():
            df = self.tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=n_bars,
                fut_contract=fut_contract,
                extended_session=extended_session
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
    
    def export_data(
        self,
        df: pd.DataFrame,
        filepath: str,
        format: str = 'csv',
        **kwargs
    ) -> str:
        """
        Export DataFrame to various formats
        
        Args:
            df: DataFrame to export
            filepath: Output file path
            format: Export format ('csv', 'excel', 'parquet', 'json', 'hdf5')
            **kwargs: Additional format-specific arguments
            
        Returns:
            Absolute path to created file
            
        Example:
            >>> df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)
            >>> fetcher.export_data(df, 'aapl_data.csv')
            >>> fetcher.export_data(df, 'aapl_data.xlsx', format='excel')
            >>> fetcher.export_data(df, 'aapl_data.parquet', format='parquet')
        """
        from .utils.export import (
            export_to_csv, export_to_excel, export_to_parquet,
            export_to_json, export_to_hdf5
        )
        
        format_lower = format.lower()
        
        if format_lower == 'csv':
            return export_to_csv(df, filepath, **kwargs)
        elif format_lower in ['excel', 'xlsx']:
            return export_to_excel(df, filepath, **kwargs)
        elif format_lower == 'parquet':
            return export_to_parquet(df, filepath, **kwargs)
        elif format_lower == 'json':
            return export_to_json(df, filepath, **kwargs)
        elif format_lower in ['hdf5', 'h5']:
            return export_to_hdf5(df, filepath, **kwargs)
        else:
            raise ValidationError(
                f"Unknown format: {format}. "
                f"Supported: csv, excel, parquet, json, hdf5"
            )
    
    def export_multi_format(
        self,
        df: pd.DataFrame,
        base_path: str,
        formats: List[str] = ['csv', 'parquet'],
        **kwargs
    ) -> Dict[str, str]:
        """
        Export DataFrame to multiple formats at once
        
        Args:
            df: DataFrame to export
            base_path: Base path (without extension)
            formats: List of formats to export
            **kwargs: Additional export arguments
            
        Returns:
            Dict of {format: filepath}
            
        Example:
            >>> df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)
            >>> paths = fetcher.export_multi_format(
            ...     df, 'aapl_data',
            ...     formats=['csv', 'excel', 'parquet']
            ... )
            >>> # Creates: aapl_data.csv, aapl_data.xlsx, aapl_data.parquet
        """
        from .utils.export import export_multi_format
        return export_multi_format(df, base_path, formats, **kwargs)
    
    def search_symbol(self, text: str, exchange: str = '') -> List[dict]:
        """Search for symbols on TradingView
        
        Args:
            text: Search query (e.g., 'AAPL', 'apple', 'COMI')
            exchange: Optional exchange filter (e.g., 'NASDAQ', 'EGX', '')
                     Empty string searches all exchanges
        
        Returns:
            List of dictionaries with symbol information:
            [
                {
                    'symbol': 'COMI',
                    'exchange': 'EGX',
                    'description': 'Commercial International Bank Egypt',
                    'type': 'stock',
                    ...
                },
                ...
            ]
        
        Example:
            >>> # Search all exchanges
            >>> results = fetcher.search_symbol('COMI')
            
            >>> # Search specific exchange
            >>> results = fetcher.search_symbol('COMI', 'EGX')
            >>> if results:
            ...     print(f"Symbol: {results[0]['symbol']}")
            ...     print(f"Exchange: {results[0]['exchange']}")
            ...     print(f"Description: {results[0]['description']}")
        """
        url = f'https://symbol-search.tradingview.com/symbol_search/?text={text}&hl=1&exchange={exchange}&lang=en&type=&domain=production'
        
        # Add headers required by TradingView API
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Origin': 'https://www.tradingview.com',
            'Referer': 'https://www.tradingview.com/'
        }
        
        symbols_list = []
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                logger.error(f"Symbol search HTTP error: {resp.status_code}")
                return []
            
            if not resp.text or resp.text.strip() == '':
                logger.error("Symbol search: Empty response from API")
                return []
            
            # Remove HTML tags and parse JSON
            symbols_list = json.loads(resp.text.replace('</em>', '').replace('<em>', ''))
            
            logger.debug(f"Found {len(symbols_list)} symbols for '{text}' on '{exchange or 'all exchanges'}'")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Symbol search network error: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Symbol search JSON parse error: {e}")
        except Exception as e:
            logger.error(f"Symbol search error: {e}")
        
        return symbols_list

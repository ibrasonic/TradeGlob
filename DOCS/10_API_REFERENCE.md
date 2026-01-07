# API Reference

Complete reference for all TradeGlob functions and classes.

## TradeGlobFetcher

Main class for fetching market data and calculating technical indicators.

### Constructor

```python
TradeGlobFetcher(
    username: Optional[str] = None,
    password: Optional[str] = None,
    auth: bool = False,
    config: Optional[FetcherConfig] = None
)
```

**Parameters:**
- `username` (str, optional): TradingView username/email for authentication
- `password` (str, optional): TradingView password
- `auth` (bool): If True, opens browser for authentication immediately
- `config` (FetcherConfig, optional): Custom configuration object

**Returns:** TradeGlobFetcher instance

**Example:**
```python
# Anonymous mode
fetcher = TradeGlobFetcher()

# With authentication
fetcher = TradeGlobFetcher(username='user@email.com', password='pass')

# Browser-based auth
fetcher = TradeGlobFetcher(auth=True)
```

---

### Methods

## authenticate()

Authenticate with TradingView account via browser.

```python
authenticate(
    username: str = None,
    password: str = None,
    force_new: bool = False
) -> bool
```

**Parameters:**
- `username` (str, optional): TradingView username
- `password` (str, optional): TradingView password  
- `force_new` (bool): Force new login by clearing cached token

**Returns:** bool - True if authentication successful

**Example:**
```python
fetcher = TradeGlobFetcher()
success = fetcher.authenticate()
if success:
    print("✓ Authenticated")
```

---

## get_ohlcv()

Fetch OHLCV data for a single symbol.

```python
get_ohlcv(
    symbol: str,
    exchange: str,
    interval: str,
    n_bars: int = 100,
    use_cache: bool = True,
    validate: bool = True
) -> pd.DataFrame
```

**Parameters:**
- `symbol` (str): Stock symbol (e.g., 'AAPL', 'COMI')
- `exchange` (str): Exchange code (e.g., 'NASDAQ', 'EGX')
- `interval` (str): Time interval - see [Valid Intervals](#valid-intervals)
- `n_bars` (int): Number of bars to fetch (max 5000)
- `use_cache` (bool): Use cached data if available
- `validate` (bool): Validate data quality

**Returns:** pd.DataFrame with columns: [symbol, open, high, low, close, volume]

**Raises:**
- `ValidationError`: Invalid input parameters
- `ConnectionError`: Failed to connect to TradingView
- `NoDataError`: No data available for symbol

**Example:**
```python
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=252)
print(df.tail())
```

---

## get_multiple()

Fetch data for multiple symbols with date range.

```python
get_multiple(
    stock_list: List[str],
    exchange: str,
    interval: str,
    start: date,
    end: date,
    columns: Union[str, List[str]] = 'close',
    parallel: bool = True,
    use_cache: bool = True
) -> pd.DataFrame
```

**Parameters:**
- `stock_list` (List[str]): List of stock symbols
- `exchange` (str): Exchange code
- `interval` (str): Time interval
- `start` (date): Start date
- `end` (date): End date
- `columns` (str or List[str]): Columns to return:
  - `'close'`: Close prices only (default)
  - `'all'`: All OHLCV columns
  - List of columns: ['open', 'close', 'volume']
- `parallel` (bool): Use parallel fetching (5x faster)
- `use_cache` (bool): Use cached data if available

**Returns:** pd.DataFrame with dates as index, symbols as columns

**Example:**
```python
from datetime import date

stocks = ['AAPL', 'MSFT', 'GOOGL']
df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)
```

---

## ta()

Calculate 130+ technical indicators on OHLCV data.

```python
ta(
    df: Optional[pd.DataFrame] = None,
    symbol: Optional[str] = None,
    exchange: Optional[str] = None,
    interval: Optional[str] = None,
    n_bars: int = 200,
    indicators: Union[str, List[str]] = 'common',
    append: bool = False,
    **kwargs
) -> pd.DataFrame
```

**Parameters:**
- `df` (pd.DataFrame, optional): DataFrame with OHLCV data (if None, will fetch)
- `symbol` (str, optional): Stock symbol (for auto-fetch if df is None)
- `exchange` (str, optional): Exchange code (for auto-fetch)
- `interval` (str, optional): Time interval (for auto-fetch)
- `n_bars` (int): Number of bars to fetch if auto-fetching
- `indicators` (str or List[str]): Which indicators to calculate:
  - `'common'`: 20 most common indicators (default)
  - `'all'`: All 130+ indicators
  - `'momentum'`, `'trend'`, `'volatility'`, `'volume'`, `'overlap'`: Category-specific
  - List: ['RSI', 'MACD', 'SMA', 'EMA']
- `append` (bool): If True, append to DataFrame; if False, return only indicators
- `**kwargs`: Additional arguments for specific indicators

**Returns:** pd.DataFrame with calculated indicators

**Example:**
```python
# Auto-fetch and calculate
df = fetcher.ta(
    symbol='AAPL',
    exchange='NASDAQ',
    interval='Daily',
    n_bars=100,
    indicators='common'
)

# Use existing DataFrame
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)
df_with_ta = fetcher.ta(df=df, indicators='common', append=True)

# Specific indicators
df = fetcher.ta(df=df, indicators=['RSI', 'MACD', 'SMA'])
```

---

## search_symbol()

Search for symbols on TradingView.

```python
search_symbol(
    text: str,
    exchange: str = ''
) -> List[dict]
```

**Parameters:**
- `text` (str): Search query (e.g., 'AAPL', 'apple', 'bitcoin')
- `exchange` (str): Optional exchange filter (empty = all exchanges)

**Returns:** List[dict] - List of symbol information dictionaries

**Example:**
```python
# Search all exchanges
results = fetcher.search_symbol('apple')

# Search specific exchange
results = fetcher.search_symbol('COMI', 'EGX')
if results:
    print(f"Symbol: {results[0]['symbol']}")
    print(f"Exchange: {results[0]['exchange']}")
    print(f"Description: {results[0]['description']}")
```

---

## export_data()

Export DataFrame to various formats.

```python
export_data(
    df: pd.DataFrame,
    filepath: str,
    format: str = 'csv',
    **kwargs
) -> str
```

**Parameters:**
- `df` (pd.DataFrame): DataFrame to export
- `filepath` (str): Output file path
- `format` (str): Export format - 'csv', 'excel', 'parquet', 'json', 'hdf5'
- `**kwargs`: Additional format-specific arguments

**Returns:** str - Absolute path to created file

**Example:**
```python
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)

fetcher.export_data(df, 'aapl.csv')
fetcher.export_data(df, 'aapl.xlsx', format='excel')
fetcher.export_data(df, 'aapl.parquet', format='parquet')
```

---

## export_multi_format()

Export DataFrame to multiple formats simultaneously.

```python
export_multi_format(
    df: pd.DataFrame,
    base_path: str,
    formats: List[str] = ['csv', 'parquet'],
    **kwargs
) -> Dict[str, str]
```

**Parameters:**
- `df` (pd.DataFrame): DataFrame to export
- `base_path` (str): Base path without extension
- `formats` (List[str]): List of formats to export
- `**kwargs`: Additional export arguments

**Returns:** Dict[str, str] - {format: filepath} mapping

**Example:**
```python
paths = fetcher.export_multi_format(
    df,
    'aapl_data',
    formats=['csv', 'excel', 'parquet']
)
# Creates: aapl_data.csv, aapl_data.xlsx, aapl_data.parquet
```

---

## get_cache_info()

Get cache statistics.

```python
get_cache_info() -> dict
```

**Returns:** dict - Cache statistics (enabled, location, files, size_mb, oldest, newest)

**Example:**
```python
info = fetcher.get_cache_info()
print(f"Cache location: {info['location']}")
print(f"Cached files: {info['files']}")
print(f"Cache size: {info['size_mb']:.2f} MB")
```

---

## clear_cache()

Clear cached data.

```python
clear_cache(
    symbol: Optional[str] = None,
    exchange: Optional[str] = None
)
```

**Parameters:**
- `symbol` (str, optional): Clear specific symbol (None = all)
- `exchange` (str, optional): Clear specific exchange (None = all)

**Example:**
```python
# Clear all cache
fetcher.clear_cache()

# Clear specific symbol
fetcher.clear_cache(symbol='AAPL')

# Clear specific exchange
fetcher.clear_cache(exchange='NASDAQ')
```

---

## Configuration Classes

### FetcherConfig

Customize fetcher behavior.

```python
from tradeglob import FetcherConfig

config = FetcherConfig(
    retry_attempts=20,
    max_workers=5,
    cache_enabled=True,
    cache_max_age_hours=24,
    log_level='ERROR',
    validate_data=True,
    progress_bar=True
)

fetcher = TradeGlobFetcher(config=config)
```

**Parameters:**
- `retry_attempts` (int): Number of retry attempts (default: 20)
- `retry_delay` (float): Delay between retries in seconds (default: 0.5)
- `retry_backoff` (float): Backoff multiplier (default: 1.0)
- `max_workers` (int): Max parallel workers (default: 5)
- `cache_enabled` (bool): Enable caching (default: True)
- `cache_max_age_hours` (int): Cache expiration hours (default: 24)
- `safety_buffer` (float): Safety multiplier for n_bars (default: 1.3)
- `connection_timeout` (int): Connection timeout seconds (default: 60)
- `log_level` (str): Logging level - DEBUG, INFO, WARNING, ERROR (default: ERROR)
- `validate_data` (bool): Enable validation (default: True)
- `progress_bar` (bool): Show progress bars (default: True)

---

### MarketConfig

Access exchange definitions by region.

```python
from tradeglob import MarketConfig

market = MarketConfig()

# Get all exchanges
all_exchanges = market.get_all_exchanges()

# Get exchanges by region
us_exchanges = market.get_region_exchanges('US')

# Find which region an exchange belongs to
region = market.find_exchange('NASDAQ')  # Returns 'US'
```

---

## Valid Intervals

### Intraday
- `'1 Minute'`
- `'3 Minute'`
- `'5 Minute'`
- `'15 Minute'`
- `'30 Minute'`
- `'45 Minute'`
- `'1 Hour'`
- `'2 Hour'`
- `'3 Hour'`
- `'4 Hour'`

### Daily+
- `'Daily'`
- `'Weekly'`
- `'Monthly'`

---

## Exception Classes

### TradeGlobError
Base exception for all TradeGlob errors.

### ConnectionError
Connection to TradingView failed.

### NoDataError
No data returned for requested symbol.

### ValidationError
Input validation failed.

### AuthenticationError
TradingView authentication failed.

**Example:**
```python
from tradeglob import NoDataError, ConnectionError, ValidationError

try:
    df = fetcher.get_ohlcv('INVALID', 'NASDAQ', 'Daily', 100)
except NoDataError:
    print("Symbol not found")
except ConnectionError:
    print("Network issue")
except ValidationError:
    print("Invalid parameters")
```

---

## See Also

- [Quick Start Guide](01_QUICK_START.md)
- [Technical Analysis Guide](05_TECHNICAL_ANALYSIS.md)
- [Configuration Guide](07_CONFIGURATION.md)

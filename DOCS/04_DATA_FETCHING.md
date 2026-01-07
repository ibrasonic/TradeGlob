# Data Fetching Guide

Complete guide to fetching market data with TradeGlob.

## Core Concepts

### Symbol Format

Symbols follow TradingView conventions:
- **Stocks**: `'AAPL'`, `'MSFT'`, `'COMI'`
- **Crypto**: `'BTCUSDT'`, `'ETHUSD'`, `'BNBUSDT'`
- **Forex**: `'EURUSD'`, `'GBPJPY'`, `'USDJPY'`
- **Commodities**: `'GOLD'`, `'CRUDE_OIL'`
- **Indices**: `'SPX'`, `'NDX'`, `'DJI'`

### Exchange Codes

Common exchange codes:
- **US**: `'NASDAQ'`, `'NYSE'`, `'AMEX'`, `'OTC'`
- **Europe**: `'LSE'`, `'XETRA'`, `'EURONEXT'`
- **Asia**: `'TSE'`, `'HKEX'`, `'SSE'`, `'KRX'`
- **Middle East**: `'TADAWUL'`, `'ADX'`, `'DFM'`, `'EGX'`
- **Crypto**: `'BINANCE'`, `'COINBASE'`, `'KRAKEN'`

See [Market Coverage](09_MARKET_COVERAGE.md) for complete list.

---

## Single Symbol Fetching

### Basic Usage

```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()

# Fetch 100 days of Apple stock
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=100)
```

### Return Format

DataFrame with these columns:
- `symbol` - Stock symbol
- `open` - Opening price
- `high` - Highest price
- `low` - Lowest price
- `close` - Closing price
- `volume` - Trading volume

Index: `Date` (datetime)

### Different Intervals

```python
# Daily data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=252)

# Hourly data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', '1 Hour', n_bars=100)

# 15-minute data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', '15 Minute', n_bars=100)

# Weekly data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Weekly', n_bars=52)
```

**Valid intervals:**
- Intraday: `'1 Minute'`, `'5 Minute'`, `'15 Minute'`, `'30 Minute'`, `'1 Hour'`, `'4 Hour'`
- Daily+: `'Daily'`, `'Weekly'`, `'Monthly'`

### Custom Bar Count

```python
# Last 30 days
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=30)

# Last year (approx 252 trading days)
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=252)

# Maximum allowed (5000 bars)
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=5000)
```

⚠️ **Note:** TradingView limits to 5000 bars maximum.

---

## Multiple Symbols Fetching

### Basic Multi-Symbol Fetch

```python
from tradeglob import TradeGlobFetcher
from datetime import date

fetcher = TradeGlobFetcher()

stocks = ['AAPL', 'MSFT', 'GOOGL']

df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)
```

**Return format:**
```
            AAPL   MSFT   GOOGL
Date                           
2024-01-01  150.2  320.5   95.3
2024-01-02  151.5  322.8   96.1
...
```

### Close Prices Only (Default)

```python
# Returns only close prices (most common use case)
df = fetcher.get_multiple(
    stock_list=['AAPL', 'MSFT'],
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    columns='close'  # Default
)
```

### All OHLCV Columns

```python
# Returns all OHLCV data
df = fetcher.get_multiple(
    stock_list=['AAPL', 'MSFT'],
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    columns='all'
)

# Multi-level columns: (symbol, column)
# Access: df[('AAPL', 'close')] or df['AAPL']['close']
```

### Specific Columns

```python
# Get only specific columns
df = fetcher.get_multiple(
    stock_list=['AAPL', 'MSFT'],
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    columns=['open', 'close', 'volume']
)
```

### Parallel Processing

```python
# Parallel fetching (5x faster for multiple stocks)
df = fetcher.get_multiple(
    stock_list=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    parallel=True  # Default
)
```

**Performance:**
- 5 stocks, serial: ~15 seconds
- 5 stocks, parallel: ~3 seconds

---

## Symbol Search

### Find Symbols

```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()

# Search all exchanges
results = fetcher.search_symbol('apple')

for result in results[:3]:
    print(f"{result['symbol']} - {result['exchange']} - {result['description']}")
```

**Output:**
```
AAPL - NASDAQ - Apple Inc.
AAPL - BATS - Apple Inc.
APC - XETRA - Apple Inc.
```

### Search Specific Exchange

```python
# Search only in EGX
results = fetcher.search_symbol('commercial', 'EGX')

if results:
    print(f"Found: {results[0]['symbol']}")
    # Use this symbol
    df = fetcher.get_ohlcv(results[0]['symbol'], 'EGX', 'Daily', 100)
```

### Crypto Symbol Search

```python
# Find Bitcoin trading pairs
results = fetcher.search_symbol('bitcoin', 'BINANCE')

for result in results[:5]:
    print(result['symbol'])
# BTCUSDT, BTCBUSD, BTCEUR, etc.
```

---

## Date Ranges

### Using Date Objects

```python
from datetime import date

df = fetcher.get_multiple(
    stock_list=['AAPL'],
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)
```

### Dynamic Date Ranges

```python
from datetime import date, timedelta

# Last 30 days
end_date = date.today()
start_date = end_date - timedelta(days=30)

df = fetcher.get_multiple(
    stock_list=['AAPL'],
    exchange='NASDAQ',
    interval='Daily',
    start=start_date,
    end=end_date
)
```

### Year-to-Date

```python
from datetime import date

df = fetcher.get_multiple(
    stock_list=['AAPL', 'MSFT'],
    exchange='NASDAQ',
    interval='Daily',
    start=date(date.today().year, 1, 1),
    end=date.today()
)
```

---

## Advanced Fetching

### Custom Configuration

```python
from tradeglob import TradeGlobFetcher, FetcherConfig

# Create custom config
config = FetcherConfig(
    retry_attempts=30,       # More retries
    max_workers=10,          # More parallel workers
    cache_max_age_hours=48,  # Cache for 2 days
    progress_bar=True        # Show progress
)

fetcher = TradeGlobFetcher(config=config)
```

### Disable Caching

```python
# Disable cache for specific request
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100, use_cache=False)

# Disable globally
config = FetcherConfig(cache_enabled=False)
fetcher = TradeGlobFetcher(config=config)
```

### Disable Validation

```python
# Skip validation (faster, but less safe)
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100, validate=False)
```

---

## Handling Missing Data

### Check for Missing Values

```python
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)

# Check for NaN values
if df.isnull().any().any():
    print("Warning: Missing values detected")
    print(df.isnull().sum())
```

### Fill Missing Values

```python
# Forward fill
df_filled = df.fillna(method='ffill')

# Backward fill
df_filled = df.fillna(method='bfill')

# Interpolate
df_filled = df.interpolate()
```

### Drop Missing Values

```python
# Drop rows with any NaN
df_clean = df.dropna()

# Drop rows where close is NaN
df_clean = df.dropna(subset=['close'])
```

---

## Data Validation

### Automatic Validation

TradeGlob validates:
- ✓ No duplicate timestamps
- ✓ OHLC relationships (high ≥ low, etc.)
- ✓ Non-negative prices/volume
- ✓ Reasonable date ranges

```python
# Validation enabled by default
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100, validate=True)
```

### Manual Validation

```python
# Check OHLC consistency
valid_ohlc = (df['high'] >= df['low']).all()
valid_close = ((df['close'] >= df['low']) & (df['close'] <= df['high'])).all()

if not (valid_ohlc and valid_close):
    print("Warning: Invalid OHLC data detected")
```

---

## Working with Different Markets

### US Stocks

```python
# NASDAQ
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)

# NYSE
df = fetcher.get_ohlcv('IBM', 'NYSE', 'Daily', 100)
```

### European Stocks

```python
# London Stock Exchange
df = fetcher.get_ohlcv('BP', 'LSE', 'Daily', 100)

# Frankfurt (XETRA)
df = fetcher.get_ohlcv('SAP', 'XETRA', 'Daily', 100)
```

### Middle East Stocks

```python
# Egyptian Exchange
df = fetcher.get_ohlcv('COMI', 'EGX', 'Daily', 100)

# Saudi Stock Exchange
df = fetcher.get_ohlcv('2222', 'TADAWUL', 'Daily', 100)

# Dubai Financial Market
df = fetcher.get_ohlcv('EMAAR', 'DFM', 'Daily', 100)
```

### Cryptocurrency

```python
# Binance
df = fetcher.get_ohlcv('BTCUSDT', 'BINANCE', 'Daily', 100)

# Coinbase
df = fetcher.get_ohlcv('BTCUSD', 'COINBASE', 'Daily', 100)

# Intraday crypto
df = fetcher.get_ohlcv('BTCUSDT', 'BINANCE', '1 Hour', 168)  # 7 days
```

### Forex

```python
# Major pairs
df = fetcher.get_ohlcv('EURUSD', 'FX_IDC', 'Daily', 100)
df = fetcher.get_ohlcv('GBPUSD', 'FX_IDC', 'Daily', 100)
df = fetcher.get_ohlcv('USDJPY', 'FX_IDC', 'Daily', 100)
```

---

## Performance Optimization

### Use Caching

```python
# First call: fetches from API (~3s)
df1 = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)

# Subsequent calls: uses cache (~0.05s)
df2 = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)
```

### Parallel Fetching

```python
# Fetch 20 stocks in parallel
stocks = [f'STOCK{i}' for i in range(20)]

df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    parallel=True,  # 5-10x faster
)
```

### Increase Workers

```python
from tradeglob import FetcherConfig

# More parallel workers for large batches
config = FetcherConfig(max_workers=10)
fetcher = TradeGlobFetcher(config=config)
```

---

## See Also

- [Technical Analysis](05_TECHNICAL_ANALYSIS.md)
- [Data Export](06_DATA_EXPORT.md)
- [Market Coverage](09_MARKET_COVERAGE.md)
- [API Reference](10_API_REFERENCE.md)

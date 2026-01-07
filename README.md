# TradeGlob

**Universal Market Data Fetcher** - Access 3.5+ million instruments from global exchanges via TradingView.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 🌍 Global Market Coverage

TradeGlob provides seamless access to:

- 📊 **70+ Stock Exchanges** (US, Europe, Asia, Middle East, Africa)
- 💱 **Forex** - All major and exotic pairs
- 🪙 **Crypto** - 70+ exchanges (Binance, Coinbase, Kraken, etc.)
- 🛢️ **Commodities** - Gold, Oil, Natural Gas, etc.
- 📈 **Indices** - S&P 500, NASDAQ, FTSE, etc.
- 🔮 **Futures** - CME, Eurex, etc.

## ✨ Key Features

- ⚡ **Fast Auto-Login** - Browser opens, detects login, closes automatically (~3-5 sec)
- 🔐 **Smart Authentication** - Remembers session, no repeated logins
- ✅ **Parallel Fetching** - 5x faster for multiple symbols
- 💾 **Smart Caching** - Automatic caching with expiration
- 🔄 **Error Handling** - Comprehensive retry mechanism
- ✔️ **Data Validation** - Quality checks on all data
- 📊 **Progress Indicators** - Visual feedback for long operations
- 🎯 **Type Hints** - Full IDE support
- 🚀 **Production Ready** - Battle-tested reliability

## 🚀 Quick Start

### Installation

**From GitHub (recommended):**
```bash
pip install git+https://github.com/ibrasonic/tradeglob.git
```

**From source:**
```bash
git clone https://github.com/ibrasonic/tradeglob.git
cd tradeglob
pip install -r requirements.txt
pip install -e .
```

### Basic Usage

```python
from tradeglob import TradeGlobFetcher
from datetime import date

# Initialize (anonymous mode)
fetcher = TradeGlobFetcher()

# Or with authentication (recommended - free account)
fetcher = TradeGlobFetcher(
    username='your_email@example.com',
    password='your_password'
)

# Get single stock OHLCV data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=100)
print(df.tail())

# Get multiple stocks
stocks = ['AAPL', 'MSFT', 'GOOGL']
df_multi = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)
print(df_multi.head())
```

## � API Reference

Complete reference of all user-facing functions in TradeGlob.

### Core TradeGlobFetcher Methods

| Function | Description | Parameters (in order with datatypes) | Returns |
|----------|-------------|--------------------------------------|---------|
| **`__init__`** | Initialize the fetcher with optional authentication | 1. `username: Optional[str] = None` - TradingView username/email<br>2. `password: Optional[str] = None` - TradingView password<br>3. `auth: bool = False` - Open browser for authentication<br>4. `config: Optional[FetcherConfig] = None` - Custom configuration | `TradeGlobFetcher` instance |
| **`authenticate`** | Authenticate with TradingView via browser (fast auto-login) | 1. `username: str = None` - TradingView username/email<br>2. `password: str = None` - TradingView password<br>3. `force_new: bool = False` - Force new login (clears cache) | `bool` - True if successful |
| **`get_ohlcv`** | Fetch OHLCV data for a single symbol | 1. `symbol: str` - Stock symbol (e.g., 'AAPL', 'COMI')<br>2. `exchange: str` - Exchange code (e.g., 'NASDAQ', 'EGX')<br>3. `interval: str` - Time interval (see intervals below)<br>4. `n_bars: int = 100` - Number of bars to fetch (max 5000)<br>5. `use_cache: bool = True` - Use cached data if available<br>6. `validate: bool = True` - Validate data quality | `pd.DataFrame` with columns: [symbol, open, high, low, close, volume] |
| **`get_multiple`** | Fetch data for multiple symbols with date range | 1. `stock_list: List[str]` - List of stock symbols<br>2. `exchange: str` - Exchange code<br>3. `interval: str` - Time interval<br>4. `start: date` - Start date<br>5. `end: date` - End date<br>6. `columns: Union[str, List[str]] = 'close'` - 'close', 'all', or list of columns<br>7. `parallel: bool = True` - Use parallel fetching (5x faster)<br>8. `use_cache: bool = True` - Use cached data | `pd.DataFrame` with dates as index, symbols as columns |
| **`search_symbol`** | Search for symbols on TradingView | 1. `text: str` - Search query (e.g., 'AAPL', 'apple', 'COMI')<br>2. `exchange: str = ''` - Exchange filter (empty = all exchanges) | `List[dict]` - List of symbol info dictionaries |
| **`export_data`** | Export DataFrame to file (CSV, Excel, Parquet, JSON, HDF5) | 1. `df: pd.DataFrame` - DataFrame to export<br>2. `filepath: str` - Output file path<br>3. `format: str = 'csv'` - Format: 'csv', 'excel', 'parquet', 'json', 'hdf5'<br>4. `**kwargs` - Format-specific arguments | `str` - Absolute path to created file |
| **`export_multi_format`** | Export DataFrame to multiple formats simultaneously | 1. `df: pd.DataFrame` - DataFrame to export<br>2. `base_path: str` - Base path without extension<br>3. `formats: List[str] = ['csv', 'parquet']` - List of formats<br>4. `**kwargs` - Additional export arguments | `Dict[str, str]` - {format: filepath} mapping |
| **`get_cache_info`** | Get cache statistics and information | None | `dict` - Cache stats: enabled, location, files, size_mb, oldest, newest |
| **`clear_cache`** | Clear cached data (all or specific symbol/exchange) | 1. `symbol: Optional[str] = None` - Clear specific symbol (None = all)<br>2. `exchange: Optional[str] = None` - Clear specific exchange (None = all) | `None` |

### Configuration Classes

| Class | Description | Key Parameters |
|-------|-------------|----------------|
| **`FetcherConfig`** | Customize fetcher behavior | `retry_attempts: int = 20` - Number of retry attempts<br>`max_workers: int = 5` - Parallel workers for concurrent fetching<br>`cache_enabled: bool = True` - Enable/disable caching<br>`cache_max_age_hours: int = 24` - Cache expiration hours<br>`safety_buffer: float = 1.3` - Safety multiplier for n_bars calculation<br>`connection_timeout: int = 60` - Connection timeout in seconds<br>`log_level: str = 'ERROR'` - Logging level (DEBUG, INFO, WARNING, ERROR)<br>`progress_bar: bool = True` - Show progress for multiple symbols<br>`validate_data: bool = True` - Enable data quality checks |
| **`MarketConfig`** | Access exchange definitions by region | `get_all_exchanges()` - Get list of all supported exchanges<br>`get_region_exchanges(region: str)` - Get exchanges for region<br>`find_exchange(exchange_code: str)` - Find region for exchange |

### Valid Intervals

| Category | Intervals |
|----------|-----------|
| **Intraday** | `'1 Minute'`, `'3 Minute'`, `'5 Minute'`, `'15 Minute'`, `'30 Minute'`, `'45 Minute'`, `'1 Hour'`, `'2 Hour'`, `'3 Hour'`, `'4 Hour'` |
| **Daily+** | `'Daily'`, `'Weekly'`, `'Monthly'` |

### Exception Classes

| Exception | Description |
|-----------|-------------|
| `TradeGlobError` | Base exception for all TradeGlob errors |
| `ConnectionError` | Connection to TradingView failed |
| `NoDataError` | No data returned for requested symbol |
| `ValidationError` | Input validation failed |
| `AuthenticationError` | TradingView authentication failed |

## �📚 Examples

> **💡 Tip:** To find symbols, visit [TradingView.com](https://www.tradingview.com/) and search manually, or use common patterns like 'AAPL', 'BTCUSD', 'EURUSD'.

### Authentication (Recommended for Better Stability)

**🎯 New: Fast Automatic Browser Login**

TradeGlob now features automatic login detection - just log in once and you're set!

**Option 1: Authenticate during initialization (fastest)**
```python
from tradeglob import TradeGlobFetcher

# Authenticate immediately when creating fetcher
fetcher = TradeGlobFetcher(auth=True)
# → Browser opens to TradingView login
# → Log in manually (or auto-redirects if already logged in)
# → Closes automatically when done
# → Super fast! (~1-2 seconds if logged in today, cached token used)
```

**Option 2: Authenticate later (more flexible)**
```python
# Initialize without authentication
fetcher = TradeGlobFetcher()

# Authenticate when ready
fetcher.authenticate()
# → Same fast browser login process

# Force new login (clears cache)
fetcher.authenticate(force_new=True)

# Check authentication status
if fetcher.authenticated:
    print("✓ Authenticated - Better stability & rate limits")
else:
    print("⚠ Anonymous mode - May hit rate limits")
```

> **💡 Benefits:** Free TradingView account provides better rate limits and stability. No paid subscription required!
> 
> **⚡ Performance:** Token cached for 24 hours - subsequent initializations take ~1-2 seconds with no browser!

### Egyptian Stock Market

```python
from tradeglob import TradeGlobFetcher
from datetime import date

fetcher = TradeGlobFetcher()

# Single stock
df = fetcher.get_ohlcv('COMI', 'EGX', 'Daily', n_bars=252)

# Multiple stocks
stocks = ['COMI', 'EGAL', 'MCQE']
df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='EGX',
    interval='Weekly',
    start=date(2023, 1, 1),
    end=date(2024, 12, 31)
)
```

### Cryptocurrency

```python
# Bitcoin from Binance (use BTCUSDT for perpetual, or search for correct symbol)
df = fetcher.get_ohlcv('BTCUSDT', 'BINANCE', 'Daily', n_bars=365)

# Coinbase (more reliable for USD pairs)
df = fetcher.get_ohlcv('BTCUSD', 'COINBASE', 'Daily', n_bars=365)

# Multiple crypto pairs from Coinbase
cryptos = ['BTCUSD', 'ETHUSD']
df = fetcher.get_multiple(
    stock_list=cryptos,
    exchange='COINBASE',
    interval='4 Hour',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)
```

### Forex

```python
# EUR/USD from OANDA or FX
df = fetcher.get_ohlcv('EURUSD', 'OANDA', 'Daily', n_bars=500)

# Or use FX for generic forex data
df = fetcher.get_ohlcv('EURUSD', 'FX', 'Daily', n_bars=500)

# Multiple pairs
pairs = ['EURUSD', 'GBPUSD', 'USDJPY']
df = fetcher.get_multiple(
    stock_list=pairs,
    exchange='OANDA',
    interval='1 Hour',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)

# Search for forex pairs
results = fetcher.search_symbol('EUR', 'OANDA')
for r in results[:5]:
    print(f"{r['symbol']} - {r['description']}")
import pandas_ta as ta

# Fetch data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=252)

# Add technical indicators
df.ta.rsi(length=14, append=True)
df.ta.macd(append=True)
df.ta.bbands(append=True)
df.ta.sma(length=20, append=True)
df.ta.ema(length=50, append=True)

print(df[['close', 'RSI_14', 'MACD_12_26_9', 'SMA_20']].tail())
```

### Full OHLCV Data

```python
# Get all OHLCV columns for multiple stocks
stocks = ['AAPL', 'MSFT']
df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    columns='all'  # Returns MultiIndex with (symbol, column)
)

# Access specific stock's high prices
print(df[('AAPL', 'high')])

# Or get specific columns only
df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    columns=['open', 'close', 'volume']
)
```

### Data Validation

```python
# Enable data quality validation (default)
df = fetcher.get_ohlcv(
    'AAPL',
    'NASDAQ',
    'Daily',
    n_bars=100,
    validate=True  # Checks for missing data, duplicates, price anomalies
)

# Disable validation for faster fetching
df = fetcher.get_ohlcv(
    'AAPL',
    'NASDAQ',
    'Daily',
    n_bars=100,
    validate=False  # Skip quality checks
)

# Configure validation globally
config = FetcherConfig(validate_data=False)  # Disable for all fetches
fetcher = TradeGlobFetcher(config=config)
```

**Validation checks:**
- Missing dates detection
- Duplicate rows detection  
- Price anomalies (negative prices, volume issues)
- Data completeness

### Parallel vs Sequential Fetching

```python
# Parallel fetching (default) - 5x faster for multiple symbols
df = fetcher.get_multiple(
    stock_list=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    parallel=True  # Default: True
)

# Sequential fetching - more stable for unreliable connections
df = fetcher.get_multiple(
    stock_list=['AAPL', 'MSFT'],
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    parallel=False  # Fetch one by one
)

# Disable cache for fresh data
df = fetcher.get_ohlcv(
    'AAPL',
    'NASDAQ',
    'Daily',
    n_bars=100,
    use_cache=False  # Always fetch fresh data
)
```

**When to use sequential mode:**
- Unreliable internet connection
- Rate limiting issues
- Debugging symbol fetch problems
- Small number of symbols (1-2)

**Parallel mode benefits:**
- 5-10x faster for 5+ symbols
- Better resource utilization
- Progress bar shows overall completion
- Continues on partial failures

## ⚙️ Configuration

```python
from tradeglob import TradeGlobFetcher, FetcherConfig

# Custom configuration
config = FetcherConfig(
    # Retry settings
    retry_attempts=30,           # Number of retry attempts (default: 20)
    retry_delay=1.0,             # Delay between retries in seconds (default: 0.5)
    retry_backoff=1.5,           # Backoff multiplier for exponential retry (default: 1.0)
    
    # Parallel processing
    max_workers=10,              # Max parallel workers (default: 5)
    
    # Cache settings
    cache_enabled=True,          # Enable caching (default: True)
    cache_max_age_hours=48,      # Cache expiration in hours (default: 24)
    
    # Data fetching optimization
    safety_buffer=1.5,           # Multiplier for n_bars (1.5 = 50% buffer, default: 1.3)
    min_bars_daily=100,          # Min bars for daily data (default: 100)
    min_bars_weekly=20,          # Min bars for weekly data (default: 20)
    min_bars_monthly=6,          # Min bars for monthly data (default: 6)
    min_bars_intraday=500,       # Min bars for intraday data (default: 500)
    
    # Connection settings
    connection_timeout=60,       # Timeout in seconds (default: 60)
    
    # Logging & Validation
    log_level='DEBUG',           # Logging level: DEBUG, INFO, WARNING, ERROR (default: ERROR)
    validate_data=True,          # Enable data quality validation (default: True)
    progress_bar=True            # Show progress bars (default: True)
)

fetcher = TradeGlobFetcher(
    username='your_email@example.com',
    password='your_password',
    config=config
)
```

### MarketConfig - Exchange Discovery

```python
from tradeglob import MarketConfig

market = MarketConfig()

# Get all supported exchanges
all_exchanges = market.get_all_exchanges()
print(f"Total exchanges: {len(all_exchanges)}")

# Get exchanges by region
us_exchanges = market.get_region_exchanges('US')
print(f"US exchanges: {us_exchanges}")  # ['NASDAQ', 'NYSE', 'AMEX', 'OTC']

asia_exchanges = market.get_region_exchanges('ASIA')
print(f"Asia exchanges: {asia_exchanges}")  # ['TSE', 'HKEX', 'SSE', ...]

crypto_exchanges = market.get_region_exchanges('CRYPTO')
print(f"Crypto exchanges: {crypto_exchanges}")  # ['BINANCE', 'COINBASE', ...]

# Find which region an exchange belongs to
region = market.find_exchange('NASDAQ')
print(f"NASDAQ is in: {region}")  # US

region = market.find_exchange('EGX')
print(f"EGX is in: {region}")  # AFRICA (EGX is also in EGYPT)

# Access regional exchange lists directly
print(f"Middle East: {market.MIDDLE_EAST}")  # ['TADAWUL', 'DFM', 'ADX', ...]
print(f"Europe: {market.EUROPE}")  # ['LSE', 'EURONEXT', 'XETRA', ...]
```

## 🎯 Supported Intervals

- **Intraday**: `1 Minute`, `3 Minute`, `5 Minute`, `15 Minute`, `30 Minute`, `45 Minute`
- **Hourly**: `1 Hour`, `2 Hour`, `3 Hour`, `4 Hour`
- **Daily/Weekly/Monthly**: `Daily`, `Weekly`, `Monthly`

## 🌐 Major Exchanges

### Middle East & Africa
- **EGX** - Egyptian Exchange
- **TADAWUL** - Saudi Stock Exchange
- **DFM** - Dubai Financial Market
- **JSE** - Johannesburg Stock Exchange

### United States
- **NASDAQ**, **NYSE**, **AMEX**

### Europe
- **LSE** (London), **EURONEXT**, **XETRA** (Germany)

### Asia
- **TSE** (Tokyo), **HKEX** (Hong Kong), **NSE/BSE** (India)

### Crypto & Forex
- **BINANCE**, **COINBASE**, **KRAKEN**
- **FX_IDC**, **OANDA**, **FXCM**

## 🔍 Symbol Search

TradeGlob includes a built-in symbol search function - **no authentication required!**

### Using search_symbol()

```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()  # No auth needed for search

# Search all exchanges
results = fetcher.search_symbol('COMI')
for r in results[:3]:
    print(f"{r['symbol']} ({r['exchange']}) - {r['description']}")
# Output: COMI (EGX) - Commercial International Bank Egypt

# Search specific exchange
results = fetcher.search_symbol('COMI', 'EGX')
if results:
    symbol_info = results[0]
    print(f"Symbol: {symbol_info['symbol']}")
    print(f"Exchange: {symbol_info['exchange']}")
    print(f"Description: {symbol_info['description']}")
    print(f"Type: {symbol_info['type']}")

# Search with partial name
results = fetcher.search_symbol('apple', 'NASDAQ')
# Returns: AAPL and related symbols

# Crypto search
results = fetcher.search_symbol('BTC', 'BINANCE')

# Forex search
results = fetcher.search_symbol('EUR', 'OANDA')
```

### Manual Verification (Alternative)
1. Visit [TradingView](https://www.tradingview.com/)
2. Search for your stock/crypto/forex pair
3. Check the chart URL or symbol details

**Common patterns:**
- **Stocks:** `AAPL` (NASDAQ), `TSLA` (NASDAQ), `COMI` (EGX), `2222` (TADAWUL - Aramco)
- **Crypto:** `BTCUSD` (COINBASE), `BTCUSDT` (BINANCE), `ETHUSD` (COINBASE)
- **Forex:** `EURUSD` (OANDA), `GBPUSD` (OANDA), `USDJPY` (FX)

### Try Fetching D

```python
# Get cache info
info = fetcher.get_cache_info()
print(info)
# {
#     'enabled': True,
#     'files': 15,
#     'size_mb': 2.3,
#     'cache_dir': '/path/to/cache',
#     'max_age_hours': 24
# }

# Clear specific symbol from all exchanges
fetcher.clear_cache(symbol='AAPL')

# Clear all symbols from specific exchange
fetcher.clear_cache(exchange='NASDAQ')

# Clear specific symbol on specific exchange
fetcher.clear_cache(symbol='AAPL', exchange='NASDAQ')

# Clear all cache
fetcher.clear_cache()
print("✓ Cache cleared")

# Disable caching temporarily
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100, use_cache=False)

# Disable caching globally via config
config = FetcherConfig(cache_enabled=False)
fetcher = TradeGlobFetcher(config=config)
```

## 💾 Exporting Data

TradeGlob supports exporting data to multiple formats for analysis and storage.

### Export to Single Format

```python
from tradeglob import TradeGlobFetcher
from datetime import date

fetcher = TradeGlobFetcher()

# Fetch data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=252)

# Export to CSV
fetcher.export_data(df, 'aapl_data.csv', format='csv')

# Export to Excel
fetcher.export_data(df, 'aapl_data.xlsx', format='excel')

# Export to Parquet (efficient for large datasets)
fetcher.export_data(df, 'aapl_data.parquet', format='parquet')

# Export to JSON
fetcher.export_data(df, 'aapl_data.json', format='json')

# Export to HDF5 (great for time series)
fetcher.export_data(df, 'aapl_data.h5', format='hdf5')
```

### Export to Multiple Formats at Once

```python
# Fetch multiple stocks
stocks = ['AAPL', 'MSFT', 'GOOGL']
df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)

# Export to multiple formats simultaneously
fetcher.export_multi_format(
    df,
    base_filename='nasdaq_stocks',
    formats=['csv', 'excel', 'parquet']
)
# Creates: nasdaq_stocks.csv, nasdaq_stocks.xlsx, nasdaq_stocks.parquet
```

### Supported Export Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| CSV | `.csv` | Universal compatibility, text editors |
| Excel | `.xlsx` | Business analysis, spreadsheet tools |
| Parquet | `.parquet` | Large datasets, fast I/O, compression |
| JSON | `.json` | Web APIs, JavaScript integration |
| HDF5 | `.h5` | Time series, scientific computing |

## 🚀 Performance Tips & Best Practices

### Optimize Fetching Speed

```python
# ✅ DO: Fetch multiple symbols in parallel (5-10x faster)
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
df = fetcher.get_multiple(stocks, 'NASDAQ', 'Daily',
                         start=date(2024,1,1), end=date(2024,12,31),
                         parallel=True)  # ~10 seconds

# ❌ DON'T: Fetch one by one in a loop
for stock in stocks:
    df = fetcher.get_ohlcv(stock, 'NASDAQ', 'Daily', 252)  # ~50 seconds
```

### Leverage Caching

```python
# First fetch (from TradingView)
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 252)  # ~3 seconds

# Subsequent fetches (from cache, within 24 hours)
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 252)  # ~0.05 seconds (60x faster!)

# Adjust cache expiration for your needs
config = FetcherConfig(
    cache_enabled=True,
    cache_max_age_hours=48  # Keep cache for 2 days
)
```

### Handle Failures Gracefully

```python
from tradeglob import NoDataError, ConnectionError, ValidationError

# Parallel mode continues on partial failures
stocks = ['AAPL', 'INVALID_SYMBOL', 'MSFT', 'BAD_TICKER', 'GOOGL']
df = fetcher.get_multiple(stocks, 'NASDAQ', 'Daily',
                         start=date(2024,1,1), end=date(2024,12,31))
# Returns data for: AAPL, MSFT, GOOGL (skips invalid symbols)
print(f"Successfully fetched: {len(df.columns)} symbols")

# Handle specific errors
try:
    df = fetcher.get_ohlcv('SYMBOL', 'EXCHANGE', 'Daily', 100)
except NoDataError:
    print("Symbol not found or no data available")
except ConnectionError:
    print("Network issue - check internet connection")
except ValidationError:
    print("Invalid parameters - check symbol/exchange/interval")
```

### Optimize Configuration

```python
# For bulk downloads (many symbols)
config = FetcherConfig(
    max_workers=20,           # More parallel threads
    retry_attempts=10,        # Fewer retries
    cache_enabled=True,       # Cache results
    progress_bar=True         # Track progress
)

# For real-time/fresh data needs
config = FetcherConfig(
    cache_max_age_hours=1,    # Short cache expiration
    retry_attempts=30,        # More retries for reliability
    retry_delay=0.5           # Faster retry
)

# For unreliable connections
config = FetcherConfig(
    retry_attempts=50,        # Many retries
    retry_delay=2.0,          # Longer delays
    retry_backoff=2.0         # Exponential backoff
)
```

## ⚠️ Important Notes

### Data Availability
- **Free account**: 15-20 min delayed data, limited intraday history
- **Paid plans**: Real-time data, extended history (see TradingView pricing)

### Symbol Format
Different exchanges use different formats:
- **US stocks**: `AAPL` (simple ticker)
- **Japanese stocks**: `7203` (numerical codes)
- **Crypto**: `BTCUSD` (pair format)

Use `search_symbol()` to find the correct format.

### Trading Hours
Intraday data only available during market hours:
- **EGX**: Sunday-Thursday, 10:00-14:30 EET
- **US markets**: Monday-Friday, 9:30-16:00 EST
- **Crypto**: 24/7

## 🐛 Error Handling

```python
from tradeglob import TradeGlobFetcher
from tradeglob import NoDataError, ConnectionError, ValidationError

fetcher = TradeGlobFetcher()

try:
    df = fetcher.get_ohlcv('INVALID', 'NASDAQ', 'Daily', 100)
except NoDataError as e:
    print(f"No data available: {e}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except ValidationError as e:
    print(f"Invalid input: {e}")
```

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check TradingView documentation for exchange/symbol codes

## 🙏 Acknowledgments

Built on top of the excellent [tvDatafeed](https://github.com/StreamAlpha/tvdatafeed) library.

---

**TradeGlob** - *Flow of global market data* 🌊🌍

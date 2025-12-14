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

- ✅ **Authentication Support** - Free TradingView account = better stability
- ✅ **Parallel Fetching** - 5x faster for multiple symbols
- ✅ **Smart Caching** - Automatic caching with expiration
- ✅ **Error Handling** - Comprehensive retry mechanism
- ✅ **Data Validation** - Quality checks on all data
- ✅ **Progress Indicators** - Visual feedback for long operations
- ✅ **Type Hints** - Full IDE support
- ✅ **Production Ready** - Battle-tested reliability

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

**Important:** TradeGlob requires `numpy<2.3` for compatibility with `numba`. If you have `numpy>=2.3` installed:
```bash
pip install "numpy>=1.24,<2.3" --force-reinstall
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

## 📚 Examples

> **💡 Tip:** To find symbols, visit [TradingView.com](https://www.tradingview.com/) and search manually, or use common patterns like 'AAPL', 'BTCUSD', 'EURUSD'.

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

## ⚙️ Configuration

```python
from tradeglob import TradeGlobFetcher, FetcherConfig

# Custom configuration
config = FetcherConfig(
    retry_attempts=30,           # Increase retries
    retry_delay=1.0,             # Longer delay between retries
    max_workers=10,              # More parallel workers
    cache_enabled=True,          # Enable caching
    cache_max_age_hours=48,      # Cache expires after 48 hours
    safety_buffer=1.5,           # 50% extra bars
    log_level='DEBUG',           # Detailed logging
    progress_bar=True            # Show progress bars
)

fetcher = TradeGlobFetcher(
    username='your_email@example.com',
    password='your_password',
    config=config
)
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

## 🔍 Finding Correct Symbols

**Note:** `search_symbol()` requires TradingView authentication. If you're using without credentials, here's how to find symbols:

### Method 1: Use search_symbol() (requires authentication)
```python
fetcher = TradeGlobFetcher(username='your_email', password='your_password')
results = fetcher.search_symbol('apple', 'NASDAQ')
if results:
    print(results[0])
    # {'symbol': 'AAPL', 'exchange': 'NASDAQ', 'description': 'Apple Inc', ...}
```
### Manual Verification
1. Visit [TradingView](https://www.tradingview.com/)
2. Search for your stock/crypto/forex pair
3. Check the chart URL or symbol details

**Common patterns:**
- **Stocks:** `AAPL` (NASDAQ), `TSLA` (NASDAQ), `2222` (TADAWUL - Aramco)
- **Crypto:** `BTCUSD` (COINBASE), `BTCUSDT` (BINANCE), `ETHUSD` (COINBASE)
- **Forex:** `EURUSD` (OANDA), `GBPUSD` (OANDA), `USDJPY` (FX)

### Try Fetching D

```python
# Get cache info
info = fetcher.get_cache_info()
print(info)
# {'enabled': True, 'files': 15, 'size_mb': 2.3, ...}

# Clear specific symbol
fetcher.clear_cache(symbol='AAPL')

# Clear specific exchange
fetcher.clear_cache(exchange='NASDAQ')

# Clear all cache
fetcher.clear_cache()
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

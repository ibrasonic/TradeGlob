# Frequently Asked Questions (FAQ)

## General Questions

### What is TradeGlob?

TradeGlob is a Python library for fetching market data from 3.5+ million financial instruments across 70+ global exchanges via TradingView. It includes 130+ technical indicators and supports stocks, crypto, forex, commodities, and indices.

### Is it free to use?

Yes! TradeGlob is open-source under the MIT license. However, you may want a free TradingView account for better stability and rate limits.

### Do I need a paid TradingView subscription?

No. A **free TradingView account** is recommended for better stability, but you can also use anonymous mode with limitations.

---

## Installation & Setup

### How do I install TradeGlob?

```bash
pip install git+https://github.com/ibrasonic/TradeGlob.git
```

### What are the dependencies?

- Python 3.7+
- pandas
- selenium
- numba (for technical indicators)
- scipy (for technical indicators)
- Other dependencies installed automatically

### Installation fails with "No matching distribution"

Make sure you're using Python 3.7 or higher:
```bash
python --version
```

---

## Authentication

### Do I need to authenticate?

No, but it's **recommended**. Anonymous mode may hit rate limits or get slower data.

### How do I authenticate?

**Option 1:** During initialization
```python
fetcher = TradeGlobFetcher(auth=True)
```

**Option 2:** After initialization
```python
fetcher = TradeGlobFetcher()
fetcher.authenticate()
```

### How does authentication work?

TradeGlob opens a Chrome browser where you manually log in to TradingView. The session token is cached for 24 hours, so you don't need to log in repeatedly.

### Browser doesn't open during authentication

Make sure Chrome is installed. TradeGlob uses Selenium with Chrome.

---

## Data Fetching

### What markets are supported?

- **70+ Stock Exchanges** (US, Europe, Asia, Middle East, Africa)
- **Crypto** (Binance, Coinbase, Kraken, 70+ exchanges)
- **Forex** (all major and exotic pairs)
- **Commodities** (Gold, Oil, Natural Gas, etc.)
- **Indices** (S&P 500, NASDAQ, etc.)

See [Market Coverage](09_MARKET_COVERAGE.md) for full list.

### How do I find the correct symbol name?

Use the `search_symbol()` function:
```python
results = fetcher.search_symbol('apple', 'NASDAQ')
print(results[0]['symbol'])  # 'AAPL'
```

Or visit [TradingView.com](https://www.tradingview.com/) and search manually.

### What's the maximum number of bars I can fetch?

TradingView limits to **5000 bars** per request. TradeGlob automatically caps requests at this limit.

### Can I get real-time data?

Free accounts get **15-20 minute delayed data**. Real-time data requires a TradingView paid subscription.

### How do I get intraday data?

Use intraday intervals:
```python
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', '1 Hour', n_bars=100)
```

**Note:** Intraday history is limited for free accounts.

---

## Technical Analysis

### How many indicators are available?

130+ indicators across 8 categories:
- Momentum (RSI, MACD, Stochastic, etc.)
- Trend (ADX, Aroon, PSAR, etc.)
- Volatility (ATR, Bollinger Bands, etc.)
- Volume (OBV, VWAP, MFI, etc.)
- Overlap (SMA, EMA, WMA, etc.)
- Statistics
- Performance
- Candlestick patterns

### How do I calculate indicators?

```python
df = fetcher.ta(
    symbol='AAPL',
    exchange='NASDAQ',
    interval='Daily',
    n_bars=100,
    indicators='common'
)
```

See [Technical Analysis Guide](05_TECHNICAL_ANALYSIS.md).

### Why are my indicator values NaN?

**Cause:** Not enough historical data for the indicator's lookback period.

**Solution:** Increase `n_bars`:
```python
# BAD: Only 50 bars for 200-period SMA
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=50)

# GOOD: Enough data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=300)
```

### Can I customize indicator parameters?

Yes, using the DataFrame `.ta` accessor:
```python
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 200)

# Custom RSI period
df.ta.rsi(length=21, append=True)

# Custom SMA periods
df.ta.sma(length=10, append=True)
df.ta.sma(length=30, append=True)
```

---

## Caching

### How does caching work?

TradeGlob automatically caches fetched data for 24 hours (configurable). Subsequent requests for the same data use the cache, making it **60x faster**.

### Where is cache stored?

In `.cache/` directory in your current working directory.

### How do I disable caching?

**Temporarily:**
```python
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100, use_cache=False)
```

**Globally:**
```python
from tradeglob import FetcherConfig

config = FetcherConfig(cache_enabled=False)
fetcher = TradeGlobFetcher(config=config)
```

### How do I clear the cache?

```python
# Clear all cache
fetcher.clear_cache()

# Clear specific symbol
fetcher.clear_cache(symbol='AAPL')

# Clear specific exchange
fetcher.clear_cache(exchange='NASDAQ')
```

---

## Performance

### Fetching multiple stocks is slow

Use **parallel fetching** (enabled by default):
```python
df = fetcher.get_multiple(
    stock_list=['AAPL', 'MSFT', 'GOOGL'],
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    parallel=True  # 5x faster
)
```

### How can I speed up fetching?

1. **Use caching** (enabled by default)
2. **Use parallel fetching** for multiple symbols
3. **Increase max_workers**:
```python
config = FetcherConfig(max_workers=10)
fetcher = TradeGlobFetcher(config=config)
```

### Calculate only needed indicators

```python
# SLOW: All 130+ indicators
df = fetcher.ta(df=df, indicators='all')

# FAST: Only what you need
df = fetcher.ta(df=df, indicators=['RSI', 'MACD', 'SMA'])
```

---

## Export

### What export formats are supported?

- CSV (`.csv`)
- Excel (`.xlsx`)
- Parquet (`.parquet`) - most efficient
- JSON (`.json`)
- HDF5 (`.h5`)

### How do I export to Excel?

```python
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)
fetcher.export_data(df, 'aapl.xlsx', format='excel')
```

### Can I export to multiple formats at once?

Yes:
```python
paths = fetcher.export_multi_format(
    df,
    'aapl_data',
    formats=['csv', 'excel', 'parquet']
)
```

---

## Errors

### "No data returned for symbol"

**Causes:**
1. Symbol doesn't exist on that exchange
2. Wrong exchange code
3. Symbol format incorrect

**Solutions:**
1. Use `search_symbol()` to find correct symbol/exchange
2. Check TradingView.com for correct symbol format
3. Verify exchange code

### "Connection failed" or "Network error"

**Causes:**
1. No internet connection
2. TradingView is down
3. Firewall blocking connection
4. Rate limiting

**Solutions:**
1. Check internet connection
2. Try again later
3. Authenticate with TradingView account
4. Reduce parallel workers

### "DataFrame object has no attribute 'ta'"

**Cause:** TA module not properly imported

**Solution:**
```python
# Make sure to import from tradeglob
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()
```

### "Selenium WebDriver error"

**Cause:** Chrome or ChromeDriver not installed/updated

**Solution:**
```bash
# chromedriver-autoinstaller should handle this
# If not, manually install Chrome browser
```

---

## Data Quality

### How do I check data quality?

Enable validation (on by default):
```python
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100, validate=True)
```

This checks for:
- Missing values
- Price anomalies
- Duplicate timestamps
- Invalid OHLC relationships (high < low, etc.)

### Missing dates in my data

Stock markets don't trade on weekends and holidays. This is normal.

### Volume is zero for some days

This can happen for:
- Holidays
- Trading halts
- Low-liquidity stocks

---

## Best Practices

### Recommended workflow?

```python
from tradeglob import TradeGlobFetcher
from datetime import date

# 1. Initialize with auth
fetcher = TradeGlobFetcher(auth=True)

# 2. Fetch data
df = fetcher.get_multiple(
    stock_list=['AAPL', 'MSFT'],
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)

# 3. Calculate indicators (if needed)
df_with_ta = fetcher.ta(df=df, indicators='common', append=True)

# 4. Export
fetcher.export_data(df_with_ta, 'data.xlsx', format='excel')
```

### Should I use anonymous or authenticated mode?

**Use authenticated mode** for:
- Production applications
- Frequent requests
- Better stability
- Avoiding rate limits

**Use anonymous mode** for:
- Quick tests
- One-time data pulls
- When you don't have a TradingView account

---

## Still Need Help?

- Check [Error Handling Guide](12_ERROR_HANDLING.md)
- Review [Examples](../examples/)
- Open an issue on [GitHub](https://github.com/ibrasonic/TradeGlob/issues)

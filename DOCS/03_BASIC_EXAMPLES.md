# Basic Examples

Practical examples to get you started with TradeGlob.

## Example 1: Single Stock Data

Fetch historical data for one stock.

```python
from tradeglob import TradeGlobFetcher

# Initialize
fetcher = TradeGlobFetcher()

# Fetch Apple stock - 1 year of daily data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=252)

# Display results
print(f"Fetched {len(df)} days of data")
print("\nLast 5 days:")
print(df[['close', 'volume']].tail())

# Quick stats
print(f"\nPrice Range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
print(f"Average Volume: {df['volume'].mean():,.0f}")
```

**Output:**
```
Fetched 252 days of data

Last 5 days:
            close     volume
Date                        
2024-12-13  198.2   45234567
2024-12-14  199.5   48341234
2024-12-15  200.1   52134890
2024-12-16  201.3   49234123
2024-12-17  202.5   51234567

Price Range: $150.20 - $202.50
Average Volume: 47,234,567
```

---

## Example 2: Multiple Stocks Comparison

Compare multiple stocks over a date range.

```python
from tradeglob import TradeGlobFetcher
from datetime import date

fetcher = TradeGlobFetcher()

# Tech giants comparison
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

# Fetch close prices for 2024
df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    columns='close'  # Only close prices
)

# Calculate returns
returns = (df.iloc[-1] / df.iloc[0] - 1) * 100

# Display results
print("2024 Performance:")
print("-" * 40)
for stock in stocks:
    print(f"{stock:6} {returns[stock]:+6.2f}%")

# Export to Excel
fetcher.export_data(df, 'tech_stocks_2024.xlsx', format='excel')
print("\n✓ Data exported to tech_stocks_2024.xlsx")
```

**Output:**
```
2024 Performance:
----------------------------------------
AAPL   +35.20%
MSFT   +42.15%
GOOGL  +28.50%
AMZN   +51.20%
META   +63.40%

✓ Data exported to tech_stocks_2024.xlsx
```

---

## Example 3: EGX Market Data

Fetch Egyptian Exchange (EGX) stocks.

```python
from tradeglob import TradeGlobFetcher
from datetime import date

fetcher = TradeGlobFetcher()

# Top EGX stocks
egx_stocks = ['COMI', 'EGAL', 'ABUK', 'EKHO', 'SWDY']

# Fetch 6 months of data
df = fetcher.get_multiple(
    stock_list=egx_stocks,
    exchange='EGX',
    interval='Daily',
    start=date(2024, 6, 1),
    end=date(2024, 12, 31)
)

# Display statistics
print("EGX Stocks Summary:")
print("-" * 60)
print(df.describe().round(2))

# Export
fetcher.export_data(df, 'egx_stocks.csv')
```

---

## Example 4: Cryptocurrency Data

Fetch crypto data from multiple exchanges.

```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()

# Bitcoin on different exchanges
btc_binance = fetcher.get_ohlcv('BTCUSDT', 'BINANCE', 'Daily', n_bars=30)
btc_coinbase = fetcher.get_ohlcv('BTCUSD', 'COINBASE', 'Daily', n_bars=30)

print("BTC Price Comparison (Last 30 days)")
print("=" * 50)
print(f"Binance:  ${btc_binance['close'].iloc[-1]:,.2f}")
print(f"Coinbase: ${btc_coinbase['close'].iloc[-1]:,.2f}")
print(f"Spread:   ${abs(btc_binance['close'].iloc[-1] - btc_coinbase['close'].iloc[-1]):,.2f}")
```

---

## Example 5: Intraday Data

Fetch intraday (hourly) data.

```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()

# Last 100 hours of S&P 500
df = fetcher.get_ohlcv('SPX', 'SP', '1 Hour', n_bars=100)

# Find largest hourly move
df['hourly_change'] = df['close'].pct_change() * 100
largest_move = df.loc[df['hourly_change'].abs().idxmax()]

print("S&P 500 Hourly Data Summary")
print("=" * 50)
print(f"Current Price: ${df['close'].iloc[-1]:,.2f}")
print(f"\nLargest Hourly Move:")
print(f"Date/Time: {largest_move.name}")
print(f"Change: {largest_move['hourly_change']:+.2f}%")
print(f"Volume: {largest_move['volume']:,.0f}")
```

---

## Example 6: Export to Multiple Formats

Save data in different formats.

```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()

# Fetch data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=252)

# Export to multiple formats
paths = fetcher.export_multi_format(
    df,
    base_path='aapl_2024',
    formats=['csv', 'excel', 'parquet', 'json']
)

print("Exported files:")
for format_name, filepath in paths.items():
    print(f"  {format_name:10} → {filepath}")
```

**Output:**
```
Exported files:
  csv        → D:\data\aapl_2024.csv
  excel      → D:\data\aapl_2024.xlsx
  parquet    → D:\data\aapl_2024.parquet
  json       → D:\data\aapl_2024.json
```

---

## Example 7: Search for Symbols

Find correct symbol names.

```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()

# Search for Apple
results = fetcher.search_symbol('apple')

print("Search results for 'apple':")
print("-" * 70)
for i, result in enumerate(results[:5], 1):
    print(f"{i}. {result['symbol']:8} | {result['exchange']:10} | {result['description']}")
```

**Output:**
```
Search results for 'apple':
----------------------------------------------------------------------
1. AAPL     | NASDAQ     | Apple Inc.
2. AAPL     | BATS       | Apple Inc.
3. APC      | XETRA      | Apple Inc.
4. AAPL     | OTC        | Apple Inc.
5. AAPL34   | BMFBOVESPA | Apple Inc. BDR
```

---

## Example 8: Working with All OHLCV Columns

Get complete OHLCV data for analysis.

```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()

# Fetch with all columns
stocks = ['AAPL', 'MSFT']
df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 12, 1),
    end=date(2024, 12, 31),
    columns='all'  # Get OHLCV for each stock
)

# The result is a multi-level DataFrame
print(df.head())

# Access specific stock and column
aapl_close = df[('AAPL', 'close')]
aapl_volume = df[('AAPL', 'volume')]

print(f"\nAAPL Average Volume: {aapl_volume.mean():,.0f}")
```

---

## Example 9: Cache Management

Work with caching efficiently.

```python
from tradeglob import TradeGlobFetcher
import time

fetcher = TradeGlobFetcher()

# First fetch (from API)
start = time.time()
df1 = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)
time1 = time.time() - start

# Second fetch (from cache)
start = time.time()
df2 = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)
time2 = time.time() - start

print(f"First fetch (API):   {time1:.2f}s")
print(f"Second fetch (cache): {time2:.2f}s")
print(f"Speedup: {time1/time2:.0f}x faster!")

# View cache info
info = fetcher.get_cache_info()
print(f"\nCache files: {info['files']}")
print(f"Cache size: {info['size_mb']:.2f} MB")

# Clear cache for specific symbol
fetcher.clear_cache(symbol='AAPL')
print("\n✓ Cache cleared for AAPL")
```

---

## Example 10: Error Handling

Handle errors gracefully.

```python
from tradeglob import TradeGlobFetcher
from tradeglob import NoDataError, ConnectionError, ValidationError

fetcher = TradeGlobFetcher()

stocks = ['AAPL', 'INVALID_SYMBOL', 'MSFT']

for stock in stocks:
    try:
        df = fetcher.get_ohlcv(stock, 'NASDAQ', 'Daily', 100)
        print(f"✓ {stock:15} {len(df)} bars fetched")
        
    except NoDataError:
        print(f"✗ {stock:15} Symbol not found")
        
    except ConnectionError:
        print(f"✗ {stock:15} Connection failed")
        
    except ValidationError as e:
        print(f"✗ {stock:15} Validation error: {e}")
        
    except Exception as e:
        print(f"✗ {stock:15} Unexpected error: {e}")
```

**Output:**
```
✓ AAPL            100 bars fetched
✗ INVALID_SYMBOL  Symbol not found
✓ MSFT            100 bars fetched
```

---

## Next Steps

- Learn about [Technical Analysis](05_TECHNICAL_ANALYSIS.md)
- Explore [Data Export Options](06_DATA_EXPORT.md)
- Review [API Reference](10_API_REFERENCE.md)
- Check out [examples/](../examples/) folder for more

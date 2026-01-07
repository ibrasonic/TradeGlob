# Quick Start Guide

Get started with TradeGlob in under 5 minutes!

## Installation

```bash
pip install git+https://github.com/ibrasonic/TradeGlob.git
```

## Your First Data Fetch

### 1. Import TradeGlob

```python
from tradeglob import TradeGlobFetcher
from datetime import date
```

### 2. Create a Fetcher Instance

```python
# Anonymous mode (limited functionality)
fetcher = TradeGlobFetcher()

# OR with authentication (recommended - FREE account)
fetcher = TradeGlobFetcher(
    username='your_email@example.com',
    password='your_password'
)
```

### 3. Fetch Stock Data

```python
# Get 100 days of Apple stock data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=100)
print(df.tail())
```

**Output:**
```
            symbol   open   high    low  close     volume
Date                                                      
2024-12-16   AAPL  150.2  152.3  149.8  151.5   50234567
2024-12-17   AAPL  151.5  153.1  151.0  152.8   52341234
...
```

### 4. Get Multiple Stocks

```python
stocks = ['AAPL', 'MSFT', 'GOOGL']
df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)
print(df.head())
```

**Output:**
```
            AAPL   MSFT   GOOGL
Date                           
2024-01-01  150.2  320.5   95.3
2024-01-02  151.5  322.8   96.1
...
```

### 5. Calculate Technical Indicators

```python
# Fetch data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=100)

# Calculate common indicators (RSI, MACD, SMA, EMA, etc.)
df_with_ta = fetcher.ta(df=df, indicators='common', append=True)

# Check the new columns
print(df_with_ta.columns)
# ['symbol', 'open', 'high', 'low', 'close', 'volume', 
#  'RSI_14', 'MACD_12_26_9', 'SMA_20', 'SMA_50', 'EMA_12', ...]

# View latest values
print(df_with_ta[['close', 'RSI_14', 'MACD_12_26_9', 'SMA_20']].tail())
```

### 6. Export to Excel

```python
# Export to Excel
fetcher.export_data(df_with_ta, 'aapl_data.xlsx', format='excel')
print("✓ Data exported to aapl_data.xlsx")
```

## Complete Example

```python
from tradeglob import TradeGlobFetcher
from datetime import date

# Initialize
fetcher = TradeGlobFetcher(auth=True)

# Fetch multiple stocks
stocks = ['AAPL', 'MSFT', 'GOOGL']
df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)

# Export to Excel
fetcher.export_data(df, 'nasdaq_stocks.xlsx', format='excel')

print(f"✓ Fetched {len(df)} days of data for {len(stocks)} stocks")
print(f"✓ Exported to nasdaq_stocks.xlsx")
```

## What's Next?

- **Basic Examples** → [03_BASIC_EXAMPLES.md](03_BASIC_EXAMPLES.md)
- **Technical Analysis** → [05_TECHNICAL_ANALYSIS.md](05_TECHNICAL_ANALYSIS.md)
- **More Export Options** → [06_DATA_EXPORT.md](06_DATA_EXPORT.md)
- **Global Markets** → [09_MARKET_COVERAGE.md](09_MARKET_COVERAGE.md)

## Common Intervals

- **Intraday:** `'1 Minute'`, `'5 Minute'`, `'15 Minute'`, `'1 Hour'`, `'4 Hour'`
- **Daily+:** `'Daily'`, `'Weekly'`, `'Monthly'`

## Need Help?

Check the [FAQ](11_FAQ.md) or [Error Handling](12_ERROR_HANDLING.md) guides.

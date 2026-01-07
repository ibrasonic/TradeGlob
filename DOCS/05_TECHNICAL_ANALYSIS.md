# Technical Analysis Guide

TradeGlob includes 130+ technical indicators powered by an integrated TA engine.

## Quick Start

### Calculate Common Indicators

```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()

# Auto-fetch with TA
df = fetcher.ta(
    symbol='AAPL',
    exchange='NASDAQ',
    interval='Daily',
    n_bars=100,
    indicators='common',  # 20 most popular indicators
    append=True
)

print(df[['close', 'RSI_14', 'MACD_12_26_9', 'SMA_20', 'SMA_50']].tail())
```

### Use Existing Data

```python
# Fetch data first
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=200)

# Then calculate indicators
df_with_ta = fetcher.ta(df=df, indicators='common', append=True)
```

## Indicator Sets

### Common Indicators (Default)

```python
df = fetcher.ta(df=df, indicators='common')
```

**Includes (~20 indicators):**
- **Momentum:** RSI (14), MACD, Stochastic, CCI, Williams %R
- **Trend:** ADX, Aroon, PSAR
- **Volatility:** ATR, Bollinger Bands (upper, middle, lower)
- **Volume:** OBV, VWAP
- **Moving Averages:** SMA (20, 50, 200), EMA (12, 26, 50)

### All Indicators

```python
df = fetcher.ta(df=df, indicators='all')  # ALL 130+ indicators
```

⚠️ **Warning:** This may be slow and create 130+ new columns!

### By Category

```python
# Momentum indicators only
df = fetcher.ta(df=df, indicators='momentum')

# Trend indicators only
df = fetcher.ta(df=df, indicators='trend')

# Volatility indicators only
df = fetcher.ta(df=df, indicators='volatility')

# Volume indicators only
df = fetcher.ta(df=df, indicators='volume')

# Overlap/Moving averages only
df = fetcher.ta(df=df, indicators='overlap')
```

**Available categories:**
- `'momentum'` - RSI, MACD, Stochastic, CCI, ROC, etc.
- `'trend'` - ADX, Aroon, PSAR, DPO, Vortex, etc.
- `'volatility'` - ATR, Bollinger Bands, Keltner Channels, Donchian, etc.
- `'volume'` - OBV, VWAP, MFI, Chaikin Money Flow, etc.
- `'overlap'` - SMA, EMA, WMA, HMA, VWMA, etc.
- `'statistics'` - Standard Deviation, Variance, Skew, Kurtosis, etc.
- `'performance'` - Returns, Drawdown, etc.
- `'candle'` - Candlestick patterns

### Specific Indicators

```python
# Select specific indicators
df = fetcher.ta(df=df, indicators=['RSI', 'MACD', 'SMA', 'EMA', 'BBands'])

# With custom parameters (using underscore notation)
df = fetcher.ta(df=df, indicators=['RSI_14', 'SMA_20', 'SMA_50', 'EMA_12'])
```

## Return Options

### Append to Existing DataFrame

```python
# Adds indicators as new columns to existing OHLCV data
df_with_ta = fetcher.ta(df=df, indicators='common', append=True)

# Result: ['symbol', 'open', 'high', 'low', 'close', 'volume', 
#          'RSI_14', 'MACD_12_26_9', 'SMA_20', ...]
```

### Return Indicators Only

```python
# Returns only indicator columns (no OHLCV)
indicators_only = fetcher.ta(df=df, indicators='common', append=False)

# Result: ['RSI_14', 'MACD_12_26_9', 'SMA_20', 'SMA_50', ...]
```

## Popular Indicators

### Momentum Indicators

| Indicator | Description | Column Name |
|-----------|-------------|-------------|
| **RSI** | Relative Strength Index (14) | `RSI_14` |
| **MACD** | Moving Average Convergence Divergence | `MACD_12_26_9`, `MACDh_12_26_9`, `MACDs_12_26_9` |
| **Stochastic** | Stochastic Oscillator | `STOCHk_14_3_3`, `STOCHd_14_3_3` |
| **CCI** | Commodity Channel Index | `CCI_14_0.015` |
| **Williams %R** | Williams Percent Range | `WILLR_14` |

### Trend Indicators

| Indicator | Description | Column Name |
|-----------|-------------|-------------|
| **ADX** | Average Directional Index | `ADX_14`, `DMP_14`, `DMN_14` |
| **Aroon** | Aroon Up/Down | `AROONU_25`, `AROOND_25`, `AROONOSC_25` |
| **PSAR** | Parabolic SAR | `PSARl_0.02_0.2`, `PSARs_0.02_0.2` |

### Volatility Indicators

| Indicator | Description | Column Names |
|-----------|-------------|--------------|
| **ATR** | Average True Range | `ATRr_14` |
| **Bollinger Bands** | Volatility bands | `BBL_20_2.0`, `BBM_20_2.0`, `BBU_20_2.0`, `BBB_20_2.0`, `BBP_20_2.0` |

### Volume Indicators

| Indicator | Description | Column Name |
|-----------|-------------|-------------|
| **OBV** | On Balance Volume | `OBV` |
| **VWAP** | Volume Weighted Average Price | `VWAP_D` |
| **MFI** | Money Flow Index | `MFI_14` |

### Moving Averages

| Indicator | Description | Column Name |
|-----------|-------------|-------------|
| **SMA** | Simple Moving Average | `SMA_20`, `SMA_50`, `SMA_200` |
| **EMA** | Exponential Moving Average | `EMA_12`, `EMA_26`, `EMA_50` |
| **WMA** | Weighted Moving Average | `WMA_10` |

## Practical Examples

### Screen for Overbought Stocks

```python
# Fetch multiple stocks with TA
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

overbought = []

for stock in stocks:
    df = fetcher.ta(
        symbol=stock,
        exchange='NASDAQ',
        interval='Daily',
        n_bars=100,
        indicators='common',
        append=True
    )
    
    # Get latest RSI
    latest_rsi = df['RSI_14'].iloc[-1]
    
    if latest_rsi > 70:  # Overbought condition
        overbought.append({
            'stock': stock,
            'RSI': latest_rsi,
            'close': df['close'].iloc[-1]
        })

print("Overbought stocks (RSI > 70):")
for item in overbought:
    print(f"{item['stock']}: RSI={item['RSI']:.2f}, Price={item['close']:.2f}")
```

### Find MACD Crossovers

```python
df = fetcher.ta(
    symbol='AAPL',
    exchange='NASDAQ',
    interval='Daily',
    n_bars=100,
    indicators='common',
    append=True
)

# MACD crossover signals
df['MACD_signal'] = None
df.loc[df['MACD_12_26_9'] > df['MACDs_12_26_9'], 'MACD_signal'] = 'BUY'
df.loc[df['MACD_12_26_9'] < df['MACDs_12_26_9'], 'MACD_signal'] = 'SELL'

# Show recent signals
print(df[['close', 'MACD_12_26_9', 'MACDs_12_26_9', 'MACD_signal']].tail(10))
```

### Export TA Data for Multiple Stocks

```python
from datetime import date
import pandas as pd

stocks = ['COMI', 'EGAL', 'ABUK']  # EGX stocks
stock_indicators = {}

for stock in stocks:
    # Fetch and calculate TA
    df = fetcher.get_ohlcv(stock, 'EGX', 'Daily', n_bars=200)
    df_ta = fetcher.ta(df=df, indicators='common', append=True)
    
    # Store latest values
    latest = df_ta.iloc[-1]
    stock_indicators[stock] = latest[['RSI_14', 'MACD_12_26_9', 'SMA_20', 'SMA_50']]

# Create comparison DataFrame
comparison = pd.DataFrame(stock_indicators).T
comparison.index.name = 'Stock'

# Export
fetcher.export_data(comparison, 'egx_indicators_snapshot.xlsx', format='excel')
```

## Column Naming Convention

Indicators follow this pattern: `{INDICATOR}_{PARAMETER1}_{PARAMETER2}...`

Examples:
- `RSI_14` → RSI with 14-period
- `SMA_20` → Simple Moving Average with 20-period
- `MACD_12_26_9` → MACD with fast=12, slow=26, signal=9
- `BBU_20_2.0` → Bollinger Upper Band, 20-period, 2 std dev

## Performance Tips

### 1. Use Cache for Repeated Calculations

```python
# First call fetches from API
df1 = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)  # ~3 seconds

# Subsequent calls use cache
df2 = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)  # ~0.05 seconds
```

### 2. Fetch Enough Historical Data

```python
# BAD: Not enough data for 200-period SMA
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=50)
df.ta.sma(length=200, append=True)  # Will have many NaN values

# GOOD: Sufficient historical data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=300)
df.ta.sma(length=200, append=True)  # ~100 valid values
```

### 3. Calculate What You Need

```python
# DON'T: Calculate all 130+ indicators if you only need RSI
df = fetcher.ta(df=df, indicators='all')  # Slow!

# DO: Calculate specific indicators
df = fetcher.ta(df=df, indicators=['RSI', 'MACD', 'SMA'])  # Fast!
```

## Advanced: Direct DataFrame Access

If you need more control, use the `.ta` accessor directly:

```python
import pandas as pd
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 200)

# Calculate individual indicators with custom parameters
df.ta.rsi(length=21, append=True)  # Custom RSI period
df.ta.sma(length=10, append=True)   # 10-day SMA
df.ta.sma(length=30, append=True)   # 30-day SMA
df.ta.ema(length=9, append=True)    # 9-day EMA

# Bollinger Bands with custom parameters
df.ta.bbands(length=20, std=2.5, append=True)

# MACD with custom parameters
df.ta.macd(fast=8, slow=21, signal=5, append=True)
```

## Troubleshooting

### NaN Values in Indicators

**Cause:** Not enough historical data

**Solution:**
```python
# Increase n_bars to provide sufficient lookback period
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=500)
```

### Missing Indicator Columns

**Cause:** Indicator calculation failed or name mismatch

**Solution:**
```python
# Check column names
print(df.columns.tolist())

# Check for errors
df = fetcher.ta(df=df, indicators='common', append=True)
```

## See Also

- [Data Fetching Guide](04_DATA_FETCHING.md)
- [Export Guide](06_DATA_EXPORT.md)
- [API Reference](10_API_REFERENCE.md)

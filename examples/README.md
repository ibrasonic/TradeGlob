# TradeGlob Examples

This directory contains example scripts demonstrating various features of TradeGlob.

## Examples

### 1. Basic Usage (`example_1_basic.py`)
- Fetching single stock data
- Fetching multiple stocks
- Different intervals (Daily, Weekly, Monthly)
- Cache information

**Run:**
```bash
python examples/example_1_basic.py
```

### 2. Global Markets (`example_2_global_markets.py`)
- US stocks (NASDAQ)
- Cryptocurrency (Binance)
- Forex pairs
- Symbol search

**Run:**
```bash
python examples/example_2_global_markets.py
```

### 3. Technical Analysis (`example_3_technical_analysis.py`)
- Integration with pandas_ta
- Adding technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Generating trading signals
- Strategy statistics

**Requirements:**
```bash
pip install pandas_ta
```

**Run:**
```bash
python examples/example_3_technical_analysis.py
```

### 4. Advanced Configuration (`example_4_advanced.py`)
- Custom configuration
- Parallel vs sequential fetching comparison
- Cache performance demonstration
- Full OHLCV data fetching

**Run:**
```bash
python examples/example_4_advanced.py
```

## Quick Start

1. Install requirements:
```bash
cd tradeglob
pip install -r requirements.txt
```

2. Run an example:
```bash
python examples/example_1_basic.py
```

3. (Optional) Add authentication for better stability:
```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher(
    username='your_email@example.com',
    password='your_password'
)
```

## Output

Examples print results to console. You can modify them to save data to CSV:

```python
df.to_csv('output.csv')
```

## Notes

- Examples use anonymous mode by default (no authentication)
- For better stability, create a free TradingView account
- Some examples may take time due to API rate limits
- Cache is enabled by default to speed up repeated runs

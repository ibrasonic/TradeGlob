# Data Export Guide

Export your market data to various formats for further analysis.

## Supported Formats

TradeGlob supports 5 export formats:
- **CSV** (`.csv`) - Universal text format
- **Excel** (`.xlsx`) - Microsoft Excel
- **Parquet** (`.parquet`) - Efficient columnar format
- **JSON** (`.json`) - Web-friendly format
- **HDF5** (`.h5`) - High-performance binary format

---

## Basic Export

### CSV Export

```python
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)

# Export to CSV
fetcher.export_data(df, 'aapl.csv')
# or explicitly
fetcher.export_data(df, 'aapl.csv', format='csv')
```

### Excel Export

```python
# Export to Excel
fetcher.export_data(df, 'aapl.xlsx', format='excel')
```

### Parquet Export

```python
# Export to Parquet (most efficient)
fetcher.export_data(df, 'aapl.parquet', format='parquet')
```

### JSON Export

```python
# Export to JSON
fetcher.export_data(df, 'aapl.json', format='json')
```

### HDF5 Export

```python
# Export to HDF5
fetcher.export_data(df, 'aapl.h5', format='hdf5')
```

---

## Multi-Format Export

Export to multiple formats simultaneously:

```python
# Export to CSV, Excel, and Parquet at once
paths = fetcher.export_multi_format(
    df,
    base_path='aapl_data',
    formats=['csv', 'excel', 'parquet']
)

print("Files created:")
for format_name, filepath in paths.items():
    print(f"  {format_name}: {filepath}")
```

**Output:**
```
Files created:
  csv: D:\data\aapl_data.csv
  excel: D:\data\aapl_data.xlsx
  parquet: D:\data\aapl_data.parquet
```

---

## Format-Specific Options

### CSV Options

```python
# Custom CSV delimiter
fetcher.export_data(df, 'aapl.csv', format='csv', sep=';')

# Don't include index (dates)
fetcher.export_data(df, 'aapl.csv', format='csv', index=False)

# Custom encoding
fetcher.export_data(df, 'aapl.csv', format='csv', encoding='utf-8-sig')
```

### Excel Options

```python
# Custom sheet name
fetcher.export_data(df, 'aapl.xlsx', format='excel', sheet_name='AAPL Data')

# Don't include index
fetcher.export_data(df, 'aapl.xlsx', format='excel', index=False)

# Multiple sheets
with pd.ExcelWriter('stocks.xlsx') as writer:
    df_aapl.to_excel(writer, sheet_name='AAPL')
    df_msft.to_excel(writer, sheet_name='MSFT')
```

### JSON Options

```python
# Pretty-printed JSON
fetcher.export_data(df, 'aapl.json', format='json', indent=4)

# Orient by records (more compact)
fetcher.export_data(df, 'aapl.json', format='json', orient='records')

# Default is 'index' orientation
```

### Parquet Options

```python
# Compression (default: 'snappy')
fetcher.export_data(df, 'aapl.parquet', format='parquet', compression='gzip')

# Other compression: 'brotli', 'zstd', 'lz4'
```

---

## Export Workflows

### Export After Fetching

```python
# Fetch and export in one go
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 252)
fetcher.export_data(df, 'aapl_yearly.xlsx', format='excel')
```

### Export Multiple Stocks

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

# Export to Excel
fetcher.export_data(df, 'nasdaq_stocks.xlsx', format='excel')
```

### Export with Technical Indicators

```python
# Fetch with indicators
df = fetcher.ta(
    symbol='AAPL',
    exchange='NASDAQ',
    interval='Daily',
    n_bars=100,
    indicators='common',
    append=True
)

# Export with all columns (OHLCV + indicators)
fetcher.export_data(df, 'aapl_with_ta.xlsx', format='excel')
```

---

## Advanced Export Patterns

### Separate Exports for Each Stock

```python
stocks = ['AAPL', 'MSFT', 'GOOGL']

for stock in stocks:
    df = fetcher.get_ohlcv(stock, 'NASDAQ', 'Daily', 100)
    filename = f'{stock}_data.csv'
    fetcher.export_data(df, filename)
    print(f"✓ Exported {filename}")
```

### Export with Custom Filename Pattern

```python
from datetime import datetime

# Add timestamp to filename
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'aapl_{timestamp}.xlsx'
fetcher.export_data(df, filename, format='excel')
```

### Export Filtered Data

```python
# Fetch data
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 252)

# Filter to only high-volume days
high_volume = df[df['volume'] > df['volume'].median()]

# Export filtered data
fetcher.export_data(high_volume, 'aapl_high_volume.csv')
```

### Export Summary Statistics

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

# Calculate summary stats
summary = df.describe()

# Export summary
fetcher.export_data(summary, 'stocks_summary.xlsx', format='excel')
```

---

## Export Technical Analysis Data

### Snapshot Format (Latest Values)

Export latest indicator values for multiple stocks:

```python
import pandas as pd
from datetime import date

stocks = ['AAPL', 'MSFT', 'GOOGL']
indicators_data = {}

for stock in stocks:
    # Fetch and calculate TA
    df = fetcher.get_ohlcv(stock, 'NASDAQ', 'Daily', 200)
    df_ta = fetcher.ta(df=df, indicators='common', append=True)
    
    # Get latest values
    latest = df_ta.iloc[-1]
    indicators_data[stock] = latest[['close', 'RSI_14', 'MACD_12_26_9', 'SMA_20', 'SMA_50']]

# Create comparison DataFrame
snapshot = pd.DataFrame(indicators_data).T
snapshot.index.name = 'Stock'

# Export
fetcher.export_data(snapshot, 'stocks_indicators_snapshot.xlsx', format='excel')
```

**Result (snapshot.xlsx):**
```
Stock   close    RSI_14  MACD_12_26_9  SMA_20  SMA_50
AAPL    150.20   65.32   1.25          148.50  145.20
MSFT    320.50   58.45   2.10          315.30  310.50
GOOGL   95.30    72.18   0.85          94.20   92.80
```

### Time-Series Format (Historical)

Export full time series with indicators:

```python
# Fetch with indicators
df = fetcher.ta(
    symbol='AAPL',
    exchange='NASDAQ',
    interval='Daily',
    n_bars=252,
    indicators='common',
    append=True
)

# Export full time series
fetcher.export_data(df, 'aapl_timeseries.xlsx', format='excel')
```

**Result (timeseries.xlsx):**
```
Date        close  RSI_14  MACD_12_26_9  SMA_20  SMA_50
2024-01-01  150.2  64.5    1.2           148.5   145.2
2024-01-02  151.5  66.2    1.4           149.0   145.8
...
```

---

## Format Comparison

| Format  | Size | Speed | Readability | Use Case |
|---------|------|-------|-------------|----------|
| **CSV** | Large | Fast | High | Universal, human-readable |
| **Excel** | Medium | Medium | High | Analysis in Excel, presentations |
| **Parquet** | Small | Very Fast | Low | Big data, Python/R analysis |
| **JSON** | Large | Slow | Medium | Web APIs, JavaScript |
| **HDF5** | Small | Very Fast | Low | Large datasets, scientific computing |

### Recommendations

- **General use**: Excel (`.xlsx`)
- **Large datasets**: Parquet (`.parquet`)
- **Sharing**: CSV (`.csv`)
- **Web apps**: JSON (`.json`)
- **Scientific**: HDF5 (`.h5`)

---

## File Size Comparison

Example: 252 days of OHLCV data for 10 stocks

| Format | File Size | Compression Ratio |
|--------|-----------|-------------------|
| CSV | 150 KB | 1.0x |
| Excel | 85 KB | 1.8x |
| Parquet | 25 KB | 6.0x |
| JSON | 180 KB | 0.8x |
| HDF5 | 30 KB | 5.0x |

---

## Handling Large Exports

### Export in Batches

```python
# Fetch large amount of data
stocks = [f'STOCK{i}' for i in range(100)]

# Export in batches of 20
batch_size = 20
for i in range(0, len(stocks), batch_size):
    batch = stocks[i:i+batch_size]
    
    df = fetcher.get_multiple(
        stock_list=batch,
        exchange='NASDAQ',
        interval='Daily',
        start=date(2024, 1, 1),
        end=date(2024, 12, 31)
    )
    
    filename = f'stocks_batch_{i//batch_size + 1}.parquet'
    fetcher.export_data(df, filename, format='parquet')
    print(f"✓ Exported {filename}")
```

### Use Parquet for Large Data

```python
# For datasets > 100 MB, use Parquet
large_df = fetcher.get_multiple(
    stock_list=[f'STOCK{i}' for i in range(500)],
    exchange='NASDAQ',
    interval='Daily',
    start=date(2020, 1, 1),
    end=date(2024, 12, 31)
)

# Export with compression
fetcher.export_data(
    large_df,
    'large_dataset.parquet',
    format='parquet',
    compression='zstd'  # Best compression
)
```

---

## Reading Exported Files

### Read CSV

```python
import pandas as pd

df = pd.read_csv('aapl.csv', index_col=0, parse_dates=True)
```

### Read Excel

```python
df = pd.read_excel('aapl.xlsx', index_col=0, parse_dates=True)
```

### Read Parquet

```python
df = pd.read_parquet('aapl.parquet')
```

### Read JSON

```python
df = pd.read_json('aapl.json', orient='index')
```

### Read HDF5

```python
df = pd.read_hdf('aapl.h5', key='df')
```

---

## See Also

- [Data Fetching Guide](04_DATA_FETCHING.md)
- [Technical Analysis Guide](05_TECHNICAL_ANALYSIS.md)
- [Basic Examples](03_BASIC_EXAMPLES.md)

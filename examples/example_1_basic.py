"""
Example 1: Basic Usage - Fetching Egyptian Stock Data

This example demonstrates basic usage of TradeGlob for fetching
Egyptian Exchange (EGX) stock data.
"""

import sys
import os
# Add parent directory to path if running from tradeglob folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tradeglob import TradeGlobFetcher
from datetime import date
import pandas as pd

# Initialize fetcher (anonymous mode)
# For better stability, use: TradeGlobFetcher(username='email', password='pass')
fetcher = TradeGlobFetcher()

print("=" * 70)
print("Example 1: Egyptian Stock Market (EGX)")
print("=" * 70)

# Single stock OHLCV data
print("\n1. Fetching single stock (COMI)...")
df = fetcher.get_ohlcv('COMI', 'EGX', 'Daily', n_bars=100)
print(f"✓ Fetched {len(df)} rows")
print("\nLast 5 days:")
print(df[['open', 'high', 'low', 'close', 'volume']].tail())

# Export to CSV
df.to_csv('output_1_single_stock_COMI.csv')
print("✓ Exported to: output_1_single_stock_COMI.csv")

# Multiple stocks
print("\n2. Fetching multiple stocks...")
stocks = ['COMI', 'EGAL', 'MCQE']
df_multi = fetcher.get_multiple(
    stock_list=stocks,
    exchange='EGX',
    interval='Daily',
    start=date(2025, 1, 1),
    end=date(2025, 12, 14)
)
print(f"✓ Fetched {len(df_multi)} rows for {len(df_multi.columns)} stocks")
print("\nLast 5 days:")
print(df_multi.tail())

# Export to CSV
df_multi.to_csv('output_1_multiple_stocks_daily.csv')
print("✓ Exported to: output_1_multiple_stocks_daily.csv")

# Weekly data
print("\n3. Fetching weekly data...")
df_weekly = fetcher.get_multiple(
    stock_list=stocks,
    exchange='EGX',
    interval='Weekly',
    start=date(2024, 1, 1),
    end=date(2025, 12, 14)
)
print(f"✓ Fetched {len(df_weekly)} rows")
print(df_weekly.tail())

# Export to CSV
df_weekly.to_csv('output_1_weekly_data.csv')
print("✓ Exported to: output_1_weekly_data.csv")

# Cache info
print("\n4. Cache information:")
cache_info = fetcher.get_cache_info()
print(f"Cache enabled: {cache_info['enabled']}")
print(f"Cached files: {cache_info.get('files', 0)}")
print(f"Cache size: {cache_info.get('size_mb', 0):.2f} MB")

print("\n" + "=" * 70)
print("Example completed successfully!")
print("=" * 70)

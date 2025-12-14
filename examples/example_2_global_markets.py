"""
Example 2: Global Markets - US, Crypto, Forex

This example demonstrates fetching data from different global markets:
- US stocks (NASDAQ)
- Cryptocurrency (Binance)
- Forex pairs
"""

import sys
import os
# Add parent directory to path if running from tradeglob folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tradeglob import TradeGlobFetcher
from datetime import date

fetcher = TradeGlobFetcher()

print("=" * 70)
print("Example 2: Global Markets")
print("=" * 70)

# US Tech Stocks
print("\n1. US Tech Stocks (NASDAQ)...")
us_stocks = ['AAPL', 'MSFT', 'GOOGL']
df_us = fetcher.get_multiple(
    stock_list=us_stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2025, 1, 1),
    end=date(2025, 12, 14)
)
print(f"✓ US Stocks: {len(df_us)} rows")
print(df_us.tail())

# Export to CSV
df_us.to_csv('output_2_us_stocks.csv')
print("✓ Exported to: output_2_us_stocks.csv")

# Cryptocurrency
print("\n2. Cryptocurrency (Binance)...")
cryptos = ['BTCUSD', 'ETHUSD']
df_crypto = fetcher.get_multiple(
    stock_list=cryptos,
    exchange='BINANCE',
    interval='Daily',
    start=date(2025, 1, 1),
    end=date(2025, 12, 14)
)
print(f"✓ Crypto: {len(df_crypto)} rows")
print(df_crypto.tail())

# Export to CSV
df_crypto.to_csv('output_2_crypto.csv')
print("✓ Exported to: output_2_crypto.csv")

# Forex
print("\n3. Forex Pairs...")
forex_pairs = ['EURUSD', 'GBPUSD']
df_forex = fetcher.get_multiple(
    stock_list=forex_pairs,
    exchange='FX_IDC',
    interval='Daily',
    start=date(2025, 1, 1),
    end=date(2025, 12, 14)
)
print(f"✓ Forex: {len(df_forex)} rows")
print(df_forex.tail())

# Export to CSV
df_forex.to_csv('output_2_forex.csv')
print("✓ Exported to: output_2_forex.csv")

print("\n" + "=" * 70)
print("Global markets example completed!")
print("=" * 70)

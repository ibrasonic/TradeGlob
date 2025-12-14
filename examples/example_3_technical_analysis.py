"""
Example 3: Integration with pandas_ta

This example demonstrates integrating TradeGlob with pandas_ta
for technical analysis.
"""

import sys
import os
# Add parent directory to path if running from tradeglob folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tradeglob import TradeGlobFetcher
from datetime import date

try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    print("pandas_ta not installed. Install with: pip install pandas_ta")
    HAS_PANDAS_TA = False

fetcher = TradeGlobFetcher()

print("=" * 70)
print("Example 3: Technical Analysis with pandas_ta")
print("=" * 70)

if not HAS_PANDAS_TA:
    print("Please install pandas_ta to run this example:")
    print("pip install pandas_ta")
    exit(1)

# Fetch data
print("\n1. Fetching AAPL data...")
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=252)
print(f"✓ Fetched {len(df)} rows")

# Add technical indicators
print("\n2. Adding technical indicators...")

# Momentum indicators
df.ta.rsi(length=14, append=True)
df.ta.macd(append=True)
df.ta.stoch(append=True)

# Trend indicators
df.ta.sma(length=20, append=True)
df.ta.ema(length=50, append=True)
df.ta.ema(length=200, append=True)

# Volatility indicators
df.ta.bbands(append=True)
df.ta.atr(append=True)

# Volume indicators
df.ta.obv(append=True)

print("✓ Added indicators")

# Display results
print("\n3. Results with indicators:")
columns_to_show = [
    'close', 
    'RSI_14', 
    'MACD_12_26_9', 
    'SMA_20', 
    'EMA_50',
    'BBM_5_2.0',
    'ATRr_14'
]

# Filter columns that exist
existing_cols = [col for col in columns_to_show if col in df.columns]
print(df[existing_cols].tail(10))

# Export to CSV
df.to_csv('output_3_technical_analysis.csv')
print("\n✓ Exported to: output_3_technical_analysis.csv")

# Trading signals
print("\n4. Simple trading signals:")
df['Signal'] = 'HOLD'
df.loc[(df['RSI_14'] < 30) & (df['close'] < df['BBL_5_2.0']), 'Signal'] = 'BUY'
df.loc[(df['RSI_14'] > 70) & (df['close'] > df['BBU_5_2.0']), 'Signal'] = 'SELL'

signals = df[df['Signal'] != 'HOLD'][['close', 'RSI_14', 'Signal']]
if not signals.empty:
    print(f"Found {len(signals)} trading signals:")
    print(signals.tail())
else:
    print("No trading signals in recent data")

# Strategy performance
print("\n5. Strategy statistics:")
print(f"Total signals: {len(df[df['Signal'] != 'HOLD'])}")
print(f"BUY signals: {len(df[df['Signal'] == 'BUY'])}")
print(f"SELL signals: {len(df[df['Signal'] == 'SELL'])}")
print(f"Current RSI: {df['RSI_14'].iloc[-1]:.2f}")
print(f"Current Signal: {df['Signal'].iloc[-1]}")

print("\n" + "=" * 70)
print("Technical analysis example completed!")
print("=" * 70)

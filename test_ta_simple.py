"""Quick TA import test"""
print("1. Testing import...")
from tradeglob.ta import version
print(f"   ✓ TradeGlob TA version: {version}")

print("\n2. Testing DataFrame accessor...")
import pandas as pd
df = pd.DataFrame({
    'open': [100, 101, 102],
    'high': [102, 103, 104],
    'low': [99, 100, 101],
    'close': [101, 102, 103],
    'volume': [1000, 1100, 1200]
})

# Test if .ta accessor is available
print(f"   DataFrame has .ta accessor: {hasattr(df, 'ta')}")

# Try a simple indicator
df.ta.sma(length=2, append=True)
print(f"   ✓ SMA calculated, columns: {list(df.columns)}")

print("\n✓ TA module working!")

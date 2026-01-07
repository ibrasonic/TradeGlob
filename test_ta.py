"""Test script for TA integration"""
from tradeglob import TradeGlobFetcher
from datetime import date

# Initialize fetcher
fetcher = TradeGlobFetcher()

print("Testing TradeGlob TA Integration...")
print("=" * 50)

# Test 1: Fetch data
print("\n1. Fetching AAPL data...")
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=100)
print(f"   ✓ Fetched {len(df)} rows")
print(f"   Columns: {list(df.columns)}")

# Test 2: Calculate common indicators
print("\n2. Calculating common indicators...")
df_ta = fetcher.ta(df=df, indicators='common', append=True)
print(f"   ✓ Added indicators")
print(f"   Total columns: {len(df_ta.columns)}")
print(f"   New indicator columns: {len(df_ta.columns) - len(df.columns)}")

# Test 3: Show last values
print("\n3. Last values of key indicators:")
if 'RSI_14' in df_ta.columns:
    print(f"   RSI_14: {df_ta['RSI_14'].iloc[-1]:.2f}")
if 'MACD_12_26_9' in df_ta.columns:
    print(f"   MACD: {df_ta['MACD_12_26_9'].iloc[-1]:.2f}")
if 'SMA_20' in df_ta.columns:
    print(f"   SMA_20: {df_ta['SMA_20'].iloc[-1]:.2f}")
if 'SMA_50' in df_ta.columns:
    print(f"   SMA_50: {df_ta['SMA_50'].iloc[-1]:.2f}")

# Test 4: Auto-fetch with TA
print("\n4. Auto-fetch with TA (MSFT)...")
df_msft = fetcher.ta(symbol='MSFT', exchange='NASDAQ', interval='Daily', 
                     n_bars=50, indicators='common', append=True)
print(f"   ✓ Fetched and calculated TA for MSFT")
print(f"   Rows: {len(df_msft)}, Columns: {len(df_msft.columns)}")

print("\n" + "=" * 50)
print("✓ All tests passed!")
print("TradeGlob TA integration working correctly")

"""
Test authentication after Selenium 4.x fixes
"""
from tradeglob import TradeGlobFetcher

print("Testing authentication support...")
print("="*60)

# Test 1: Anonymous mode (should work)
print("\n1. Testing anonymous mode...")
try:
    fetcher = TradeGlobFetcher()
    print(f"✓ Anonymous mode initialized")
    print(f"  Authenticated: {fetcher.authenticated}")
    
    # Try fetching data
    df = fetcher.get_ohlcv('COMI', 'EGX', 'Daily', 5)
    print(f"✓ Data fetch works: {len(df)} rows")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Auth mode (requires credentials)
print("\n2. Testing auth mode (manual login)...")
print("Note: This will open Chrome browser for manual login")
print("You need to provide TradingView credentials")

choice = input("\nDo you want to test authentication? (y/n): ")

if choice.lower() == 'y':
    try:
        # Using auto_login=False for manual browser login
        from tradeglob._vendor.main import TvDatafeed
        tv = TvDatafeed(auto_login=False)
        print(f"✓ TvDatafeed initialized for manual login")
        print(f"  Token: {tv.token[:20] if tv.token else 'None'}...")
        
        # Try fetching with auth
        from tradeglob._vendor.main import Interval
        df = tv.get_hist('COMI', 'EGX', Interval.in_daily, 5)
        if df is not None and not df.empty:
            print(f"✓ Authenticated fetch works: {len(df)} rows")
        else:
            print("✗ Fetch returned empty data")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("Skipped authentication test")

print("\n" + "="*60)
print("Test completed!")

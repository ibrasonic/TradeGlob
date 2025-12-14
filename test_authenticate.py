"""
Test script for TradeGlob authenticate() method
"""

from tradeglob import TradeGlobFetcher

print("Testing TradeGlob authenticate() method")
print("=" * 60)

# Test 1: Start anonymous, then authenticate
print("\n1. Testing authenticate() method with browser...")
print("-" * 60)

fetcher = TradeGlobFetcher()
print(f"Initial state: authenticated = {fetcher.authenticated}")

# Prompt for authentication
proceed = input("\nOpen browser for manual login? (y/n): ").strip().lower()

if proceed == 'y':
    print("\nOpening browser for manual login...")
    print("Follow the instructions in the browser to login to TradingView")
    
    success = fetcher.authenticate()
    
    if success:
        print("✓ Authentication successful!")
        print(f"  authenticated = {fetcher.authenticated}")
        
        # Test data fetch with auth
        print("\nTesting data fetch with authentication...")
        try:
            df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=5)
            print(f"✓ Data fetch successful: {len(df)} rows")
            print(df.head())
        except Exception as e:
            print(f"✗ Data fetch failed: {e}")
    else:
        print("✗ Authentication failed")
        print(f"  authenticated = {fetcher.authenticated}")
else:
    print("Skipped authentication test")

# Test 2: Initialize with manual login from start
print("\n\n2. Testing initialization with manual login from start...")
print("-" * 60)

proceed2 = input("Open browser for manual login during initialization? (y/n): ").strip().lower()

if proceed2 == 'y':
    print("\nInitializing with manual login...")
    print("Follow the instructions in the browser to login to TradingView")
    
    # Note: This will still use anonymous mode, then authenticate separately
    fetcher2 = TradeGlobFetcher()
    success2 = fetcher2.authenticate()
    
    print(f"✓ Initialized: authenticated = {fetcher2.authenticated}")
    
    if fetcher2.authenticated:
        # Test data fetch
        print("\nTesting data fetch...")
        try:
            df = fetcher2.get_ohlcv('MSFT', 'NASDAQ', 'Daily', n_bars=5)
            print(f"✓ Data fetch successful: {len(df)} rows")
            print(df.head())
        except Exception as e:
            print(f"✗ Data fetch failed: {e}")
else:
    print("Skipped initialization test")

print("\n" + "=" * 60)
print("Test completed!")

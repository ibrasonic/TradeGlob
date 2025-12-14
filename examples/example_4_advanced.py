"""
Example 4: Advanced Configuration

This example demonstrates advanced configuration options:
- Custom retry settings
- Parallel vs sequential fetching
- Cache management
- Data validation
"""

import sys
import os
# Add parent directory to path if running from tradeglob folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tradeglob import TradeGlobFetcher, FetcherConfig
from datetime import date
import time

print("=" * 70)
print("Example 4: Advanced Configuration")
print("=" * 70)

# Custom configuration
print("\n1. Creating custom configuration...")
config = FetcherConfig(
    retry_attempts=30,           # More retries for unstable connections
    retry_delay=1.0,             # Longer delay between retries
    max_workers=10,              # More parallel workers
    cache_enabled=True,          # Enable caching
    cache_max_age_hours=48,      # Cache valid for 48 hours
    safety_buffer=1.5,           # Request 50% more bars
    log_level='INFO',            # Logging level
    progress_bar=True,           # Show progress bars
    validate_data=True           # Validate data quality
)

fetcher = TradeGlobFetcher(config=config)
print("✓ Custom configuration applied")

# Performance comparison: Parallel vs Sequential
print("\n2. Performance comparison...")
stocks = ['COMI', 'EGAL', 'MCQE', 'HRHO', 'PHDC']
start_date = date(2025, 1, 1)
end_date = date(2025, 12, 14)

# Parallel fetching
print("\n  a) Parallel fetching:")
start = time.time()
df_parallel = fetcher.get_multiple(
    stock_list=stocks,
    exchange='EGX',
    interval='Daily',
    start=start_date,
    end=end_date,
    parallel=True
)
parallel_time = time.time() - start
print(f"     ✓ Completed in {parallel_time:.2f} seconds")df_parallel.to_csv('output_4_parallel.csv')
print("     ✓ Exported to: output_4_parallel.csv")
# Sequential fetching (with cache disabled for fair comparison)
print("\n  b) Sequential fetching:")
fetcher.clear_cache()  # Clear cache for fair comparison
start = time.time()
df_sequential = fetcher.get_multiple(
    stock_list=stocks,
    exchange='EGX',
    interval='Daily',
    start=start_date,
    end=end_date,
    parallel=False
)
sequential_time = time.time() - start
print(f"     ✓ Completed in {sequential_time:.2f} seconds")

print(f"\n  Speedup: {sequential_time/parallel_time:.1f}x faster with parallel fetching")

# Cache demonstration
print("\n3. Cache demonstration...")
print("  a) First fetch (no cache):")
fetcher.clear_cache()
start = time.time()
df1 = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=100)
time1 = time.time() - start
print(f"     Time: {time1:.2f} seconds")

print("\n  b) Second fetch (with cache):")
start = time.time()
df2 = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=100)
time2 = time.time() - start
print(f"     Time: {time2:.2f} seconds")
print(f"     Speedup: {time1/time2:.1f}x faster with cache")

# Cache management
print("\n4. Cache management...")
cache_info = fetcher.get_cache_info()
print(f"  Cache location: {cache_info['location']}")
print(f"  Cached files: {cache_info['files']}")
print(f"  Cache size: {cache_info['size_mb']:.2f} MB")

# Full OHLCV data
print("\n5. Fetching full OHLCV data...")
stocks = ['AAPL', 'MSFT']
df_full = fetcher.get_multiple(
    stock_list=stocks,
    exchange='NASDAQ',
    interval='Daily',
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    columns='all'  # Get all OHLCV columns
)
print(f"✓ Fetched full OHLCV: {df_full.shape}")
print("\nAvailable columns:")
print(df_full.columns.tolist()[:10], "...")

# Access specific stock's data
print("\nAAPL High prices (last 5):")
print(df_full[('AAPL', 'high')].tail())

print("\n" + "=" * 70)
print("Advanced configuration example completed!")
print("=" * 70)

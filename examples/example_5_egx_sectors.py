"""
Example 5: EGX Sector Browsing & Sector-Based Fetching

Demonstrates how to:
- List all EGX sectors
- Browse stocks within a sector
- Fetch OHLCV data for an entire sector in one call
- Compare sector performance
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tradeglob import TradeGlobFetcher, EGX_SECTORS, list_egx_sectors, get_egx_sector_stocks
from datetime import date

fetcher = TradeGlobFetcher()

print("=" * 70)
print("Example 5: EGX Sector Browsing")
print("=" * 70)

# ── 1. List all available EGX sectors ────────────────────────────────────────
print("\n1. Available EGX sectors:")
sectors = list_egx_sectors()          # or: fetcher.list_sectors('EGX')
for i, sector in enumerate(sectors, 1):
    n = len(EGX_SECTORS[sector])
    print(f"   {i:2d}. {sector:<40} ({n} stocks)")

# ── 2. Pick a sector and inspect its stocks ───────────────────────────────────
print("\n2. Stocks in the 'Banking' sector:")
banking_stocks = get_egx_sector_stocks("Banking")   # standalone helper
# or: fetcher.get_sector_stocks("Banking", "EGX")
print(f"   {', '.join(banking_stocks)}")

print("\n   Stocks in 'Real Estate & Housing':")
real_estate = fetcher.get_sector_stocks("Real Estate & Housing", "EGX")
print(f"   {', '.join(real_estate)}")

# ── 3. Fetch closing prices for all banking stocks ────────────────────────────
print("\n3. Fetching daily closing prices for the Banking sector...")
df_banking = fetcher.get_sector(
    sector="Banking",
    exchange="EGX",
    interval="Daily",
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    columns="close",
)
print(f"   ✓ Shape: {df_banking.shape}  (rows × stocks)")
print("\n   Last 5 trading days:")
print(df_banking.tail())
df_banking.to_csv("output_5_egx_banking_sector.csv")
print("   ✓ Exported to: output_5_egx_banking_sector.csv")

# ── 4. Fetch full OHLCV for a sector without a date range ─────────────────────
print("\n4. Fetching last 50 bars (all OHLCV) for Telecom sector...")
df_telecom = fetcher.get_sector(
    sector="Telecommunications",
    exchange="EGX",
    interval="Daily",
    n_bars=50,
    columns="all",
)
print(f"   ✓ Shape: {df_telecom.shape}")
print(df_telecom.tail())
df_telecom.to_csv("output_5_egx_telecom_sector.csv")
print("   ✓ Exported to: output_5_egx_telecom_sector.csv")

# ── 5. Quick sector comparison: annual returns ────────────────────────────────
print("\n5. Sector performance snapshot (Banking vs Real Estate, 2024)...")

df_re = fetcher.get_sector(
    sector="Real Estate & Housing",
    exchange="EGX",
    interval="Daily",
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    columns="close",
)

for label, df in [("Banking", df_banking), ("Real Estate & Housing", df_re)]:
    valid = df.dropna(axis=1, how='all')
    if valid.empty:
        print(f"   {label}: no data")
        continue
    first = valid.iloc[0]
    last = valid.iloc[-1]
    annual_ret = ((last / first) - 1) * 100
    print(f"\n   {label} annual returns:")
    for sym, ret in annual_ret.items():
        print(f"      {sym:<8} {ret:+.1f}%")

print("\n" + "=" * 70)
print("EGX sector example completed!")
print("=" * 70)

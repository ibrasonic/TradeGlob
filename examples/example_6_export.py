"""
Example 6: Data Export - Multiple Formats

This example demonstrates exporting data to various formats:
CSV, Excel, Parquet, JSON, HDF5
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path if running from tradeglob folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tradeglob import TradeGlobFetcher
from datetime import date

fetcher = TradeGlobFetcher()

print("=" * 70)
print("Example 6: Data Export - Multiple Formats")
print("=" * 70)

# Fetch some data
print("\n1. Fetching Egyptian stocks data...")
stocks = ['COMI', 'EGAL', 'MCQE']
df = fetcher.get_multiple(
    stock_list=stocks,
    exchange='EGX',
    interval='Daily',
    start=date(2025, 1, 1),
    end=date(2025, 12, 14)
)
print(f"✓ Fetched {len(df)} rows for {len(df.columns)} stocks")
print("\nData preview:")
print(df.head())

# Export to CSV
print("\n" + "=" * 70)
print("2. Exporting to CSV...")
print("=" * 70)
csv_path = fetcher.export_data(df, 'output_6_stocks.csv', format='csv')
print(f"✓ CSV: {csv_path}")

# Export to Excel
print("\n" + "=" * 70)
print("3. Exporting to Excel...")
print("=" * 70)
try:
    excel_path = fetcher.export_data(df, 'output_6_stocks.xlsx', format='excel')
    print(f"✓ Excel: {excel_path}")
except ImportError as e:
    print(f"⚠ Excel export requires openpyxl: pip install openpyxl")
    print(f"  Error: {e}")

# Export to Parquet (efficient for large datasets)
print("\n" + "=" * 70)
print("4. Exporting to Parquet (compressed)...")
print("=" * 70)
try:
    parquet_path = fetcher.export_data(df, 'output_6_stocks.parquet', format='parquet')
    print(f"✓ Parquet: {parquet_path}")
except ImportError as e:
    print(f"⚠ Parquet export requires pyarrow: pip install pyarrow")
    print(f"  Error: {e}")

# Export to JSON
print("\n" + "=" * 70)
print("5. Exporting to JSON...")
print("=" * 70)
json_path = fetcher.export_data(
    df, 'output_6_stocks.json',
    format='json',
    orient='records',
    indent=2
)
print(f"✓ JSON: {json_path}")

# Export to HDF5 (great for large time series)
print("\n" + "=" * 70)
print("6. Exporting to HDF5...")
print("=" * 70)
try:
    hdf5_path = fetcher.export_data(df, 'output_6_stocks.h5', format='hdf5')
    print(f"✓ HDF5: {hdf5_path}")
except ImportError as e:
    print(f"⚠ HDF5 export requires tables: pip install tables")
    print(f"  Error: {e}")

# Export to multiple formats at once
print("\n" + "=" * 70)
print("7. Exporting to multiple formats at once...")
print("=" * 70)
paths = fetcher.export_multi_format(
    df,
    'output_6_multi',
    formats=['csv', 'json']  # Start with formats that don't need extra deps
)
print("✓ Created files:")
for fmt, path in paths.items():
    print(f"  - {fmt.upper()}: {path}")

# Example with different timeframes
print("\n" + "=" * 70)
print("8. Exporting multiple timeframes to Excel...")
print("=" * 70)

# Fetch daily data
df_daily = fetcher.get_multiple(
    stock_list=['COMI', 'EGAL'],
    exchange='EGX',
    interval='Daily',
    start=date(2025, 11, 1),
    end=date(2025, 12, 14)
)

# Fetch weekly data
df_weekly = fetcher.get_multiple(
    stock_list=['COMI', 'EGAL'],
    exchange='EGX',
    interval='Weekly',
    start=date(2025, 1, 1),
    end=date(2025, 12, 14)
)

try:
    # Export to Excel with multiple sheets
    from tradeglob.utils.export import export_to_excel
    
    excel_multi = export_to_excel(
        {
            'Daily': df_daily,
            'Weekly': df_weekly
        },
        'output_6_multi_timeframe.xlsx'
    )
    print(f"✓ Multi-sheet Excel: {excel_multi}")
    print(f"  - Sheet 'Daily': {len(df_daily)} rows")
    print(f"  - Sheet 'Weekly': {len(df_weekly)} rows")
except ImportError:
    print("⚠ Multi-sheet Excel requires openpyxl: pip install openpyxl")

print("\n" + "=" * 70)
print("Example completed!")
print("=" * 70)

print("\nSupported formats:")
print("  ✓ CSV - Universal, human-readable")
print("  ✓ Excel - Multiple sheets, business-friendly")
print("  ✓ Parquet - Compressed, fast, best for big data")
print("  ✓ JSON - Web APIs, configuration")
print("  ✓ HDF5 - Scientific data, very large datasets")

print("\nInstall optional dependencies:")
print("  pip install openpyxl  # For Excel")
print("  pip install pyarrow   # For Parquet")
print("  pip install tables    # For HDF5")

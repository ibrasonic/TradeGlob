"""
Data export utilities for TradeGlob

Supports multiple formats: CSV, Excel, Parquet, JSON, HDF5
"""

import pandas as pd
from pathlib import Path
from typing import Union, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def export_to_csv(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    include_index: bool = True,
    fill_missing: Union[int, float, str] = 0,
    **kwargs
) -> str:
    """
    Export DataFrame to CSV
    
    Args:
        df: DataFrame to export
        filepath: Output file path
        include_index: Include index in CSV
        fill_missing: Value to replace NaN/missing values (default: 0)
        **kwargs: Additional pandas to_csv arguments
        
    Returns:
        Absolute path to created file
        
    Example:
        >>> export_to_csv(df, 'stocks.csv')
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Fill missing values
    df_export = df.fillna(fill_missing)
    
    df_export.to_csv(filepath, index=include_index, **kwargs)
    logger.info(f"✓ Exported to CSV: {filepath}")
    
    return str(filepath.absolute())


def export_to_excel(
    data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
    filepath: Union[str, Path],
    include_index: bool = True,
    sheet_name: str = 'Sheet1',
    fill_missing: Union[int, float, str] = 0,
    **kwargs
) -> str:
    """
    Export DataFrame(s) to Excel
    
    Args:
        data: Single DataFrame or dict of {sheet_name: DataFrame}
        filepath: Output file path (.xlsx)
        include_index: Include index in Excel
        sheet_name: Sheet name (if data is single DataFrame)
        fill_missing: Value to replace NaN/missing values (default: 0)
        **kwargs: Additional pandas to_excel arguments
        
    Returns:
        Absolute path to created file
        
    Example:
        >>> # Single sheet
        >>> export_to_excel(df, 'stocks.xlsx')
        
        >>> # Multiple sheets
        >>> export_to_excel({
        ...     'Daily': df_daily,
        ...     'Weekly': df_weekly
        ... }, 'multi_stocks.xlsx')
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure .xlsx extension
    if filepath.suffix.lower() not in ['.xlsx', '.xls']:
        filepath = filepath.with_suffix('.xlsx')
    
    try:
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if isinstance(data, dict):
                # Multiple sheets
                for sheet, df in data.items():
                    df_export = df.fillna(fill_missing)
                    df_export.to_excel(writer, sheet_name=sheet, index=include_index, **kwargs)
                    logger.debug(f"  ✓ Sheet '{sheet}': {len(df)} rows")
                logger.info(f"✓ Exported {len(data)} sheets to Excel: {filepath}")
            else:
                # Single sheet
                df_export = data.fillna(fill_missing)
                df_export.to_excel(writer, sheet_name=sheet_name, index=include_index, **kwargs)
                logger.info(f"✓ Exported to Excel: {filepath}")
    except ImportError:
        raise ImportError(
            "openpyxl required for Excel export. Install with: pip install openpyxl"
        )
    
    return str(filepath.absolute())


def export_to_parquet(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    compression: str = 'snappy',
    fill_missing: Union[int, float, str] = 0,
    **kwargs
) -> str:
    """
    Export DataFrame to Parquet (efficient binary format)
    
    Args:
        df: DataFrame to export
        filepath: Output file path (.parquet)
        compression: Compression algorithm ('snappy', 'gzip', 'brotli', 'none')
        fill_missing: Value to replace NaN/missing values (default: 0)
        **kwargs: Additional pandas to_parquet arguments
        
    Returns:
        Absolute path to created file
        
    Example:
        >>> export_to_parquet(df, 'stocks.parquet')
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure .parquet extension
    if filepath.suffix.lower() != '.parquet':
        filepath = filepath.with_suffix('.parquet')
    
    try:
        # Fill missing values
        df_export = df.fillna(fill_missing)
        
        df_export.to_parquet(filepath, compression=compression, **kwargs)
        
        # Show file size
        size_mb = filepath.stat().st_size / (1024 * 1024)
        logger.info(f"✓ Exported to Parquet: {filepath} ({size_mb:.2f} MB)")
    except ImportError:
        raise ImportError(
            "pyarrow or fastparquet required for Parquet export. "
            "Install with: pip install pyarrow"
        )
    
    return str(filepath.absolute())


def export_to_json(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    orient: str = 'records',
    indent: int = 2,
    fill_missing: Union[int, float, str] = 0,
    **kwargs
) -> str:
    """
    Export DataFrame to JSON
    
    Args:
        df: DataFrame to export
        filepath: Output file path (.json)
        orient: JSON orientation ('records', 'index', 'columns', 'values', 'split')
        indent: JSON indentation (None for compact)
        fill_missing: Value to replace NaN/missing values (default: 0)
        **kwargs: Additional pandas to_json arguments
        
    Returns:
        Absolute path to created file
        
    Example:
        >>> export_to_json(df, 'stocks.json')
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure .json extension
    if filepath.suffix.lower() != '.json':
        filepath = filepath.with_suffix('.json')
    
    # Fill missing values
    df_export = df.fillna(fill_missing)
    
    df_export.to_json(filepath, orient=orient, indent=indent, **kwargs)
    logger.info(f"✓ Exported to JSON: {filepath}")
    
    return str(filepath.absolute())


def export_to_hdf5(
    data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
    filepath: Union[str, Path],
    key: str = 'data',
    mode: str = 'w',
    complevel: int = 9,
    fill_missing: Union[int, float, str] = 0,
    **kwargs
) -> str:
    """
    Export DataFrame(s) to HDF5 (efficient for large datasets)
    
    Args:
        data: Single DataFrame or dict of {key: DataFrame}
        filepath: Output file path (.h5 or .hdf5)
        key: Key name (if data is single DataFrame)
        mode: File mode ('w' = write, 'a' = append)
        complevel: Compression level (0-9)
        fill_missing: Value to replace NaN/missing values (default: 0)
        **kwargs: Additional pandas to_hdf arguments
        
    Returns:
        Absolute path to created file
        
    Example:
        >>> export_to_hdf5(df, 'stocks.h5')
        
        >>> # Multiple datasets
        >>> export_to_hdf5({
        ...     'daily': df_daily,
        ...     'weekly': df_weekly
        ... }, 'multi_stocks.h5')
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure .h5 or .hdf5 extension
    if filepath.suffix.lower() not in ['.h5', '.hdf5']:
        filepath = filepath.with_suffix('.h5')
    
    try:
        if isinstance(data, dict):
            # Multiple datasets
            for k, df in data.items():
                df_export = df.fillna(fill_missing)
                df_export.to_hdf(filepath, key=k, mode='a' if k != list(data.keys())[0] else mode,
                         complevel=complevel, **kwargs)
                logger.debug(f"  ✓ Key '{k}': {len(df)} rows")
            logger.info(f"✓ Exported {len(data)} datasets to HDF5: {filepath}")
        else:
            # Single dataset
            df_export = data.fillna(fill_missing)
            df_export.to_hdf(filepath, key=key, mode=mode, complevel=complevel, **kwargs)
            logger.info(f"✓ Exported to HDF5: {filepath}")
            
        # Show file size
        size_mb = filepath.stat().st_size / (1024 * 1024)
        logger.info(f"  File size: {size_mb:.2f} MB")
    except ImportError:
        raise ImportError(
            "tables (PyTables) required for HDF5 export. Install with: pip install tables"
        )
    
    return str(filepath.absolute())


def export_multi_format(
    df: pd.DataFrame,
    base_path: Union[str, Path],
    formats: List[str] = ['csv', 'parquet'],
    **kwargs
) -> Dict[str, str]:
    """
    Export DataFrame to multiple formats at once
    
    Args:
        df: DataFrame to export
        base_path: Base path (without extension)
        formats: List of formats ('csv', 'excel', 'parquet', 'json', 'hdf5')
        **kwargs: Additional export arguments
        
    Returns:
        Dict of {format: filepath}
        
    Example:
        >>> paths = export_multi_format(df, 'stocks', formats=['csv', 'parquet', 'excel'])
        >>> # Creates: stocks.csv, stocks.parquet, stocks.xlsx
    """
    base_path = Path(base_path).with_suffix('')  # Remove extension if present
    results = {}
    
    format_map = {
        'csv': (export_to_csv, '.csv'),
        'excel': (export_to_excel, '.xlsx'),
        'parquet': (export_to_parquet, '.parquet'),
        'json': (export_to_json, '.json'),
        'hdf5': (export_to_hdf5, '.h5')
    }
    
    for fmt in formats:
        fmt_lower = fmt.lower()
        if fmt_lower not in format_map:
            logger.warning(f"Unknown format: {fmt}")
            continue
            
        export_func, ext = format_map[fmt_lower]
        filepath = str(base_path) + ext
        
        try:
            results[fmt_lower] = export_func(df, filepath, **kwargs)
        except Exception as e:
            logger.error(f"Failed to export {fmt}: {e}")
    
    logger.info(f"✓ Exported to {len(results)} formats")
    return results

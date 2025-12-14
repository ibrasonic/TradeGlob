"""Input validation and data quality checks"""

import pandas as pd
import logging
from datetime import date
from typing import Optional, List, Union

logger = logging.getLogger(__name__)


def validate_inputs(
    symbol: Optional[str] = None,
    exchange: Optional[str] = None,
    interval: Optional[str] = None,
    start: Optional[date] = None,
    end: Optional[date] = None,
    n_bars: Optional[int] = None,
    stock_list: Optional[List[str]] = None
) -> bool:
    """
    Validate input parameters
    
    Args:
        symbol: Stock symbol
        exchange: Exchange code
        interval: Time interval
        start: Start date
        end: End date
        n_bars: Number of bars
        stock_list: List of stock symbols
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    from .exceptions import ValidationError
    
    # Validate symbol
    if symbol is not None:
        if not symbol or not isinstance(symbol, str):
            raise ValidationError("symbol must be a non-empty string")
        if len(symbol) > 20:
            raise ValidationError("symbol too long (max 20 characters)")
    
    # Validate exchange
    if exchange is not None:
        if not exchange or not isinstance(exchange, str):
            raise ValidationError("exchange must be a non-empty string")
    
    # Validate interval
    valid_intervals = [
        'Daily', 'Weekly', 'Monthly',
        '1 Minute', '3 Minute', '5 Minute', '15 Minute', '30 Minute', '45 Minute',
        '1 Hour', '2 Hour', '3 Hour', '4 Hour'
    ]
    if interval is not None:
        if interval not in valid_intervals:
            raise ValidationError(
                f"Invalid interval: {interval}. Must be one of: {', '.join(valid_intervals)}"
            )
    
    # Validate dates
    if start and end:
        if start > end:
            raise ValidationError(f"Start date ({start}) cannot be after end date ({end})")
        
        # Check if date range is reasonable
        days_diff = (end - start).days
        if days_diff > 365 * 50:  # 50 years
            logger.warning(f"Very large date range: {days_diff} days")
        if days_diff < 0:
            raise ValidationError("Date range is negative")
    
    # Validate n_bars
    if n_bars is not None:
        if not isinstance(n_bars, int) or n_bars <= 0:
            raise ValidationError(f"n_bars must be a positive integer, got {n_bars}")
        
        if n_bars > 5000:
            logger.warning(f"n_bars={n_bars} exceeds TradingView limit of 5000, will be capped")
    
    # Validate stock_list
    if stock_list is not None:
        if not isinstance(stock_list, list):
            raise ValidationError("stock_list must be a list")
        
        if not stock_list:
            raise ValidationError("stock_list cannot be empty")
        
        if len(stock_list) > 100:
            logger.warning(f"Large stock list: {len(stock_list)} symbols. This may take a while.")
        
        for stock in stock_list:
            if not isinstance(stock, str) or not stock:
                raise ValidationError(f"Invalid stock symbol in list: {stock}")
    
    return True


def validate_data_quality(df: pd.DataFrame, symbol: str) -> dict:
    """
    Validate data quality and return quality report
    
    Args:
        df: DataFrame to validate
        symbol: Symbol name for logging
        
    Returns:
        dict: Quality report with issues found
    """
    issues = []
    warnings = []
    
    if df is None or df.empty:
        return {
            'valid': False,
            'issues': ['DataFrame is empty'],
            'warnings': [],
            'passed': False
        }
    
    # Check for missing data
    if df.isnull().any().any():
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        issues.append(f"Missing values: {missing.to_dict()}")
    
    # Check columns
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
    
    # Check price relationships (if all columns present)
    if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
        # High >= Low
        invalid_high_low = df[df['high'] < df['low']]
        if not invalid_high_low.empty:
            issues.append(f"Invalid prices (high < low): {len(invalid_high_low)} rows")
        
        # High >= Open, Close
        invalid_high_open = df[df['high'] < df['open']]
        if not invalid_high_open.empty:
            warnings.append(f"High < Open: {len(invalid_high_open)} rows")
        
        invalid_high_close = df[df['high'] < df['close']]
        if not invalid_high_close.empty:
            warnings.append(f"High < Close: {len(invalid_high_close)} rows")
        
        # Low <= Open, Close
        invalid_low_open = df[df['low'] > df['open']]
        if not invalid_low_open.empty:
            warnings.append(f"Low > Open: {len(invalid_low_open)} rows")
        
        invalid_low_close = df[df['low'] > df['close']]
        if not invalid_low_close.empty:
            warnings.append(f"Low > Close: {len(invalid_low_close)} rows")
    
    # Check for zero/negative prices
    if 'close' in df.columns:
        zero_prices = df[df['close'] <= 0]
        if not zero_prices.empty:
            issues.append(f"Zero/negative prices: {len(zero_prices)} rows")
    
    # Check for zero volume (warning only)
    if 'volume' in df.columns:
        zero_volume = df[df['volume'] == 0]
        if not zero_volume.empty:
            warnings.append(f"Zero volume: {len(zero_volume)} rows ({len(zero_volume)/len(df)*100:.1f}%)")
    
    # Check for extreme price changes (>50% in one bar)
    if 'close' in df.columns and len(df) > 1:
        pct_change = df['close'].pct_change().abs()
        extreme = pct_change[pct_change > 0.5]
        if not extreme.empty:
            warnings.append(
                f"Extreme price changes (>50%): {len(extreme)} rows. "
                f"Max: {pct_change.max()*100:.1f}%"
            )
    
    # Check for duplicate indices
    if df.index.duplicated().any():
        duplicates = df.index[df.index.duplicated()].unique()
        issues.append(f"Duplicate timestamps: {len(duplicates)}")
    
    # Check if data is sorted
    if not df.index.is_monotonic_increasing:
        warnings.append("Data is not sorted by time")
    
    # Log results
    passed = len(issues) == 0
    
    if issues:
        logger.warning(f"{symbol} quality issues: {'; '.join(issues)}")
    if warnings:
        logger.info(f"{symbol} quality warnings: {'; '.join(warnings)}")
    if passed and not warnings:
        logger.info(f"{symbol} data quality: PASSED")
    
    return {
        'valid': passed,
        'issues': issues,
        'warnings': warnings,
        'passed': passed,
        'rows': len(df),
        'columns': list(df.columns)
    }

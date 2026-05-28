"""
TradeGlob - Universal Market Data Fetcher

A competitive, production-ready library for fetching market data from
3.5+ million instruments across global exchanges via TradingView.

Features:
- Authentication support (free & paid accounts)
- Parallel fetching (5x faster)
- Smart caching system
- Comprehensive error handling
- Data quality validation
- Progress indicators
- Multi-market support
- 130+ Technical Analysis indicators

Author: TradeGlob Team
Version: 1.0.0
License: MIT
"""

from .core import TradeGlobFetcher
from .config import FetcherConfig, MarketConfig
from .utils.exceptions import (
    TradeGlobError,
    ConnectionError,
    NoDataError,
    ValidationError
)
from .markets.egx import EGX_SECTORS, list_egx_sectors, get_egx_sector_stocks

# Register DataFrame .ta accessor for technical analysis
from .ta.core import AnalysisIndicators  # noqa: F401

__version__ = "1.0.0"
__all__ = [
    'TradeGlobFetcher',
    'FetcherConfig',
    'MarketConfig',
    'TradeGlobError',
    'ConnectionError',
    'NoDataError',
    'ValidationError',
    'EGX_SECTORS',
    'list_egx_sectors',
    'get_egx_sector_stocks',
]

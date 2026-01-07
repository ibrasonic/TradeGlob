# -*- coding: utf-8 -*-
"""
Technical Analysis Module for TradeGlob

This module contains 130+ technical indicators derived from pandas-ta
by Kevin Johnson, licensed under MIT License.
See LICENSE_PANDAS_TA.txt for full attribution.
"""

version = "1.0.0"  # TradeGlob TA version

# Import maps and utils first (required by core)
from tradeglob.ta.maps import EXCHANGE_TZ, RATE, Category, Imports
from tradeglob.ta.utils import *
from tradeglob.ta.utils import __all__ as utils_all

# Flat Structure. Supports ta.ema() or ta.overlap.ema()
from tradeglob.ta.candle import *
from tradeglob.ta.cycle import *
from tradeglob.ta.momentum import *
from tradeglob.ta.overlap import *
from tradeglob.ta.performance import *
from tradeglob.ta.statistics import *
from tradeglob.ta.trend import *
from tradeglob.ta.volatility import *
from tradeglob.ta.volume import *
from tradeglob.ta.candle import __all__ as candle_all
from tradeglob.ta.cycle import __all__ as cycle_all
from tradeglob.ta.momentum import __all__ as momentum_all
from tradeglob.ta.overlap import __all__ as overlap_all
from tradeglob.ta.performance import __all__ as performance_all
from tradeglob.ta.statistics import __all__ as statistics_all
from tradeglob.ta.trend import __all__ as trend_all
from tradeglob.ta.volatility import __all__ as volatility_all
from tradeglob.ta.volume import __all__ as volume_all

# Common Averages useful for Indicators
# with a mamode argument, like ta.adx()
from tradeglob.ta.ma import ma

# Custom External Directory Commands. See help(import_dir)
from tradeglob.ta.custom import create_dir, import_dir

# Enable "ta" DataFrame Extension (import last to avoid circular imports)
from tradeglob.ta.core import AnalysisIndicators

__all__ = [
    # "name",
    "EXCHANGE_TZ",
    "RATE",
    "Category",
    "Imports",
    "version",
    "ma",
    "create_dir",
    "import_dir",
    "AnalysisIndicators",
    "AllStudy",
    "CommonStudy",
]

__all__ += [
    utils_all
    + candle_all
    + cycle_all
    + momentum_all
    + overlap_all
    + performance_all
    + statistics_all
    + trend_all
    + volatility_all
    + volume_all
]

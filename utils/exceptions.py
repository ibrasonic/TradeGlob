"""Custom exceptions for TradeGlob"""


class TradeGlobError(Exception):
    """Base exception for all TradeGlob errors"""
    pass


class ConnectionError(TradeGlobError):
    """Connection to TradingView failed"""
    pass


class NoDataError(TradeGlobError):
    """No data returned for requested symbol"""
    pass


class ValidationError(TradeGlobError):
    """Input validation failed"""
    pass


class CacheError(TradeGlobError):
    """Cache operation failed"""
    pass


class AuthenticationError(TradeGlobError):
    """TradingView authentication failed"""
    pass

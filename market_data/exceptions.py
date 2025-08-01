"""
Market Data Exceptions

Custom exceptions for the market data module.
"""


class MarketDataError(Exception):
    """Base exception for market data errors"""
    pass


class QuoteError(MarketDataError):
    """Raised when quote retrieval fails"""
    pass


class HistoricalDataError(MarketDataError):
    """Raised when historical data retrieval fails"""
    pass


class NotSupportedError(MarketDataError):
    """Raised when a feature is not supported by the provider"""
    pass


class ConnectionError(MarketDataError):
    """Raised when connection to data provider fails"""
    pass

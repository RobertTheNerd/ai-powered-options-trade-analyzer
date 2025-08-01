"""
Market Data Module

Clean, scalable interface for stock and options data providers.
Enables easy switching between different data sources (IBKR, TastyTrade, etc.)

Usage:
    from market_data import IBKRProvider, TastyTradeProvider
    
    # IBKR - supports quotes and historical data
    ibkr = IBKRProvider()
    quote = ibkr.get_quote("AAPL")
    hist_data = ibkr.get_historical_data("AAPL", "1M", "1D")
    
    # TastyTrade - quotes only
    tt = TastyTradeProvider(username="user", password="pass")
    quote = tt.get_quote("AAPL")
    # hist_data = tt.get_historical_data("AAPL")  # Raises NotSupportedError
"""

# Core interface and data models
from .interface import MarketDataProvider, Quote, HistoricalData

# Exceptions
from .exceptions import (
    MarketDataError,
    QuoteError, 
    HistoricalDataError,
    NotSupportedError,
    ConnectionError
)

# Provider implementations
from .providers import IBKRProvider, TastyTradeProvider

__all__ = [
    # Interface
    'MarketDataProvider',
    'Quote',
    'HistoricalData',
    
    # Exceptions
    'MarketDataError',
    'QuoteError',
    'HistoricalDataError', 
    'NotSupportedError',
    'ConnectionError',
    
    # Providers
    'IBKRProvider',
    'TastyTradeProvider',
]

__version__ = '1.0.0'

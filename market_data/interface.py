"""
Market Data Interface

Abstract interface for stock and options data providers.
Enables switching between different data sources (IBKR, TastyTrade, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import pandas as pd


@dataclass
class Quote:
    """Universal quote data structure"""
    symbol: str
    price: float
    bid: float
    ask: float
    volume: int
    timestamp: datetime
    
    @property
    def spread(self) -> float:
        """Bid-ask spread"""
        return self.ask - self.bid if self.ask and self.bid else 0.0
    
    @property
    def mid_price(self) -> float:
        """Mid-point between bid and ask"""
        return (self.bid + self.ask) / 2 if self.ask and self.bid else self.price


@dataclass
class HistoricalData:
    """Universal historical data structure"""
    symbol: str
    data: pd.DataFrame  # Columns: open, high, low, close, volume
    timeframe: str
    period: str
    
    @property
    def latest_price(self) -> float:
        """Get the latest closing price"""
        return float(self.data['close'].iloc[-1]) if not self.data.empty else 0.0
    
    @property
    def price_range(self) -> tuple[float, float]:
        """Get the (min, max) price range for the period"""
        if self.data.empty:
            return (0.0, 0.0)
        return (float(self.data['low'].min()), float(self.data['high'].max()))


class MarketDataProvider(ABC):
    """
    Abstract base class for market data providers
    
    This interface defines the contract that all market data providers must implement.
    Implementations handle their own connection lifecycle internally.
    """
    
    @abstractmethod
    def get_quote(self, symbol: str, **kwargs) -> Optional[Quote]:
        """
        Get real-time quote for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            **kwargs: Provider-specific parameters
            
        Returns:
            Quote object or None if failed
            
        Raises:
            QuoteError: If quote retrieval fails
        """
        pass
    
    @abstractmethod
    def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1Y", 
        timeframe: str = "1D",
        **kwargs
    ) -> Optional[HistoricalData]:
        """
        Get historical price data for a symbol
        
        Args:
            symbol: Stock symbol
            period: Time period (e.g., '1Y', '6M', '1M', '5D')
            timeframe: Bar size (e.g., '1D', '1H', '15M', '5M')
            **kwargs: Provider-specific parameters
            
        Returns:
            HistoricalData object or None if failed
            
        Raises:
            HistoricalDataError: If historical data retrieval fails
            NotSupportedError: If provider doesn't support historical data
        """
        pass

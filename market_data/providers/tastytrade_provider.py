"""
TastyTrade Market Data Provider Implementation

Implementation of MarketDataProvider interface using TastyTrade API.
Supports real-time quotes only. Historical data throws NotSupportedError.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote as TTQuote

from ..interface import MarketDataProvider, Quote, HistoricalData
from ..exceptions import QuoteError, NotSupportedError, ConnectionError


class TastyTradeProvider(MarketDataProvider):
    """
    TastyTrade implementation of MarketDataProvider interface
    
    Supports real-time quotes only.
    Historical data raises NotSupportedError.
    """
    
    def __init__(self, username: str, password: str):
        """
        Initialize TastyTrade provider
        
        Args:
            username: TastyTrade username
            password: TastyTrade password
        """
        self.username = username
        self.password = password
        self.session = None
        self._connected = False
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _ensure_connected(self):
        """Internal connection management - consumer doesn't see this"""
        if not self._connected or not self.session:
            try:
                self.session = Session(self.username, self.password)
                self._connected = True
                self.logger.info("Connected to TastyTrade")
            except Exception as e:
                self.logger.error(f"Failed to connect to TastyTrade: {e}")
                raise ConnectionError(f"TastyTrade connection failed: {e}")
    
    async def _get_quote_async(self, symbol: str) -> Optional[Quote]:
        """Async helper for getting quotes"""
        async with DXLinkStreamer(self.session) as streamer:
            await streamer.subscribe(TTQuote, [symbol])
            
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < 10:  # 10 second timeout
                try:
                    quote = await asyncio.wait_for(streamer.get_event(TTQuote), timeout=2.0)
                    
                    if quote and quote.event_symbol == symbol:
                        # Calculate mid price if both bid and ask are available
                        if quote.bid_price and quote.ask_price:
                            price = float((quote.bid_price + quote.ask_price) / 2)
                        else:
                            # Use the available price or fallback to 0
                            price = float(quote.bid_price or quote.ask_price or 0.0)
                        
                        return Quote(
                            symbol=symbol.upper(),
                            price=price,
                            bid=float(quote.bid_price) if quote.bid_price else 0.0,
                            ask=float(quote.ask_price) if quote.ask_price else 0.0,
                            volume=int(quote.bid_size + quote.ask_size) if quote.bid_size and quote.ask_size else 0,
                            timestamp=datetime.now()
                        )
                        
                except asyncio.TimeoutError:
                    continue
            
            return None
    
    def get_quote(self, symbol: str, **kwargs) -> Optional[Quote]:
        """
        Get real-time quote for a stock
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            **kwargs: Ignored for TastyTrade
            
        Returns:
            Quote object or None if failed
            
        Raises:
            QuoteError: If quote retrieval fails
        """
        self._ensure_connected()
        
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                quote = loop.run_until_complete(self._get_quote_async(symbol))
                if quote:
                    return quote
                else:
                    raise QuoteError(f"No quote data received for {symbol}")
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"Error getting quote for {symbol}: {e}")
            raise QuoteError(f"Failed to get quote for {symbol}: {e}")
    
    def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1Y", 
        timeframe: str = "1D",
        **kwargs
    ) -> Optional[HistoricalData]:
        """
        Get historical data - NOT SUPPORTED by TastyTrade
        
        Args:
            symbol: Stock symbol
            period: Time period (ignored)
            timeframe: Bar size (ignored)
            **kwargs: Ignored
            
        Returns:
            Never returns - always raises NotSupportedError
            
        Raises:
            NotSupportedError: Always - TastyTrade doesn't support historical data API
        """
        raise NotSupportedError(
            "Historical data is not supported by TastyTrade API. "
            "Use IBKR provider for historical data or access TastyTrade's web platform for backtesting."
        )

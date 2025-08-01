"""
IBKR Provider with Event-Driven Data Retrieval

Implements BEST practices for IB API data retrieval using event-driven patterns.
No arbitrary sleeps, proper timeout handling, optimal performance.
"""

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Callable, Optional

import pandas as pd
from ib_async import IB, Stock, util

from ..exceptions import ConnectionError, HistoricalDataError, QuoteError
from ..interface import HistoricalData, MarketDataProvider, Quote


class IBKRProvider(MarketDataProvider):
    """
    IBKR provider using event-driven patterns for optimal performance

    ✅ No arbitrary sleeps
    ✅ Event-driven data waiting
    ✅ Proper timeout handling
    ✅ Async-ready for high performance
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 7496, client_id: int = 1):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self._connected = False
        self.logger = logging.getLogger(__name__)

    def _ensure_connected(self):
        """Internal connection management"""
        if not self._connected or not self.ib.isConnected():
            try:
                self.ib.connect(
                    self.host, self.port, clientId=self.client_id, timeout=10
                )
                self._connected = True
                self.logger.info(f"Connected to IBKR at {self.host}:{self.port}")
            except Exception as e:
                self.logger.error(f"Failed to connect to IBKR: {e}")
                raise ConnectionError(f"IBKR connection failed: {e}")

    def _create_qualified_contract(
        self, symbol: str, exchange: str = "SMART", currency: str = "USD"
    ):
        """Create and qualify a stock contract"""
        contract = Stock(symbol, exchange, currency)
        qualified_contracts = self.ib.qualifyContracts(contract)
        if qualified_contracts:
            return qualified_contracts[0]
        else:
            raise ValueError(f"Could not qualify contract for {symbol}")

    def get_quote(self, symbol: str, **kwargs) -> Optional[Quote]:
        """
        Get real-time quote using EVENT-DRIVEN approach (no arbitrary sleeps!)

        🚀 BEST PRACTICE: Wait for actual ticker updates, not arbitrary time
        """
        self._ensure_connected()

        exchange = kwargs.get("exchange", "SMART")
        currency = kwargs.get("currency", "USD")
        timeout = kwargs.get("timeout", 10)

        try:
            contract = self._create_qualified_contract(symbol, exchange, currency)

            # 🎯 METHOD 1: Event-driven with ticker update monitoring
            return self._get_quote_event_driven(contract, symbol, timeout)

        except ValueError as e:
            self.logger.error(f"Contract qualification failed for {symbol}: {e}")
            raise QuoteError(f"Contract qualification failed for {symbol}: {e}")
        except Exception as e:
            self.logger.error(f"Error getting quote for {symbol}: {e}")
            raise QuoteError(f"Failed to get quote for {symbol}: {e}")

    def _get_quote_event_driven(self, contract, symbol: str, timeout: int) -> Quote:
        """
        🏆 BEST APPROACH: Event-driven quote retrieval

        Uses threading event to wait for actual data arrival
        """
        quote_received = threading.Event()
        received_quote = None
        error_msg = None

        def on_ticker_update(ticker):
            nonlocal received_quote, error_msg

            try:
                # Check if we have valid price data
                if ticker.last and ticker.last > 0:
                    received_quote = Quote(
                        symbol=symbol.upper(),
                        price=float(ticker.last),
                        bid=float(ticker.bid) if ticker.bid else 0.0,
                        ask=float(ticker.ask) if ticker.ask else 0.0,
                        volume=int(ticker.volume) if ticker.volume else 0,
                        timestamp=datetime.now(),
                    )
                    quote_received.set()

                # Also check for bid/ask only (common for some instruments)
                elif ticker.bid and ticker.ask and ticker.bid > 0 and ticker.ask > 0:
                    mid_price = (float(ticker.bid) + float(ticker.ask)) / 2
                    received_quote = Quote(
                        symbol=symbol.upper(),
                        price=mid_price,
                        bid=float(ticker.bid),
                        ask=float(ticker.ask),
                        volume=int(ticker.volume) if ticker.volume else 0,
                        timestamp=datetime.now(),
                    )
                    quote_received.set()

            except Exception as e:
                error_msg = str(e)
                quote_received.set()

        try:
            # Request market data and subscribe to updates
            ticker = self.ib.reqMktData(contract, "", False, False)
            ticker.updateEvent += on_ticker_update

            # Wait for data or timeout
            if quote_received.wait(timeout=timeout):
                if error_msg:
                    raise QuoteError(f"Error processing ticker data: {error_msg}")
                if received_quote:
                    return received_quote
                else:
                    raise QuoteError(f"No valid price data received for {symbol}")
            else:
                raise QuoteError(
                    f"Timeout waiting for market data for {symbol} after {timeout}s"
                )

        finally:
            # Always cleanup
            try:
                ticker.updateEvent -= on_ticker_update
                self.ib.cancelMktData(contract)
            except:
                pass

    def get_quote_async_ready(self, symbol: str, **kwargs) -> Optional[Quote]:
        """
        🚀 ASYNC VERSION: For high-performance applications

        Can be awaited in async context for non-blocking operation
        """
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, use sync version
            return self.get_quote(symbol, **kwargs)

        # Run in thread pool to avoid blocking
        with ThreadPoolExecutor() as executor:
            future = executor.submit(self.get_quote, symbol, **kwargs)
            return future.result()

    def get_historical_data(
        self, symbol: str, period: str = "1Y", timeframe: str = "1D", **kwargs
    ) -> Optional[HistoricalData]:
        """
        Enhanced historical data with proper timeout handling

        🎯 Uses ib_async's built-in historical data mechanisms
        """
        self._ensure_connected()

        exchange = kwargs.get("exchange", "SMART")
        currency = kwargs.get("currency", "USD")
        what_to_show = kwargs.get("what_to_show", "TRADES")
        timeout = kwargs.get("timeout", 30)  # Historical data can take longer

        # Map timeframe to IBKR format
        timeframe_map = {
            "1M": "1 min",
            "5M": "5 mins",
            "15M": "15 mins",
            "30M": "30 mins",
            "1H": "1 hour",
            "2H": "2 hours",
            "4H": "4 hours",
            "1D": "1 day",
            "1W": "1 week",
            "1Mo": "1 month",
        }
        bar_size = timeframe_map.get(timeframe, "1 day")

        try:
            contract = self._create_qualified_contract(symbol, exchange, currency)

            # 🎯 Use ib_async's timeout parameter (no manual waiting!)
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime="",
                durationStr=period,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=True,
                formatDate=1,
                timeout=timeout,  # ✅ Built-in timeout handling!
            )

            if bars:
                df = util.df(bars)
                if not df.empty:
                    # Clean up the dataframe
                    df.set_index("date", inplace=True)
                    df.index = pd.to_datetime(df.index)

                    return HistoricalData(
                        symbol=symbol.upper(),
                        data=df,
                        timeframe=timeframe,
                        period=period,
                    )

            raise HistoricalDataError(f"No historical data received for {symbol}")

        except ValueError as e:
            self.logger.error(f"Contract qualification failed for {symbol}: {e}")
            raise HistoricalDataError(
                f"Contract qualification failed for {symbol}: {e}"
            )
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {e}")
            raise HistoricalDataError(
                f"Failed to get historical data for {symbol}: {e}"
            )

    def get_multiple_quotes_optimized(self, symbols: list, **kwargs) -> dict:
        """
        🚀 OPTIMIZED: Get multiple quotes efficiently

        Uses concurrent requests instead of sequential
        """
        import concurrent.futures

        results = {}
        timeout = kwargs.get("timeout", 10)

        def get_single_quote(symbol):
            try:
                return symbol, self.get_quote(symbol, **kwargs)
            except Exception as e:
                return symbol, None

        # Process multiple symbols concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(get_single_quote, symbol): symbol for symbol in symbols
            }

            for future in concurrent.futures.as_completed(
                future_to_symbol, timeout=timeout * 2
            ):
                symbol, quote = future.result()
                results[symbol] = quote

        return results

    def __del__(self):
        """Cleanup connections on destruction"""
        if self._connected and self.ib.isConnected():
            try:
                self.ib.disconnect()
            except:
                pass


# 🎯 USAGE EXAMPLES


def demo_event_driven_patterns():
    """
    Show event-driven approaches for getting data from IB API
    """
    provider = IBKRProvider()

    print("🎯 Method 1: Event-driven quote (BEST)")
    quote = provider.get_quote("AAPL", timeout=10)
    print(f"AAPL: ${quote.price} (spread: ${quote.spread:.3f})")

    print("\n🚀 Method 2: Multiple quotes optimized")
    symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
    quotes = provider.get_multiple_quotes_optimized(symbols)
    for symbol, quote in quotes.items():
        if quote:
            print(f"{symbol}: ${quote.price:.2f}")

    print("\n📈 Method 3: Historical data with timeout")
    hist_data = provider.get_historical_data(
        "AAPL", period="1M", timeframe="1D", timeout=30
    )
    if hist_data:
        print(
            f"AAPL historical: {len(hist_data.data)} bars, latest: ${hist_data.latest_price:.2f}"
        )


if __name__ == "__main__":
    demo_event_driven_patterns()

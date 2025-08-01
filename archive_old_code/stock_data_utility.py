"""
IBKR Stock Data Utility

A utility-oriented wrapper for Interactive Brokers API using ib_async.
Provides clean, simple functions for common stock data operations.

Requirements:
- IBKR Trader Workstation or IB Gateway running
- ib_async library installed: pip install ib_async
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd

try:
    from ib_async import IB, Contract, Option, Stock, util
    from ib_async.contract import Contract
except ImportError:
    raise ImportError("Please install ib_async: pip install ib_async")


@dataclass
class StockQuote:
    """Simple stock quote data structure"""

    symbol: str
    price: float
    bid: float
    ask: float
    volume: int
    timestamp: datetime
    change: float = 0.0
    change_percent: float = 0.0


@dataclass
class HistoricalData:
    """Historical data structure"""

    symbol: str
    data: pd.DataFrame
    timeframe: str
    period: str


class IBKRDataUtility:
    """
    IBKR Data Utility - Clean interface for stock data operations

    Usage:
        utility = IBKRDataUtility()
        utility.connect()

        # Get current quote
        quote = utility.get_quote("AAPL")

        # Get historical data
        data = utility.get_historical_data("AAPL", period="1Y", timeframe="1D")

        utility.disconnect()
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 7496, client_id: int = 1):
        """
        Initialize IBKR utility

        Args:
            host: TWS/Gateway host (default: localhost)
            port: TWS port 7496, Gateway port 4002 (default: 7496)
            client_id: Unique client ID (default: 1)
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.connected = False

        # Setup logging
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)

    def connect(self, timeout: int = 10) -> bool:
        """
        Connect to IBKR TWS/Gateway

        Args:
            timeout: Connection timeout in seconds

        Returns:
            bool: True if connected successfully
        """
        try:
            self.ib.connect(
                self.host, self.port, clientId=self.client_id, timeout=timeout
            )
            self.connected = True
            self.logger.info(f"Connected to IBKR at {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to IBKR: {e}")
            return False

    def disconnect(self):
        """Disconnect from IBKR"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            self.logger.info("Disconnected from IBKR")

    def is_connected(self) -> bool:
        """Check if connected to IBKR"""
        return self.connected and self.ib.isConnected()

    def _ensure_connected(self):
        """Ensure we're connected, raise exception if not"""
        if not self.is_connected():
            raise ConnectionError("Not connected to IBKR. Call connect() first.")

    def _create_stock_contract(
        self, symbol: str, exchange: str = "SMART", currency: str = "USD"
    ) -> Stock:
        """Create and qualify a stock contract"""
        contract = Stock(symbol, exchange, currency)
        # Qualify the contract to populate conId
        qualified_contracts = self.ib.qualifyContracts(contract)
        if qualified_contracts:
            return qualified_contracts[0]
        else:
            raise ValueError(f"Could not qualify contract for {symbol}")

    def get_quote(
        self, symbol: str, exchange: str = "SMART", currency: str = "USD"
    ) -> Optional[StockQuote]:
        """
        Get real-time quote for a stock

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            exchange: Exchange (default: 'SMART')
            currency: Currency (default: 'USD')

        Returns:
            StockQuote object or None if failed
        """
        self._ensure_connected()

        try:
            contract = self._create_stock_contract(symbol, exchange, currency)

            # Request market data
            ticker = self.ib.reqMktData(contract, "", False, False)
            self.ib.sleep(3)  # Wait for data (increased wait time)

            if ticker.last and ticker.last > 0:
                quote = StockQuote(
                    symbol=symbol.upper(),
                    price=float(ticker.last),
                    bid=float(ticker.bid) if ticker.bid else 0.0,
                    ask=float(ticker.ask) if ticker.ask else 0.0,
                    volume=int(ticker.volume) if ticker.volume else 0,
                    timestamp=datetime.now(),
                )

                # Cancel market data to free up subscription
                self.ib.cancelMktData(contract)
                return quote
            else:
                # Cancel market data even if no data received
                self.ib.cancelMktData(contract)
                self.logger.warning(f"No market data received for {symbol}")
                return None

        except ValueError as e:
            self.logger.error(f"Contract qualification failed for {symbol}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting quote for {symbol}: {e}")
            return None

    def get_multiple_quotes(
        self, symbols: List[str], exchange: str = "SMART", currency: str = "USD"
    ) -> Dict[str, StockQuote]:
        """
        Get quotes for multiple stocks

        Args:
            symbols: List of stock symbols
            exchange: Exchange (default: 'SMART')
            currency: Currency (default: 'USD')

        Returns:
            Dictionary of {symbol: StockQuote}
        """
        self._ensure_connected()
        quotes = {}

        try:
            # Create and qualify contracts
            contracts = []
            valid_symbols = []

            for symbol in symbols:
                try:
                    contract = self._create_stock_contract(symbol, exchange, currency)
                    contracts.append(contract)
                    valid_symbols.append(symbol)
                except ValueError as e:
                    self.logger.warning(f"Skipping {symbol}: {e}")
                    continue

            if not contracts:
                self.logger.error("No valid contracts could be created")
                return quotes

            # Request market data for valid contracts
            tickers = [
                self.ib.reqMktData(contract, "", False, False) for contract in contracts
            ]

            # Wait for data
            self.ib.sleep(4)  # Slightly longer wait for multiple symbols

            for i, ticker in enumerate(tickers):
                symbol = valid_symbols[i].upper()
                if ticker.last and ticker.last > 0:
                    quotes[symbol] = StockQuote(
                        symbol=symbol,
                        price=float(ticker.last),
                        bid=float(ticker.bid) if ticker.bid else 0.0,
                        ask=float(ticker.ask) if ticker.ask else 0.0,
                        volume=int(ticker.volume) if ticker.volume else 0,
                        timestamp=datetime.now(),
                    )

                # Cancel market data
                self.ib.cancelMktData(contracts[i])

        except Exception as e:
            self.logger.error(f"Error getting multiple quotes: {e}")
            # Clean up any remaining subscriptions
            for contract in contracts:
                try:
                    self.ib.cancelMktData(contract)
                except:
                    pass

        return quotes

    def get_historical_data(
        self,
        symbol: str,
        period: str = "1Y",
        timeframe: str = "1D",
        exchange: str = "SMART",
        currency: str = "USD",
        what_to_show: str = "TRADES",
    ) -> Optional[HistoricalData]:
        """
        Get historical data for a stock

        Args:
            symbol: Stock symbol
            period: Period like '1Y', '6M', '1M', '5D'
            timeframe: Bar size like '1D', '1H', '15M', '5M', '1M'
            exchange: Exchange (default: 'SMART')
            currency: Currency (default: 'USD')
            what_to_show: Data type ('TRADES', 'BID', 'ASK', 'MIDPOINT')

        Returns:
            HistoricalData object or None if failed
        """
        self._ensure_connected()

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
            contract = self._create_stock_contract(symbol, exchange, currency)

            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime="",
                durationStr=period,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=True,
                formatDate=1,
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

            self.logger.warning(f"No historical data received for {symbol}")
            return None

        except ValueError as e:
            self.logger.error(f"Contract qualification failed for {symbol}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {e}")
            return None

    def get_account_summary(self) -> Dict[str, any]:
        """
        Get account summary information

        Returns:
            Dictionary with account information
        """
        self._ensure_connected()

        try:
            account = self.ib.managedAccounts()[0]
            summary = self.ib.accountSummary(account)

            result = {}
            for item in summary:
                result[item.tag] = {"value": item.value, "currency": item.currency}

            return result

        except Exception as e:
            self.logger.error(f"Error getting account summary: {e}")
            return {}

    def get_positions(self) -> List[Dict[str, any]]:
        """
        Get current positions

        Returns:
            List of position dictionaries
        """
        self._ensure_connected()

        try:
            positions = self.ib.positions()
            result = []

            for pos in positions:
                result.append(
                    {
                        "symbol": pos.contract.symbol,
                        "position": pos.position,
                        "avg_cost": pos.avgCost,
                        "market_value": (
                            pos.position * pos.marketPrice if pos.marketPrice else 0
                        ),
                        "unrealized_pnl": pos.unrealizedPNL,
                        "contract_type": pos.contract.secType,
                    }
                )

            return result

        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []

    def search_contracts(self, pattern: str) -> List[Dict[str, str]]:
        """
        Search for contracts matching a pattern

        Args:
            pattern: Search pattern (partial symbol)

        Returns:
            List of matching contracts
        """
        self._ensure_connected()

        try:
            contracts = self.ib.reqMatchingSymbols(pattern)
            result = []

            for contract_desc in contracts:
                contract = contract_desc.contract
                result.append(
                    {
                        "symbol": contract.symbol,
                        "name": contract_desc.derivativeSecTypes,
                        "exchange": contract.exchange,
                        "currency": contract.currency,
                        "sec_type": contract.secType,
                    }
                )

            return result

        except Exception as e:
            self.logger.error(f"Error searching contracts: {e}")
            return []

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Convenience functions for quick operations
def get_stock_price(
    symbol: str, host: str = "127.0.0.1", port: int = 7497
) -> Optional[float]:
    """
    Quick function to get a single stock price

    Args:
        symbol: Stock symbol
        host: IBKR host
        port: IBKR port

    Returns:
        Current stock price or None
    """
    with IBKRDataUtility(host, port) as utility:
        quote = utility.get_quote(symbol)
        return quote.price if quote else None


def get_stock_data(
    symbol: str,
    period: str = "1Y",
    timeframe: str = "1D",
    host: str = "127.0.0.1",
    port: int = 7497,
) -> Optional[pd.DataFrame]:
    """
    Quick function to get historical stock data

    Args:
        symbol: Stock symbol
        period: Time period
        timeframe: Bar size
        host: IBKR host
        port: IBKR port

    Returns:
        DataFrame with historical data or None
    """
    with IBKRDataUtility(host, port) as utility:
        hist_data = utility.get_historical_data(symbol, period, timeframe)
        return hist_data.data if hist_data else None


if __name__ == "__main__":
    # Example usage
    print("IBKR Stock Data Utility Example")
    print("=" * 40)

    # Method 1: Using context manager (recommended)
    with IBKRDataUtility() as utility:
        # Get single quote
        quote = utility.get_quote("AAPL")
        if quote:
            print(
                f"{quote.symbol}: ${quote.price:.2f} (Bid: ${quote.bid:.2f}, Ask: ${quote.ask:.2f})"
            )

        # Get multiple quotes
        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        quotes = utility.get_multiple_quotes(symbols)
        for symbol, quote in quotes.items():
            print(f"{symbol}: ${quote.price:.2f}")

        # Get historical data
        hist_data = utility.get_historical_data("AAPL", period="1M", timeframe="1D")
        if hist_data:
            print(f"\nHistorical data for {hist_data.symbol}:")
            print(hist_data.data.tail())

    # Method 2: Using convenience functions
    print(f"\nQuick price check - AAPL: ${get_stock_price('AAPL')}")

    data = get_stock_data("AAPL", period="5D", timeframe="1H")
    if data is not None:
        print(f"Recent hourly data shape: {data.shape}")

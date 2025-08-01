"""
Example usage of IBKR Stock Data Utility

Make sure you have:
1. IBKR Trader Workstation or IB Gateway running
2. API enabled in TWS (File -> Global Configuration -> API -> Settings)
3. Required packages installed: pip install -r requirements.txt
"""

import pandas as pd

from stock_data_utility import IBKRDataUtility, get_stock_data, get_stock_price


def main():
    print("🔌 IBKR Stock Data Utility Examples")
    print("=" * 50)

    # Example 1: Quick single price check
    print("📈 Example 1: Quick Price Check")
    price = get_stock_price("AAPL")
    if price:
        print(f"AAPL Current Price: ${price:.2f}")
    else:
        print("❌ Failed to get AAPL price")

    print("\n" + "=" * 50)

    # Example 2: Using the utility class with context manager
    print("📊 Example 2: Comprehensive Data Retrieval")

    try:
        with IBKRDataUtility() as utility:
            print("✅ Connected to IBKR!")

            # Get single quote with full details
            quote = utility.get_quote("TSLA")
            if quote:
                print(f"\n📈 {quote.symbol} Quote:")
                print(f"   Price: ${quote.price:.2f}")
                print(f"   Bid/Ask: ${quote.bid:.2f} / ${quote.ask:.2f}")
                print(f"   Volume: {quote.volume:,}")
                print(f"   Time: {quote.timestamp.strftime('%H:%M:%S')}")

            # Get multiple quotes
            symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN"]
            print(f"\n📊 Multiple Quotes:")
            quotes = utility.get_multiple_quotes(symbols)

            for symbol, quote in quotes.items():
                print(f"   {symbol:5}: ${quote.price:8.2f} | Vol: {quote.volume:>10,}")

            # Get historical data
            print(f"\n📈 Historical Data (AAPL - Last 30 Days):")
            hist_data = utility.get_historical_data("AAPL", period="1M", timeframe="1D")

            if hist_data:
                df = hist_data.data
                print(f"   Data points: {len(df)}")
                print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
                print(
                    f"   Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}"
                )

                # Show recent data
                print("\n   Recent 5 days:")
                recent = df[["open", "high", "low", "close", "volume"]].tail()
                print(recent.round(2))

                # Calculate some basic stats
                returns = df["close"].pct_change().dropna()
                print(f"\n   Statistics:")
                print(f"   Avg Daily Return: {returns.mean()*100:.2f}%")
                print(f"   Volatility: {returns.std()*100:.2f}%")
                print(f"   Max Daily Gain: {returns.max()*100:.2f}%")
                print(f"   Max Daily Loss: {returns.min()*100:.2f}%")

            # Get account info (if you have positions)
            print(f"\n💼 Account Information:")
            try:
                account_summary = utility.get_account_summary()
                if account_summary:
                    for key, value in list(account_summary.items())[
                        :5
                    ]:  # Show first 5 items
                        print(f"   {key}: {value['value']} {value['currency']}")

                positions = utility.get_positions()
                if positions:
                    print(f"\n📋 Current Positions ({len(positions)} total):")
                    for pos in positions[:5]:  # Show first 5 positions
                        print(
                            f"   {pos['symbol']:5}: {pos['position']:>8.0f} @ ${pos['avg_cost']:8.2f}"
                        )
                else:
                    print("   No positions found")

            except Exception as e:
                print(f"   Account info not available: {e}")

            # Search for contracts
            print(f"\n🔍 Contract Search (Apple related):")
            contracts = utility.search_contracts("AAPL")
            for contract in contracts[:3]:  # Show first 3 results
                print(
                    f"   {contract['symbol']} ({contract['sec_type']}) - {contract['exchange']}"
                )

    except ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("💡 Make sure IBKR TWS/Gateway is running and API is enabled")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50)

    # Example 3: Quick historical data
    print("📈 Example 3: Quick Historical Data")
    data = get_stock_data("MSFT", period="5D", timeframe="1H")
    if data is not None:
        print(f"MSFT hourly data (last 5 days): {data.shape[0]} bars")
        print("Latest prices:")
        print(data[["open", "high", "low", "close"]].tail(3).round(2))

    print("\n✅ Examples completed!")


def analyze_portfolio_stocks():
    """
    Analyze your existing portfolio stocks
    """
    print("\n🔍 Portfolio Analysis")
    print("=" * 30)

    with IBKRDataUtility() as utility:
        # Get your current positions
        positions = utility.get_positions()

        if not positions:
            print("No positions found in account")
            return

        # Analyze each position
        for pos in positions:
            if pos["contract_type"] == "STK":  # Only stocks
                symbol = pos["symbol"]
                print(f"\n📊 Analyzing {symbol}:")

                # Get current quote
                quote = utility.get_quote(symbol)
                if quote:
                    current_price = quote.price
                    avg_cost = pos["avg_cost"]
                    pnl_per_share = current_price - avg_cost
                    pnl_percent = (pnl_per_share / avg_cost) * 100

                    print(f"   Position: {pos['position']:,.0f} shares")
                    print(f"   Avg Cost: ${avg_cost:.2f}")
                    print(f"   Current: ${current_price:.2f}")
                    print(f"   P&L: ${pnl_per_share:.2f} ({pnl_percent:+.1f}%)")

                # Get recent performance
                hist_data = utility.get_historical_data(
                    symbol, period="1M", timeframe="1D"
                )
                if hist_data:
                    df = hist_data.data
                    monthly_return = ((df["close"][-1] / df["close"][0]) - 1) * 100
                    max_price = df["high"].max()
                    min_price = df["low"].min()

                    print(f"   30-day return: {monthly_return:+.1f}%")
                    print(f"   30-day range: ${min_price:.2f} - ${max_price:.2f}")


if __name__ == "__main__":
    main()

    # Uncomment to analyze your portfolio
    # analyze_portfolio_stocks()

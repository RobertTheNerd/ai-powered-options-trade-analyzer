"""
Test script for the new market data module

Demonstrates how to use both IBKR and TastyTrade providers with the unified interface.
"""

from market_data import IBKRProvider, NotSupportedError, Quote, TastyTradeProvider


def test_ibkr_provider():
    """Test IBKR provider - supports both quotes and historical data"""
    print("🔌 Testing IBKR Provider")
    print("=" * 40)

    try:
        # Create IBKR provider
        ibkr = IBKRProvider(client_id=2)

        # Test quote
        print("📈 Getting quote for AAPL...")
        quote = ibkr.get_quote("AAPL", timeout=15)

        if quote:
            print(f"✅ {quote.symbol}: ${quote.price:.2f}")
            print(f"   Bid/Ask: ${quote.bid:.2f} / ${quote.ask:.2f}")
            print(f"   Spread: ${quote.spread:.3f}")
            print(f"   Volume: {quote.volume:,}")
            print(f"   Time: {quote.timestamp.strftime('%H:%M:%S')}")

        # Test historical data
        print("\n📊 Getting historical data for AAPL...")
        hist_data = ibkr.get_historical_data("AAPL", period="5D", timeframe="1D")

        if hist_data:
            print(f"✅ Historical data: {len(hist_data.data)} bars")
            print(f"   Latest price: ${hist_data.latest_price:.2f}")
            print(
                f"   Price range: ${hist_data.price_range[0]:.2f} - ${hist_data.price_range[1]:.2f}"
            )
            print(f"   Period: {hist_data.period}, Timeframe: {hist_data.timeframe}")

    except Exception as e:
        print(f"❌ IBKR Error: {e}")


def test_tastytrade_provider():
    USERNAME = "robertwayne"
    PASSWORD = "Tastytrade168*"
    """Test TastyTrade provider - quotes only, historical data not supported"""
    print("\n🔌 Testing TastyTrade Provider")
    print("=" * 40)

    # Note: This will fail without real credentials
    print("⚠️  TastyTrade requires real credentials - this is just a demo")

    try:
        # Create TastyTrade provider (will fail without real credentials)
        tt = TastyTradeProvider(username=USERNAME, password=PASSWORD)

        # Test quote (will fail due to demo credentials)
        print("📈 Attempting to get quote for AAPL...")
        quote = tt.get_quote("AAPL")

        if quote:
            print(f"✅ {quote.symbol}: ${quote.price:.2f}")

    except Exception as e:
        print(f"❌ TastyTrade Quote Error (expected with demo credentials): {e}")

    # # Test historical data (should always fail)
    # try:
    #     tt = TastyTradeProvider(username=USERNAME, password=PASSWORD)
    #     print("\n📊 Attempting to get historical data...")
    #     hist_data = tt.get_historical_data("AAPL", period="5D", timeframe="1D")

    except NotSupportedError as e:
        print(f"❌ Expected error: {e}")
    except Exception as e:
        print(f"❌ Other error: {e}")


def demonstrate_unified_interface():
    """Show how both providers can be used interchangeably"""
    print("\n🔄 Demonstrating Unified Interface")
    print("=" * 40)

    def get_quote_with_any_provider(provider, symbol):
        """Function that works with any MarketDataProvider"""
        try:
            quote = provider.get_quote(symbol)
            if quote:
                return (
                    f"{quote.symbol}: ${quote.price:.2f} | Spread: ${quote.spread:.3f}"
                )
            else:
                return f"No quote available for {symbol}"
        except Exception as e:
            return f"Error getting {symbol}: {e}"

    # This function works with any provider!
    providers = [
        ("IBKR", IBKRProvider()),
        # ("TastyTrade", TastyTradeProvider("demo", "demo")),  # Commented out due to credentials
    ]

    for name, provider in providers:
        print(f"\n{name} Provider:")
        result = get_quote_with_any_provider(provider, "AAPL")
        print(f"   {result}")


def main():
    """Run all tests"""
    print("🧪 Market Data Module Test")
    print("=" * 50)

    # Test IBKR (works if TWS is running)
    # test_ibkr_provider()

    # Test TastyTrade (demo only)
    test_tastytrade_provider()

    # Show unified interface
    # demonstrate_unified_interface()


if __name__ == "__main__":
    main()

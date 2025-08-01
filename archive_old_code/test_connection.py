"""
Simple connection test for IBKR Stock Data Utility

Run this script to verify your IBKR connection is working properly.
Make sure TWS/Gateway is running with API enabled.
"""

import sys

from stock_data_utility import IBKRDataUtility, get_stock_price


def test_connection():
    """Test basic connection to IBKR"""
    print("🔌 Testing IBKR Connection...")
    print("=" * 40)

    try:
        # Test 1: Connection test
        print("📡 Test 1: Basic Connection")
        utility = IBKRDataUtility()

        if utility.connect():
            print("✅ Connected successfully!")

            # Test 2: Simple quote
            print("\n📈 Test 2: Stock Quote")
            quote = utility.get_quote("AAPL")

            if quote:
                print(f"✅ AAPL Quote: ${quote.price:.2f}")
                print(f"   Bid/Ask: ${quote.bid:.2f} / ${quote.ask:.2f}")
                print(f"   Volume: {quote.volume:,}")
            else:
                print("❌ Failed to get quote (check market hours)")

            # Test 3: Historical data
            print("\n📊 Test 3: Historical Data")
            hist_data = utility.get_historical_data("AAPL", period="5D", timeframe="1D")

            if hist_data and not hist_data.data.empty:
                print(f"✅ Historical data: {len(hist_data.data)} bars")
                print(
                    f"   Date range: {hist_data.data.index[0].date()} to {hist_data.data.index[-1].date()}"
                )
            else:
                print("❌ Failed to get historical data")

            utility.disconnect()
            print("\n✅ All tests passed! Your IBKR connection is working.")

        else:
            print("❌ Failed to connect to IBKR")
            print("\n🛠 Troubleshooting:")
            print("   1. Is TWS or IB Gateway running?")
            print(
                "   2. Is API access enabled? (File → Global Configuration → API → Settings)"
            )
            print("   3. Check the port number (7497 for TWS, 4002 for Gateway)")
            print("   4. Is 127.0.0.1 in trusted IP addresses?")
            return False

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n🛠 Install required packages:")
        print("   pip install ib_async pandas")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True


def test_convenience_functions():
    """Test convenience functions"""
    print("\n🚀 Testing Convenience Functions...")
    print("=" * 40)

    try:
        # Quick price check
        print("📈 Quick price check...")
        price = get_stock_price("MSFT")

        if price:
            print(f"✅ MSFT Price: ${price:.2f}")
        else:
            print("❌ Failed to get price")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all tests"""
    print("🧪 IBKR Stock Data Utility - Connection Test")
    print("=" * 50)

    success = test_connection()

    if success:
        test_convenience_functions()
        print("\n🎉 All tests completed successfully!")
        print("\n📖 Next steps:")
        print("   - Run: python example_usage.py")
        print("   - Read: README_ibkr_utility.md")
    else:
        print("\n❌ Connection test failed. Please check your setup.")
        sys.exit(1)


if __name__ == "__main__":
    main()

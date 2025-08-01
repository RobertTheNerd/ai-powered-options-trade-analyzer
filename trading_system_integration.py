"""
Trading System Integration Example

Shows how to integrate the new market data module with your existing options trading system.
"""

from market_data import IBKRProvider, TastyTradeProvider, NotSupportedError
from datetime import datetime
import pandas as pd


def get_trading_companies_data(provider):
    """
    Get real-time data for your 9 trading companies using any provider
    
    This replaces your old TastyTrade-specific data collection
    """
    # Your 9 companies from the original trading system
    companies = ['NVDA', 'TSLA', 'AMZN', 'ISRG', 'PLTR', 'ENPH', 'XOM', 'DE', 'CAT']
    
    print(f"📊 Getting quotes for {len(companies)} companies...")
    stock_data = {}
    
    for symbol in companies:
        try:
            quote = provider.get_quote(symbol)
            if quote:
                stock_data[symbol] = {
                    'company_name': symbol,
                    'current_price': quote.price,
                    'bid_price': quote.bid,
                    'ask_price': quote.ask,
                    'spread': quote.spread,
                    'volume': quote.volume,
                    'when_checked': quote.timestamp.isoformat()
                }
                print(f"   ✅ {symbol}: ${quote.price:.2f} | Spread: ${quote.spread:.3f}")
            else:
                print(f"   ❌ {symbol}: No data")
                
        except Exception as e:
            print(f"   ❌ {symbol}: {e}")
    
    return {
        'step': 1,
        'what_we_did': 'Got current stock prices using unified interface',
        'timestamp': datetime.now().isoformat(),
        'companies_checked': len(stock_data),
        'stock_prices': stock_data
    }


def calculate_implied_volatility(provider, symbol, period="6M"):
    """
    Calculate implied volatility for Black-Scholes analysis
    
    Works only with providers that support historical data (IBKR)
    """
    try:
        print(f"📈 Calculating volatility for {symbol}...")
        
        # Get historical data for volatility calculation
        hist_data = provider.get_historical_data(symbol, period=period, timeframe="1D")
        
        if hist_data and not hist_data.data.empty:
            # Calculate daily returns
            returns = hist_data.data['close'].pct_change().dropna()
            
            # Annualized volatility (252 trading days)
            volatility = returns.std() * (252 ** 0.5)
            
            return {
                'symbol': symbol,
                'period': period,
                'volatility': volatility,
                'current_price': hist_data.latest_price,
                'price_range': hist_data.price_range,
                'data_points': len(hist_data.data)
            }
        else:
            print(f"   ❌ No historical data for {symbol}")
            return None
            
    except NotSupportedError:
        print(f"   ⚠️  Provider doesn't support historical data for {symbol}")
        return None
    except Exception as e:
        print(f"   ❌ Error calculating volatility for {symbol}: {e}")
        return None


def run_options_analysis_workflow():
    """
    Example workflow that could replace your existing TastyTrade-specific code
    """
    print("🤖 Options Trading Analysis Workflow")
    print("=" * 50)
    
    # Choose your provider
    print("🔌 Initializing data provider...")
    
    # Option 1: Use IBKR for full functionality
    provider = IBKRProvider()
    provider_name = "IBKR"
    
    # Option 2: Use TastyTrade for quotes only (uncomment to switch)
    # provider = TastyTradeProvider(username="your_username", password="your_password")
    # provider_name = "TastyTrade"
    
    print(f"   Using {provider_name} provider")
    
    try:
        # Step 1: Get stock prices (works with any provider)
        print(f"\n📊 Step 1: Stock Price Collection")
        stock_data = get_trading_companies_data(provider)
        
        print(f"\n✅ Collected data for {stock_data['companies_checked']} companies")
        
        # Step 2: Volatility analysis (IBKR only)
        print(f"\n📈 Step 2: Volatility Analysis")
        
        volatility_data = {}
        sample_symbols = ['NVDA', 'TSLA', 'AAPL']  # Test with a few symbols
        
        for symbol in sample_symbols:
            vol_result = calculate_implied_volatility(provider, symbol)
            if vol_result:
                volatility_data[symbol] = vol_result
                print(f"   ✅ {symbol}: {vol_result['volatility']:.2%} volatility")
        
        # Step 3: Integration with your Black-Scholes analysis
        print(f"\n🧮 Step 3: Ready for Black-Scholes Analysis")
        print("   Stock prices ✅")
        print("   Volatility data ✅" if volatility_data else "   Volatility data ❌ (use IBKR for historical data)")
        print("   Ready to find credit spread opportunities!")
        
        return {
            'stock_data': stock_data,
            'volatility_data': volatility_data,
            'provider': provider_name
        }
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return None


def main():
    """
    Main function showing how to integrate with your trading system
    """
    print("🎯 Trading System Integration Example")
    print("=" * 60)
    
    # Run the workflow
    results = run_options_analysis_workflow()
    
    if results:
        print(f"\n🎉 Analysis completed successfully!")
        print(f"   Provider: {results['provider']}")
        print(f"   Stock data points: {len(results['stock_data']['stock_prices'])}")
        print(f"   Volatility calculations: {len(results['volatility_data'])}")
        
        print(f"\n�� Next steps:")
        print(f"   1. Use stock_data for current prices")
        print(f"   2. Use volatility_data for Black-Scholes calculations")
        print(f"   3. Find credit spread opportunities")
        print(f"   4. Execute trades through your existing system")
    
    print(f"\n🔄 Provider Switching:")
    print(f"   To switch from TastyTrade to IBKR:")
    print(f"   - Change: provider = IBKRProvider()")
    print(f"   - Your code stays exactly the same!")
    
    print(f"\n📁 Integration with existing files:")
    print(f"   - Replace TastyTrade calls in your scripts")
    print(f"   - Use: from market_data import IBKRProvider")
    print(f"   - Keep your Black-Scholes analysis unchanged")


if __name__ == "__main__":
    main()

# 📈 IBKR Stock Data Utility

A clean, utility-oriented wrapper for Interactive Brokers API using [ib_async](https://github.com/ib-api-reloaded/ib_async). This library provides simple, intuitive functions for retrieving stock data, account information, and managing IBKR connections.

## 🚀 Features

- **Simple API**: Clean, utility-oriented functions for common tasks
- **Real-time Data**: Get live quotes, bid/ask spreads, and volume
- **Historical Data**: Retrieve OHLCV data with flexible timeframes
- **Account Management**: Access positions, account summary, and P&L
- **Context Manager**: Automatic connection handling
- **Error Handling**: Robust error handling with informative logging
- **Type Hints**: Full type annotations for better IDE support

## 📋 Prerequisites

1. **IBKR Account**: Active Interactive Brokers account
2. **TWS/Gateway**: IBKR Trader Workstation or IB Gateway running
3. **API Access**: API enabled in TWS (File → Global Configuration → API → Settings)
4. **Python**: Python 3.8+ required

## 🛠 Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Or install manually:**
```bash
pip install ib_async pandas numpy
```

## ⚙️ Setup

1. **Start IBKR TWS or IB Gateway**
2. **Enable API access:**
   - In TWS: File → Global Configuration → API → Settings
   - Check "Enable ActiveX and Socket Clients"
   - Note the Socket Port (default: 7497 for TWS, 4002 for Gateway)
3. **Set trusted IP addresses** (127.0.0.1 for localhost)

## 🎯 Quick Start

### Basic Usage

```python
from stock_data_utility import IBKRDataUtility, get_stock_price

# Quick price check
price = get_stock_price("AAPL")
print(f"AAPL: ${price:.2f}")

# Using the utility class
with IBKRDataUtility() as utility:
    # Get detailed quote
    quote = utility.get_quote("TSLA")
    print(f"{quote.symbol}: ${quote.price:.2f}")
    
    # Get historical data
    data = utility.get_historical_data("AAPL", period="1M", timeframe="1D")
    print(data.data.tail())
```

### Advanced Examples

```python
from stock_data_utility import IBKRDataUtility

with IBKRDataUtility() as utility:
    # Multiple quotes at once
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    quotes = utility.get_multiple_quotes(symbols)
    
    for symbol, quote in quotes.items():
        spread = quote.ask - quote.bid
        print(f"{symbol}: ${quote.price:.2f} (Spread: ${spread:.3f})")
    
    # Different timeframes
    daily_data = utility.get_historical_data("NVDA", "1Y", "1D")
    hourly_data = utility.get_historical_data("NVDA", "5D", "1H")
    minute_data = utility.get_historical_data("NVDA", "1D", "5M")
    
    # Account information
    account = utility.get_account_summary()
    positions = utility.get_positions()
    
    print(f"Account value: {account.get('NetLiquidation', {}).get('value', 'N/A')}")
    print(f"Positions: {len(positions)}")
```

## 📊 API Reference

### IBKRDataUtility Class

#### Connection Methods
```python
utility = IBKRDataUtility(host='127.0.0.1', port=7497, client_id=1)
utility.connect(timeout=10)  # Returns bool
utility.disconnect()
utility.is_connected()  # Returns bool
```

#### Market Data Methods
```python
# Single quote
quote = utility.get_quote(symbol, exchange='SMART', currency='USD')
# Returns: StockQuote object

# Multiple quotes
quotes = utility.get_multiple_quotes(symbols, exchange='SMART', currency='USD')
# Returns: Dict[str, StockQuote]

# Historical data
data = utility.get_historical_data(
    symbol, 
    period='1Y',      # '1Y', '6M', '1M', '5D', etc.
    timeframe='1D',   # '1M', '5M', '15M', '1H', '1D', '1W'
    exchange='SMART',
    currency='USD',
    what_to_show='TRADES'  # 'TRADES', 'BID', 'ASK', 'MIDPOINT'
)
# Returns: HistoricalData object
```

#### Account Methods
```python
# Account summary
summary = utility.get_account_summary()
# Returns: Dict[str, any]

# Current positions
positions = utility.get_positions()
# Returns: List[Dict[str, any]]

# Search contracts
contracts = utility.search_contracts(pattern)
# Returns: List[Dict[str, str]]
```

### Data Structures

#### StockQuote
```python
@dataclass
class StockQuote:
    symbol: str
    price: float
    bid: float
    ask: float
    volume: int
    timestamp: datetime
    change: float = 0.0
    change_percent: float = 0.0
```

#### HistoricalData
```python
@dataclass
class HistoricalData:
    symbol: str
    data: pd.DataFrame  # Columns: open, high, low, close, volume
    timeframe: str
    period: str
```

### Convenience Functions

```python
# Quick functions for simple operations
price = get_stock_price(symbol, host='127.0.0.1', port=7497)
data = get_stock_data(symbol, period='1Y', timeframe='1D', host='127.0.0.1', port=7497)
```

## 🔧 Configuration

### Connection Settings

```python
# TWS (Trader Workstation)
utility = IBKRDataUtility(host='127.0.0.1', port=7497, client_id=1)

# IB Gateway
utility = IBKRDataUtility(host='127.0.0.1', port=4002, client_id=1)

# Remote connection
utility = IBKRDataUtility(host='192.168.1.100', port=7497, client_id=1)
```

### Timeframe Options

| Period | Description | Timeframe | Description |
|--------|-------------|-----------|-------------|
| `1D` | 1 day | `1M` | 1 minute |
| `5D` | 5 days | `5M` | 5 minutes |
| `1W` | 1 week | `15M` | 15 minutes |
| `1M` | 1 month | `30M` | 30 minutes |
| `3M` | 3 months | `1H` | 1 hour |
| `6M` | 6 months | `2H` | 2 hours |
| `1Y` | 1 year | `4H` | 4 hours |
| `2Y` | 2 years | `1D` | 1 day |

## 🔍 Examples

### Portfolio Analysis
```python
def analyze_portfolio():
    with IBKRDataUtility() as utility:
        positions = utility.get_positions()
        
        for pos in positions:
            if pos['contract_type'] == 'STK':
                symbol = pos['symbol']
                quote = utility.get_quote(symbol)
                
                if quote:
                    pnl = (quote.price - pos['avg_cost']) * pos['position']
                    pnl_pct = ((quote.price / pos['avg_cost']) - 1) * 100
                    
                    print(f"{symbol}: ${quote.price:.2f} | P&L: ${pnl:,.0f} ({pnl_pct:+.1f}%)")
```

### Market Scanner
```python
def scan_market(symbols):
    with IBKRDataUtility() as utility:
        quotes = utility.get_multiple_quotes(symbols)
        
        # Sort by volume
        sorted_quotes = sorted(quotes.items(), 
                             key=lambda x: x[1].volume, reverse=True)
        
        print("Top stocks by volume:")
        for symbol, quote in sorted_quotes[:10]:
            spread_pct = ((quote.ask - quote.bid) / quote.price) * 100
            print(f"{symbol:5}: ${quote.price:8.2f} | Vol: {quote.volume:>10,} | Spread: {spread_pct:.3f}%")
```

### Technical Analysis
```python
def technical_analysis(symbol):
    with IBKRDataUtility() as utility:
        # Get daily data for moving averages
        data = utility.get_historical_data(symbol, "6M", "1D")
        
        if data:
            df = data.data
            
            # Calculate moving averages
            df['MA20'] = df['close'].rolling(20).mean()
            df['MA50'] = df['close'].rolling(50).mean()
            
            # Current values
            current = df.iloc[-1]
            print(f"{symbol} Technical Analysis:")
            print(f"Price: ${current['close']:.2f}")
            print(f"20-day MA: ${current['MA20']:.2f}")
            print(f"50-day MA: ${current['MA50']:.2f}")
            
            # Trend analysis
            if current['close'] > current['MA20'] > current['MA50']:
                print("Trend: Bullish")
            elif current['close'] < current['MA20'] < current['MA50']:
                print("Trend: Bearish")
            else:
                print("Trend: Mixed")
```

## ⚠️ Error Handling

The utility includes comprehensive error handling:

```python
try:
    with IBKRDataUtility() as utility:
        quote = utility.get_quote("INVALID_SYMBOL")
        if quote is None:
            print("Symbol not found or no data available")
            
except ConnectionError:
    print("Failed to connect to IBKR. Is TWS/Gateway running?")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure TWS/Gateway is running
   - Check API is enabled in settings
   - Verify port number (7497 for TWS, 4002 for Gateway)

2. **No Market Data**
   - Check if you have market data subscriptions
   - Verify symbol format (use US symbols like "AAPL", not "AAPL.US")
   - Some data may require exchange specification

3. **API Limits**
   - IBKR has rate limits on API calls
   - Historical data requests are limited
   - Use appropriate delays between requests

4. **Paper Trading**
   - Paper trading account: port 7497
   - Live trading account: port 7496 (be careful!)

### Logging

Enable detailed logging for debugging:

```python
import logging
logging.basicConfig(level=logging.INFO)

with IBKRDataUtility() as utility:
    # Detailed logs will show connection status and errors
    quote = utility.get_quote("AAPL")
```

## 📜 License

This project uses the BSD-2-Clause license. See the original [ib_async](https://github.com/ib-api-reloaded/ib_async) project for full license details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📞 Support

- **IBKR API Documentation**: [Official IBKR API Docs](https://interactivebrokers.github.io/tws-api/)
- **ib_async Library**: [GitHub Repository](https://github.com/ib-api-reloaded/ib_async)

## ⚠️ Disclaimer

This software is provided for educational purposes. Use at your own risk. Not affiliated with Interactive Brokers Group, Inc.
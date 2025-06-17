import yfinance as yf
import time

# Test with just a few stocks
test_stocks = [
    ("BBCA.JK", "Bank Central Asia"),
    ("BBRI.JK", "Bank Rakyat Indonesia"),
    ("TLKM.JK", "Telkom Indonesia")
]

print("Testing stock data scraping...")
print("-" * 50)

for symbol, name in test_stocks:
    try:
        print(f"\nTesting {symbol} ({name})...")
        ticker = yf.Ticker(symbol)
        
        # Try to get fast_info first
        try:
            fast_info = ticker.fast_info
            print(f"  Last Price: {fast_info.get('lastPrice', 'N/A')}")
            print(f"  Previous Close: {fast_info.get('previousClose', 'N/A')}")
            print(f"  Volume: {fast_info.get('volume', 'N/A')}")
        except:
            print("  fast_info not available")
        
        # Try regular info
        info = ticker.info
        print(f"  Info keys available: {len(info.keys())}")
        print(f"  Current Price (info): {info.get('currentPrice', 'N/A')}")
        print(f"  Market Cap: {info.get('marketCap', 'N/A')}")
        
        # Try downloading historical data
        hist = ticker.history(period="1d")
        if not hist.empty:
            latest = hist.iloc[-1]
            print(f"  Historical Close: {latest['Close']}")
            print(f"  Historical Volume: {latest['Volume']}")
        
        time.sleep(1)  # Small delay between requests
        
    except Exception as e:
        print(f"  ERROR: {str(e)}")

print("\n" + "-" * 50)
print("Test complete!")
#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Let's check what actual current prices should be from a different source
def check_real_prices():
    print("=== DEBUGGING STOCK DATA DATES ===")
    print(f"Current time: {datetime.now()}")
    print()
    
    # Test a few Indonesian stocks using different methods
    test_symbols = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]
    
    for symbol in test_symbols:
        print(f"\n--- Checking {symbol} ---")
        
        # Method 1: Direct Yahoo Finance API
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('chart', {}).get('result', [{}])[0]
                meta = result.get('meta', {})
                
                print(f"  Yahoo Direct API:")
                print(f"    Regular Market Price: {meta.get('regularMarketPrice', 'N/A')}")
                print(f"    Regular Market Time: {meta.get('regularMarketTime', 'N/A')}")
                if meta.get('regularMarketTime'):
                    timestamp = meta.get('regularMarketTime')
                    date = datetime.fromtimestamp(timestamp)
                    print(f"    Date: {date}")
                print(f"    Previous Close: {meta.get('previousClose', 'N/A')}")
                print(f"    Currency: {meta.get('currency', 'N/A')}")
                print(f"    Exchange: {meta.get('exchangeName', 'N/A')}")
                print(f"    Market State: {meta.get('marketState', 'N/A')}")
            else:
                print(f"  Yahoo Direct API failed: {response.status_code}")
        except Exception as e:
            print(f"  Yahoo Direct API error: {e}")
            
        # Method 2: Let's also check what yfinance gives us
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            print(f"  YFinance info:")
            print(f"    Current Price: {info.get('currentPrice', 'N/A')}")
            print(f"    Regular Market Price: {info.get('regularMarketPrice', 'N/A')}")
            print(f"    Previous Close: {info.get('previousClose', 'N/A')}")
            print(f"    Regular Market Time: {info.get('regularMarketTime', 'N/A')}")
            
            # Check history
            hist = ticker.history(period="1d")
            if not hist.empty:
                latest = hist.iloc[-1]
                print(f"    Latest History Date: {hist.index[-1]}")
                print(f"    Latest History Close: {latest['Close']}")
                print(f"    Latest History Volume: {latest['Volume']}")
            
            # Check 1-minute data
            try:
                hist_1m = ticker.history(period="1d", interval="1m")
                if not hist_1m.empty:
                    latest_1m = hist_1m.iloc[-1]
                    print(f"    Latest 1m Date: {hist_1m.index[-1]}")
                    print(f"    Latest 1m Close: {latest_1m['Close']}")
            except:
                print(f"    1-minute data not available")
                
        except ImportError:
            print(f"  YFinance not available")
        except Exception as e:
            print(f"  YFinance error: {e}")

if __name__ == "__main__":
    check_real_prices()
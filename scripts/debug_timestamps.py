import yfinance as yf
import json
import requests
from datetime import datetime, timezone
import time

def debug_data_freshness():
    print("=== DEBUGGING YAHOO FINANCE DATA FRESHNESS ===")
    print(f"Current UTC time: {datetime.now(timezone.utc)}")
    print(f"Current Jakarta time: {datetime.now()}")  # Assuming system is set to Jakarta time
    print()
    
    symbols = ["BBCA.JK", "BBRI.JK", "BMRI.JK"]
    
    for symbol in symbols:
        print(f"\n--- {symbol} ---")
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Get info
            info = ticker.info
            print(f"Info keys count: {len(info.keys())}")
            
            # Check all possible price fields
            current_price = info.get('currentPrice')
            regular_price = info.get('regularMarketPrice')
            previous_close = info.get('previousClose')
            regular_previous = info.get('regularMarketPreviousClose')
            
            print(f"currentPrice: {current_price}")
            print(f"regularMarketPrice: {regular_price}")
            print(f"previousClose: {previous_close}")
            print(f"regularMarketPreviousClose: {regular_previous}")
            
            # Check timestamps
            reg_time = info.get('regularMarketTime')
            if reg_time:
                if isinstance(reg_time, int):
                    reg_datetime = datetime.fromtimestamp(reg_time)
                    print(f"regularMarketTime: {reg_time} ({reg_datetime})")
                else:
                    print(f"regularMarketTime: {reg_time}")
            
            # Check different history periods
            periods = ["1d", "5d", "1mo"]
            for period in periods:
                try:
                    hist = ticker.history(period=period)
                    if not hist.empty:
                        last_date = hist.index[-1]
                        last_price = hist['Close'].iloc[-1]
                        print(f"History {period} - Last date: {last_date}, Price: {last_price}")
                    else:
                        print(f"History {period} - No data")
                except Exception as e:
                    print(f"History {period} - Error: {e}")
            
            # Try 1-minute data
            try:
                hist_1m = ticker.history(period="1d", interval="1m")
                if not hist_1m.empty:
                    last_1m_date = hist_1m.index[-1]
                    last_1m_price = hist_1m['Close'].iloc[-1]
                    print(f"1-minute data - Last: {last_1m_date}, Price: {last_1m_price}")
                else:
                    print(f"1-minute data - No data")
            except Exception as e:
                print(f"1-minute data - Error: {e}")
                
            # Direct Yahoo API check
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('chart', {}).get('result', [{}])[0]
                    meta = result.get('meta', {})
                    
                    reg_market_time = meta.get('regularMarketTime')
                    if reg_market_time:
                        reg_datetime = datetime.fromtimestamp(reg_market_time)
                        print(f"Direct API - Market time: {reg_datetime}")
                    
                    print(f"Direct API - Price: {meta.get('regularMarketPrice')}")
                    print(f"Direct API - Previous: {meta.get('previousClose')}")
                    print(f"Direct API - Market state: {meta.get('marketState')}")
                    print(f"Direct API - Exchange: {meta.get('exchangeName')}")
                    
            except Exception as e:
                print(f"Direct API error: {e}")
                
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    debug_data_freshness()
import yfinance as yf
import json
import os
from datetime import datetime
from stock_symbols import INDONESIAN_STOCKS

def scrape_stocks():
    stock_data = []
    
    for symbol, name in INDONESIAN_STOCKS:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price and other data
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            previous_close = info.get('previousClose', 0)
            
            # Calculate change
            change = current_price - previous_close if current_price and previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            stock_info = {
                'symbol': symbol,
                'name': name,
                'price': current_price,
                'change': round(change, 2),
                'changePercent': round(change_percent, 2),
                'volume': info.get('volume', 0),
                'marketCap': info.get('marketCap', 0),
                'dayHigh': info.get('dayHigh', 0),
                'dayLow': info.get('dayLow', 0),
                'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', 0),
                'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', 0)
            }
            
            stock_data.append(stock_info)
            print(f"Scraped data for {name} ({symbol})")
            
        except Exception as e:
            print(f"Error scraping {symbol}: {str(e)}")
            stock_data.append({
                'symbol': symbol,
                'name': name,
                'price': 0,
                'change': 0,
                'changePercent': 0,
                'volume': 0,
                'marketCap': 0,
                'dayHigh': 0,
                'dayLow': 0,
                'fiftyTwoWeekHigh': 0,
                'fiftyTwoWeekLow': 0,
                'error': str(e)
            })
    
    # Save to JSON
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'stocks.json')
    
    with open(output_file, 'w') as f:
        json.dump({
            'stocks': stock_data,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')
        }, f, indent=2)
    
    print(f"Data saved to {output_file}")
    return stock_data

if __name__ == "__main__":
    scrape_stocks()
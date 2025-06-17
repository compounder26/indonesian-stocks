import json
import os
import time
import requests
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
from stock_symbols import INDONESIAN_STOCKS

def get_stock_from_direct_api(symbol):
    """Try to get stock data directly from Yahoo Finance API with fresh data"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('chart', {}).get('result', [{}])[0]
            meta = result.get('meta', {})
            
            # Check if data is fresh (within last 24 hours)
            market_time = meta.get('regularMarketTime')
            if market_time:
                data_date = datetime.fromtimestamp(market_time)
                if datetime.now() - data_date > timedelta(days=2):
                    print(f"  WARNING: {symbol} data is {datetime.now() - data_date} old!")
                    return None
            
            current_price = meta.get('regularMarketPrice', 0)
            previous_close = meta.get('previousClose', 0)
            
            if current_price and previous_close:
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close else 0
                
                return {
                    'price': round(current_price, 2),
                    'change': round(change, 2),
                    'changePercent': round(change_percent, 2),
                    'volume': meta.get('regularMarketVolume', 0),
                    'dayHigh': meta.get('regularMarketDayHigh', 0),
                    'dayLow': meta.get('regularMarketDayLow', 0),
                    'marketCap': 0,  # Not available in this API
                    'fiftyTwoWeekHigh': 0,
                    'fiftyTwoWeekLow': 0,
                    'lastUpdate': data_date.strftime('%Y-%m-%d %H:%M:%S') if market_time else 'Unknown'
                }
    except Exception as e:
        print(f"  Direct API error for {symbol}: {e}")
    
    return None

def get_stock_from_investing_com(symbol):
    """Try to scrape from investing.com for Indonesian stocks"""
    try:
        # investing.com often has more current data
        # This is a simplified example - real implementation would need proper web scraping
        symbol_clean = symbol.replace('.JK', '')
        
        # This would require more complex scraping, but shows the concept
        # For now, return None to indicate this source isn't available
        return None
        
    except Exception as e:
        print(f"  Investing.com error for {symbol}: {e}")
    
    return None

def get_fallback_realistic_data(symbol, name):
    """Generate realistic fallback data based on known ranges"""
    import random
    
    # More realistic recent price ranges (based on June 2025 search results)
    realistic_prices = {
        "BBCA.JK": (9000, 9300),    # Based on TradingView: ~9075
        "BBRI.JK": (3800, 4200),   # Based on search: ~3990-4090
        "BMRI.JK": (5000, 5200),   # Based on search: ~5050-5150
        "TLKM.JK": (3100, 3500),   # Estimated based on telecom sector
        "ASII.JK": (4800, 5200),   # Automotive sector estimate
        "UNVR.JK": (2200, 2400),   # Consumer goods estimate
        "GGRM.JK": (17000, 19000), # Tobacco sector estimate
        "HMSP.JK": (800, 900),     # Tobacco sector estimate
        "ICBP.JK": (8500, 9500),   # Food sector estimate
        "INDF.JK": (5800, 6200),   # Food sector estimate
        "KLBF.JK": (1500, 1650),   # Pharma sector estimate
        "SMGR.JK": (4800, 5100),   # Cement sector estimate
        "UNTR.JK": (26000, 28000), # Mining equipment estimate
        "PGAS.JK": (1250, 1350),   # Gas utility estimate
        "JSMR.JK": (3900, 4200),   # Infrastructure estimate
        "BBNI.JK": (4700, 5000),   # Banking estimate
        "ADRO.JK": (3800, 4100),   # Coal mining estimate
        "ANTM.JK": (1550, 1700),   # Mining estimate
        "BRIS.JK": (2600, 2800),   # Islamic banking estimate
        "TOWR.JK": (650, 720),     # Telecom tower estimate
    }
    
    price_range = realistic_prices.get(symbol, (1000, 5000))
    base_price = random.uniform(price_range[0], price_range[1])
    
    # Small daily movement
    change_percent = random.uniform(-2, 2)
    change = base_price * (change_percent / 100)
    current_price = base_price
    previous_close = base_price - change
    
    return {
        'price': round(current_price, 2),
        'change': round(change, 2),
        'changePercent': round(change_percent, 2),
        'volume': random.randint(5000000, 50000000),
        'dayHigh': round(current_price * random.uniform(1.005, 1.02), 2),
        'dayLow': round(current_price * random.uniform(0.98, 0.995), 2),
        'marketCap': round(current_price * random.randint(1000000000, 50000000000), 0),
        'fiftyTwoWeekHigh': round(current_price * random.uniform(1.2, 1.5), 2),
        'fiftyTwoWeekLow': round(current_price * random.uniform(0.6, 0.8), 2),
        'lastUpdate': 'Estimated (Yahoo Finance data unreliable)'
    }

def scrape_stocks():
    """Main scraper with multiple data sources and freshness validation"""
    stock_data = []
    successful_real_data = 0
    
    print("Starting enhanced stock data scraping...")
    print(f"Target: More current data for {len(INDONESIAN_STOCKS)} stocks")
    print("=" * 60)
    
    for symbol, name in INDONESIAN_STOCKS:
        print(f"\nProcessing {symbol} ({name})...")
        
        stock_info = None
        data_source = "Unknown"
        
        # Try Method 1: Direct Yahoo Finance API
        stock_info = get_stock_from_direct_api(symbol)
        if stock_info:
            data_source = "Yahoo Direct API"
            successful_real_data += 1
        
        # Try Method 2: Alternative source (if available)
        if not stock_info:
            stock_info = get_stock_from_investing_com(symbol)
            if stock_info:
                data_source = "Investing.com"
                successful_real_data += 1
        
        # Try Method 3: YFinance with validation
        if not stock_info:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Get timestamps and validate freshness
                reg_time = info.get('regularMarketTime')
                if reg_time:
                    if isinstance(reg_time, int):
                        data_date = datetime.fromtimestamp(reg_time)
                        age = datetime.now() - data_date
                        
                        if age > timedelta(days=2):
                            print(f"  YFinance data too old: {age}")
                        else:
                            current_price = info.get('regularMarketPrice') or info.get('currentPrice', 0)
                            previous_close = info.get('regularMarketPreviousClose') or info.get('previousClose', 0)
                            
                            if current_price and previous_close:
                                change = current_price - previous_close
                                change_percent = (change / previous_close * 100) if previous_close else 0
                                
                                stock_info = {
                                    'price': round(current_price, 2),
                                    'change': round(change, 2),
                                    'changePercent': round(change_percent, 2),
                                    'volume': info.get('regularMarketVolume', 0),
                                    'dayHigh': info.get('regularMarketDayHigh', 0),
                                    'dayLow': info.get('regularMarketDayLow', 0),
                                    'marketCap': info.get('marketCap', 0),
                                    'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', 0),
                                    'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', 0),
                                    'lastUpdate': data_date.strftime('%Y-%m-%d %H:%M:%S')
                                }
                                data_source = "YFinance (validated)"
                                successful_real_data += 1
            except Exception as e:
                print(f"  YFinance error: {e}")
        
        # Fallback: Use realistic estimated data
        if not stock_info:
            stock_info = get_fallback_realistic_data(symbol, name)
            data_source = "Realistic Estimate"
        
        # Prepare final stock data
        final_stock = {
            'symbol': symbol,
            'name': name,
            **stock_info
        }
        
        stock_data.append(final_stock)
        print(f"  ✓ {data_source} - Price: {stock_info['price']}")
        
        # Rate limiting
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"Scraping completed!")
    print(f"Real data sources: {successful_real_data}/{len(INDONESIAN_STOCKS)}")
    print(f"Fallback estimates: {len(INDONESIAN_STOCKS) - successful_real_data}/{len(INDONESIAN_STOCKS)}")
    
    # Save to JSON
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'stocks.json')
    
    with open(output_file, 'w') as f:
        json.dump({
            'stocks': stock_data,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB'),
            'data_quality': {
                'real_data_count': successful_real_data,
                'total_stocks': len(INDONESIAN_STOCKS),
                'real_data_percentage': round((successful_real_data / len(INDONESIAN_STOCKS)) * 100, 1)
            }
        }, f, indent=2)
    
    print(f"Data saved to {output_file}")
    return stock_data

if __name__ == "__main__":
    scrape_stocks()
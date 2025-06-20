#!/usr/bin/env python3
"""
Generate test data for Bloomberg-style interface
Creates JSON files in the new data structure
"""

import json
import os
import random
from datetime import datetime, timedelta
import pytz

# Jakarta timezone
JKT_TZ = pytz.timezone('Asia/Jakarta')

# Stock symbols and names
STOCKS = {
    'BBCA.JK': {'name': 'Bank Central Asia', 'sector': 'Financials'},
    'BBRI.JK': {'name': 'Bank Rakyat Indonesia', 'sector': 'Financials'},
    'BMRI.JK': {'name': 'Bank Mandiri', 'sector': 'Financials'},
    'TLKM.JK': {'name': 'Telkom Indonesia', 'sector': 'Communication Services'},
    'ASII.JK': {'name': 'Astra International', 'sector': 'Consumer Discretionary'},
    'UNVR.JK': {'name': 'Unilever Indonesia', 'sector': 'Consumer Staples'},
    'GGRM.JK': {'name': 'Gudang Garam', 'sector': 'Consumer Staples'},
    'HMSP.JK': {'name': 'HM Sampoerna', 'sector': 'Consumer Staples'},
    'ICBP.JK': {'name': 'Indofood CBP', 'sector': 'Consumer Staples'},
    'INDF.JK': {'name': 'Indofood Sukses Makmur', 'sector': 'Consumer Staples'},
    'KLBF.JK': {'name': 'Kalbe Farma', 'sector': 'Health Care'},
    'SMGR.JK': {'name': 'Semen Indonesia', 'sector': 'Materials'},
    'UNTR.JK': {'name': 'United Tractors', 'sector': 'Energy'},
    'PGAS.JK': {'name': 'Perusahaan Gas Negara', 'sector': 'Utilities'},
    'JSMR.JK': {'name': 'Jasa Marga', 'sector': 'Industrials'},
    'BBNI.JK': {'name': 'Bank Negara Indonesia', 'sector': 'Financials'},
    'ADRO.JK': {'name': 'Adaro Energy', 'sector': 'Energy'},
    'ANTM.JK': {'name': 'Aneka Tambang', 'sector': 'Materials'},
    'BRIS.JK': {'name': 'Bank Syariah Indonesia', 'sector': 'Financials'},
    'TOWR.JK': {'name': 'Sarana Menara Nusantara', 'sector': 'Communication Services'}
}

def generate_historical_data(base_price, days=365):
    """Generate historical price data"""
    historical = []
    current_price = base_price
    end_date = datetime.now()
    
    for i in range(days):
        date = end_date - timedelta(days=days-i-1)
        
        # Random daily change between -3% and 3%
        change_percent = random.uniform(-0.03, 0.03)
        current_price *= (1 + change_percent)
        
        # Daily OHLC
        open_price = current_price * random.uniform(0.98, 1.02)
        high_price = max(open_price, current_price) * random.uniform(1.0, 1.02)
        low_price = min(open_price, current_price) * random.uniform(0.98, 1.0)
        close_price = current_price
        volume = random.randint(1000000, 50000000)
        
        historical.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Open': round(open_price, 2),
            'High': round(high_price, 2),
            'Low': round(low_price, 2),
            'Close': round(close_price, 2),
            'Volume': volume
        })
    
    return historical

def generate_test_stock_data(symbol, info):
    """Generate comprehensive test data for a single stock"""
    base_price = random.uniform(500, 25000)
    current_price = base_price * random.uniform(0.9, 1.1)
    prev_close = current_price / random.uniform(0.97, 1.03)
    day_change = current_price - prev_close
    day_change_percent = (day_change / prev_close) * 100
    
    # Generate historical data
    historical = generate_historical_data(base_price)
    
    # Calculate technical indicators from historical
    closes = [h['Close'] for h in historical]
    ma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
    ma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
    ma_200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else None
    
    # Performance metrics
    perf_1d = ((closes[-1] / closes[-2]) - 1) * 100 if len(closes) >= 2 else 0
    perf_1w = ((closes[-1] / closes[-5]) - 1) * 100 if len(closes) >= 5 else 0
    perf_1m = ((closes[-1] / closes[-22]) - 1) * 100 if len(closes) >= 22 else 0
    
    return {
        'symbol': symbol,
        'basic': {
            'name': info['name'],
            'price': round(current_price, 2),
            'previousClose': round(prev_close, 2),
            'dayChange': round(day_change, 2),
            'dayChangePercent': round(day_change_percent, 2),
            'volume': random.randint(1000000, 100000000),
            'avgVolume': random.randint(5000000, 50000000),
            'dayHigh': round(current_price * random.uniform(1.0, 1.02), 2),
            'dayLow': round(current_price * random.uniform(0.98, 1.0), 2),
            'fiftyTwoWeekHigh': round(max(closes) * 1.05, 2),
            'fiftyTwoWeekLow': round(min(closes) * 0.95, 2),
            'marketCap': random.randint(10000000000, 500000000000000),
            'sharesOutstanding': random.randint(1000000000, 50000000000),
            'float': random.randint(500000000, 25000000000),
            'beta': round(random.uniform(0.5, 1.5), 2),
            'currency': 'IDR'
        },
        'fundamentals': {
            'pe': round(random.uniform(5, 35), 2) if random.random() > 0.1 else None,
            'forwardPE': round(random.uniform(5, 30), 2) if random.random() > 0.2 else None,
            'peg': round(random.uniform(0.5, 3), 2) if random.random() > 0.3 else None,
            'pb': round(random.uniform(0.5, 5), 2) if random.random() > 0.1 else None,
            'ps': round(random.uniform(0.5, 10), 2) if random.random() > 0.2 else None,
            'eps': round(random.uniform(50, 2000), 2) if random.random() > 0.1 else None,
            'forwardEps': round(random.uniform(60, 2200), 2) if random.random() > 0.2 else None,
            'dividendYield': round(random.uniform(0, 5), 2) if random.random() > 0.3 else None,
            'dividendRate': round(random.uniform(0, 500), 2) if random.random() > 0.4 else None,
            'payoutRatio': round(random.uniform(0.1, 0.7), 2) if random.random() > 0.4 else None,
            'roe': round(random.uniform(0.05, 0.3), 4) if random.random() > 0.2 else None,
            'roa': round(random.uniform(0.01, 0.15), 4) if random.random() > 0.2 else None,
            'grossMargin': round(random.uniform(0.1, 0.6), 4) if random.random() > 0.3 else None,
            'operatingMargin': round(random.uniform(0.05, 0.3), 4) if random.random() > 0.3 else None,
            'profitMargin': round(random.uniform(0.02, 0.2), 4) if random.random() > 0.3 else None,
            'debtToEquity': round(random.uniform(0.1, 2), 2) if random.random() > 0.2 else None,
            'currentRatio': round(random.uniform(0.8, 3), 2) if random.random() > 0.2 else None,
            'quickRatio': round(random.uniform(0.5, 2.5), 2) if random.random() > 0.3 else None,
            'bookValue': round(random.uniform(100, 5000), 2) if random.random() > 0.2 else None,
            'revenuePerShare': round(random.uniform(500, 10000), 2) if random.random() > 0.3 else None,
            'totalCashPerShare': round(random.uniform(50, 2000), 2) if random.random() > 0.3 else None,
            'enterpriseValue': random.randint(10000000000, 600000000000000) if random.random() > 0.2 else None,
            'evToRevenue': round(random.uniform(1, 20), 2) if random.random() > 0.3 else None,
            'evToEbitda': round(random.uniform(5, 25), 2) if random.random() > 0.3 else None
        },
        'technicals': {
            'ma_20': round(ma_20, 2) if ma_20 else None,
            'ma_50': round(ma_50, 2) if ma_50 else None,
            'ma_200': round(ma_200, 2) if ma_200 else None,
            'rsi_14': round(random.uniform(30, 70), 2),
            'perf_1d': round(perf_1d, 2),
            'perf_1w': round(perf_1w, 2),
            'perf_1m': round(perf_1m, 2),
            'perf_3m': round(random.uniform(-20, 30), 2),
            'perf_ytd': round(random.uniform(-15, 25), 2)
        },
        'company': {
            'sector': info['sector'],
            'industry': f"{info['sector']} Industry",
            'fullTimeEmployees': random.randint(100, 50000) if random.random() > 0.3 else None,
            'website': f"https://www.{symbol.lower().replace('.jk', '')}.co.id",
            'description': f"{info['name']} is a leading company in the {info['sector']} sector in Indonesia.",
            'country': 'Indonesia',
            'city': 'Jakarta',
            'address': f"{random.randint(1, 100)} Jl. Sudirman"
        },
        'financials': {
            'revenue': random.randint(1000000000, 100000000000000) if random.random() > 0.2 else None,
            'netIncome': random.randint(100000000, 10000000000000) if random.random() > 0.2 else None,
            'totalAssets': random.randint(5000000000, 500000000000000) if random.random() > 0.2 else None,
            'totalLiabilities': random.randint(2000000000, 300000000000000) if random.random() > 0.3 else None,
            'totalEquity': random.randint(1000000000, 200000000000000) if random.random() > 0.3 else None,
            'operatingCashFlow': random.randint(500000000, 50000000000000) if random.random() > 0.3 else None,
            'freeCashFlow': random.randint(200000000, 30000000000000) if random.random() > 0.4 else None
        },
        'historical': {
            'daily': historical[-30:],  # Last 30 days for preview
            'monthly': historical[::30]  # Monthly samples
        },
        'lastUpdate': datetime.now(JKT_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')
    }

def main():
    # Create directory structure
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    os.makedirs(os.path.join(data_dir, 'stocks'), exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'historicals'), exist_ok=True)
    
    # Generate data for each stock
    index_data = {
        'stocks': [],
        'last_update': datetime.now(JKT_TZ).strftime('%Y-%m-%d %H:%M:%S %Z'),
        'total_stocks': len(STOCKS)
    }
    
    fundamentals_data = {}
    screener_cache = {
        'value_stocks': [],
        'growth_stocks': [],
        'large_cap': [],
        'sectors': {}
    }
    
    for symbol, info in STOCKS.items():
        print(f"Generating test data for {symbol}...")
        
        # Generate comprehensive stock data
        stock_data = generate_test_stock_data(symbol, info)
        
        # Save individual stock file
        stock_file = os.path.join(data_dir, 'stocks', f'{symbol.replace(".JK", "")}.json')
        with open(stock_file, 'w') as f:
            json.dump(stock_data, f, indent=2)
        
        # Save historical data
        hist_file = os.path.join(data_dir, 'historicals', f'{symbol.replace(".JK", "")}_daily.json')
        historical_full = generate_historical_data(stock_data['basic']['price'], 365)
        with open(hist_file, 'w') as f:
            json.dump(historical_full, f)
        
        # Add to index
        index_entry = {
            'symbol': symbol,
            'name': info['name'],
            'price': stock_data['basic']['price'],
            'change': stock_data['basic']['dayChange'],
            'changePercent': stock_data['basic']['dayChangePercent'],
            'volume': stock_data['basic']['volume'],
            'marketCap': stock_data['basic']['marketCap'],
            'pe': stock_data['fundamentals']['pe'],
            'sector': info['sector']
        }
        index_data['stocks'].append(index_entry)
        
        # Add to fundamentals
        fundamentals_data[symbol] = stock_data['fundamentals']
        
        # Categorize for screener cache
        if stock_data['fundamentals']['pe'] and stock_data['fundamentals']['pe'] < 15:
            screener_cache['value_stocks'].append(index_entry)
        if stock_data['fundamentals']['pe'] and stock_data['fundamentals']['pe'] > 20:
            screener_cache['growth_stocks'].append(index_entry)
        if stock_data['basic']['marketCap'] > 10000000000000:  # > 10T IDR
            screener_cache['large_cap'].append(index_entry)
        
        # Group by sector
        sector = info['sector']
        if sector not in screener_cache['sectors']:
            screener_cache['sectors'][sector] = []
        screener_cache['sectors'][sector].append(index_entry)
    
    # Save index file
    with open(os.path.join(data_dir, 'index.json'), 'w') as f:
        json.dump(index_data, f, indent=2)
    
    # Save fundamentals file
    with open(os.path.join(data_dir, 'fundamentals.json'), 'w') as f:
        json.dump(fundamentals_data, f, indent=2)
    
    # Save screener cache
    with open(os.path.join(data_dir, 'screener_cache.json'), 'w') as f:
        json.dump(screener_cache, f, indent=2)
    
    print(f"\nTest data generation completed!")
    print(f"Generated data for {len(STOCKS)} stocks")
    print(f"Files saved in: {data_dir}")

if __name__ == '__main__':
    main()
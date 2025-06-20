#!/usr/bin/env python3
"""
Enhanced Yahoo Finance scraper for comprehensive Indonesian stock data
Collects fundamentals, technicals, historicals, and company info
"""

import yfinance as yf
import json
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any
import time
import numpy as np
import pandas as pd
from stock_symbols import INDONESIAN_STOCKS

# Jakarta timezone
JKT_TZ = pytz.timezone('Asia/Jakarta')

def safe_get(data: Any, *keys, default=None):
    """Safely get nested dictionary values"""
    try:
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key, default)
            elif hasattr(result, key):
                result = getattr(result, key)
            else:
                return default
        return result if result is not None else default
    except:
        return default

def calculate_technical_indicators(hist_data: pd.DataFrame) -> Dict:
    """Calculate technical indicators from historical data"""
    if hist_data.empty:
        return {}
    
    try:
        close_prices = hist_data['Close']
        
        # Moving averages
        ma_20 = close_prices.rolling(window=20).mean().iloc[-1] if len(close_prices) >= 20 else None
        ma_50 = close_prices.rolling(window=50).mean().iloc[-1] if len(close_prices) >= 50 else None
        ma_200 = close_prices.rolling(window=200).mean().iloc[-1] if len(close_prices) >= 200 else None
        
        # RSI (14 days)
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1] if len(close_prices) >= 14 else None
        
        # Price performance
        current_price = close_prices.iloc[-1]
        perf_1d = ((current_price / close_prices.iloc[-2]) - 1) * 100 if len(close_prices) >= 2 else None
        perf_1w = ((current_price / close_prices.iloc[-5]) - 1) * 100 if len(close_prices) >= 5 else None
        perf_1m = ((current_price / close_prices.iloc[-22]) - 1) * 100 if len(close_prices) >= 22 else None
        perf_3m = ((current_price / close_prices.iloc[-66]) - 1) * 100 if len(close_prices) >= 66 else None
        perf_ytd = ((current_price / close_prices[str(datetime.now().year):].iloc[0]) - 1) * 100 if str(datetime.now().year) in hist_data.index.astype(str) else None
        
        return {
            'ma_20': round(ma_20, 2) if ma_20 else None,
            'ma_50': round(ma_50, 2) if ma_50 else None,
            'ma_200': round(ma_200, 2) if ma_200 else None,
            'rsi_14': round(rsi, 2) if rsi and not np.isnan(rsi) else None,
            'perf_1d': round(perf_1d, 2) if perf_1d else None,
            'perf_1w': round(perf_1w, 2) if perf_1w else None,
            'perf_1m': round(perf_1m, 2) if perf_1m else None,
            'perf_3m': round(perf_3m, 2) if perf_3m else None,
            'perf_ytd': round(perf_ytd, 2) if perf_ytd else None
        }
    except Exception as e:
        print(f"Error calculating technical indicators: {e}")
        return {}

def scrape_comprehensive_data(symbol: str) -> Dict:
    """Scrape comprehensive data for a single stock"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get historical data (1 year daily, 5 years monthly)
        end_date = datetime.now()
        start_date_1y = end_date - timedelta(days=365)
        start_date_5y = end_date - timedelta(days=365*5)
        
        hist_1y = ticker.history(start=start_date_1y, end=end_date)
        hist_5y = ticker.history(start=start_date_5y, end=end_date, interval='1mo')
        
        # Calculate technical indicators
        technicals = calculate_technical_indicators(hist_1y)
        
        # Get financials
        try:
            income_stmt = ticker.quarterly_income_stmt
            balance_sheet = ticker.quarterly_balance_sheet
            cash_flow = ticker.quarterly_cashflow
        except:
            income_stmt = pd.DataFrame()
            balance_sheet = pd.DataFrame()
            cash_flow = pd.DataFrame()
        
        # Extract comprehensive data
        data = {
            'symbol': symbol,
            'basic': {
                'name': info.get('longName', ''),
                'price': info.get('currentPrice', 0),
                'previousClose': info.get('previousClose', 0),
                'dayChange': info.get('currentPrice', 0) - info.get('previousClose', 0),
                'dayChangePercent': ((info.get('currentPrice', 0) / info.get('previousClose', 1)) - 1) * 100 if info.get('previousClose', 0) > 0 else 0,
                'volume': info.get('volume', 0),
                'avgVolume': info.get('averageVolume', 0),
                'dayHigh': info.get('dayHigh', 0),
                'dayLow': info.get('dayLow', 0),
                'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', 0),
                'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', 0),
                'marketCap': info.get('marketCap', 0),
                'sharesOutstanding': info.get('sharesOutstanding', 0),
                'float': info.get('floatShares', 0),
                'beta': info.get('beta', None),
                'currency': info.get('currency', 'IDR')
            },
            'fundamentals': {
                'pe': info.get('trailingPE', None),
                'forwardPE': info.get('forwardPE', None),
                'peg': info.get('pegRatio', None),
                'pb': info.get('priceToBook', None),
                'ps': info.get('priceToSalesTrailing12Months', None),
                'eps': info.get('trailingEps', None),
                'forwardEps': info.get('forwardEps', None),
                'dividendYield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else None,
                'dividendRate': info.get('dividendRate', None),
                'payoutRatio': info.get('payoutRatio', None),
                'roe': info.get('returnOnEquity', None),
                'roa': info.get('returnOnAssets', None),
                'grossMargin': info.get('grossMargins', None),
                'operatingMargin': info.get('operatingMargins', None),
                'profitMargin': info.get('profitMargins', None),
                'debtToEquity': info.get('debtToEquity', None),
                'currentRatio': info.get('currentRatio', None),
                'quickRatio': info.get('quickRatio', None),
                'bookValue': info.get('bookValue', None),
                'revenuePerShare': info.get('revenuePerShare', None),
                'totalCashPerShare': info.get('totalCashPerShare', None),
                'enterpriseValue': info.get('enterpriseValue', None),
                'evToRevenue': info.get('enterpriseToRevenue', None),
                'evToEbitda': info.get('enterpriseToEbitda', None)
            },
            'technicals': technicals,
            'company': {
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'fullTimeEmployees': info.get('fullTimeEmployees', None),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', ''),
                'country': info.get('country', 'Indonesia'),
                'city': info.get('city', ''),
                'address': info.get('address1', '')
            },
            'financials': {
                'revenue': float(income_stmt.loc['Total Revenue'].iloc[0]) if not income_stmt.empty and 'Total Revenue' in income_stmt.index else None,
                'netIncome': float(income_stmt.loc['Net Income'].iloc[0]) if not income_stmt.empty and 'Net Income' in income_stmt.index else None,
                'totalAssets': float(balance_sheet.loc['Total Assets'].iloc[0]) if not balance_sheet.empty and 'Total Assets' in balance_sheet.index else None,
                'totalLiabilities': float(balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0]) if not balance_sheet.empty and 'Total Liabilities Net Minority Interest' in balance_sheet.index else None,
                'totalEquity': float(balance_sheet.loc['Total Equity Gross Minority Interest'].iloc[0]) if not balance_sheet.empty and 'Total Equity Gross Minority Interest' in balance_sheet.index else None,
                'operatingCashFlow': float(cash_flow.loc['Operating Cash Flow'].iloc[0]) if not cash_flow.empty and 'Operating Cash Flow' in cash_flow.index else None,
                'freeCashFlow': float(cash_flow.loc['Free Cash Flow'].iloc[0]) if not cash_flow.empty and 'Free Cash Flow' in cash_flow.index else None
            },
            'historical': {
                'daily': hist_1y.reset_index().to_dict('records') if not hist_1y.empty else [],
                'monthly': hist_5y.reset_index().to_dict('records') if not hist_5y.empty else []
            },
            'lastUpdate': datetime.now(JKT_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')
        }
        
        # Clean up data
        for key in ['basic', 'fundamentals', 'financials']:
            for field, value in data[key].items():
                if isinstance(value, float):
                    if np.isnan(value) or np.isinf(value):
                        data[key][field] = None
                    else:
                        data[key][field] = round(value, 2)
        
        # Format historical data
        for period in ['daily', 'monthly']:
            for record in data['historical'][period]:
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
                for field in ['Open', 'High', 'Low', 'Close']:
                    if field in record:
                        record[field] = round(record[field], 2)
                if 'Volume' in record:
                    record['Volume'] = int(record['Volume'])
        
        return data
        
    except Exception as e:
        print(f"Error scraping {symbol}: {e}")
        return None

def generate_data_structure():
    """Generate the new data directory structure"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    # Create directory structure
    dirs = [
        'data',
        'data/stocks',
        'data/historicals'
    ]
    
    for dir_path in dirs:
        full_path = os.path.join(base_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)

def main():
    """Main scraping function"""
    print("Starting enhanced data scraping...")
    
    # Generate directory structure
    generate_data_structure()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    all_stocks_data = []
    fundamentals_data = {}
    index_data = {
        'stocks': [],
        'last_update': datetime.now(JKT_TZ).strftime('%Y-%m-%d %H:%M:%S %Z'),
        'total_stocks': len(INDONESIAN_STOCKS)
    }
    
    for i, (symbol, name) in enumerate(INDONESIAN_STOCKS.items()):
        print(f"Scraping {symbol} ({i+1}/{len(INDONESIAN_STOCKS)})...")
        
        data = scrape_comprehensive_data(symbol)
        
        if data:
            # Save individual stock file
            stock_file = os.path.join(data_dir, 'stocks', f'{symbol.replace(".JK", "")}.json')
            with open(stock_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save historical data separately for better performance
            hist_file = os.path.join(data_dir, 'historicals', f'{symbol.replace(".JK", "")}_daily.json')
            with open(hist_file, 'w') as f:
                json.dump(data['historical']['daily'], f)
            
            # Add to index
            index_data['stocks'].append({
                'symbol': symbol,
                'name': data['basic']['name'],
                'price': data['basic']['price'],
                'change': data['basic']['dayChange'],
                'changePercent': data['basic']['dayChangePercent'],
                'volume': data['basic']['volume'],
                'marketCap': data['basic']['marketCap'],
                'pe': data['fundamentals']['pe'],
                'sector': data['company']['sector']
            })
            
            # Add to fundamentals
            fundamentals_data[symbol] = data['fundamentals']
            
            # Delay to avoid rate limiting
            time.sleep(1)
    
    # Save index file
    index_file = os.path.join(data_dir, 'index.json')
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    # Save fundamentals file
    fundamentals_file = os.path.join(data_dir, 'fundamentals.json')
    with open(fundamentals_file, 'w') as f:
        json.dump(fundamentals_data, f, indent=2)
    
    # Save screener cache with pre-calculated filters
    screener_cache = {
        'value_stocks': [s for s in index_data['stocks'] if s['pe'] and s['pe'] < 15],
        'growth_stocks': [s for s in index_data['stocks'] if s['pe'] and s['pe'] > 20],
        'large_cap': [s for s in index_data['stocks'] if s['marketCap'] and s['marketCap'] > 10000000000000],  # > 10T IDR
        'sectors': {}
    }
    
    # Group by sector
    for stock in index_data['stocks']:
        sector = stock.get('sector', 'Unknown')
        if sector not in screener_cache['sectors']:
            screener_cache['sectors'][sector] = []
        screener_cache['sectors'][sector].append(stock)
    
    screener_file = os.path.join(data_dir, 'screener_cache.json')
    with open(screener_file, 'w') as f:
        json.dump(screener_cache, f, indent=2)
    
    print(f"Enhanced scraping completed! Scraped {len(index_data['stocks'])} stocks.")
    
    # Also update the old format for backward compatibility
    old_data = {
        'stocks': [{
            'symbol': s['symbol'],
            'name': s['name'],
            'price': s['price'],
            'change': s['change'],
            'changePercent': s['changePercent'],
            'volume': s['volume'],
            'dayHigh': 0,
            'dayLow': 0,
            'marketCap': s['marketCap'],
            'fiftyTwoWeekHigh': 0,
            'fiftyTwoWeekLow': 0,
            'lastUpdate': datetime.now(JKT_TZ).strftime('%Y-%m-%d %H:%M:%S')
        } for s in index_data['stocks']],
        'last_update': index_data['last_update'],
        'data_quality': {
            'real_data_count': len(index_data['stocks']),
            'total_stocks': len(INDONESIAN_STOCKS),
            'real_data_percentage': (len(index_data['stocks']) / len(INDONESIAN_STOCKS)) * 100
        }
    }
    
    old_file = os.path.join(base_dir, 'static', 'data', 'stocks.json')
    with open(old_file, 'w') as f:
        json.dump(old_data, f, indent=2)

if __name__ == '__main__':
    main()
import json
import os
from datetime import datetime
from jinja2 import Template

# Static HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indonesian Stock Market Dashboard</title>
    <style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: #f0f2f5;
    color: #333;
    line-height: 1.6;
}

header {
    background: linear-gradient(135deg, #c41e3a 0%, #8b0000 100%);
    color: white;
    padding: 2rem 0;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
}

.subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 0.5rem;
}

.last-update {
    font-size: 0.9rem;
    opacity: 0.8;
    font-style: italic;
}

main {
    max-width: 1400px;
    margin: 2rem auto;
    padding: 0 1rem;
}

.stock-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

.stock-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    border-top: 4px solid #ddd;
}

.stock-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.stock-card.positive {
    border-top-color: #10b981;
}

.stock-card.negative {
    border-top-color: #ef4444;
}

.stock-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.25rem;
}

.company-name {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.price-section {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #eee;
}

.current-price {
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.25rem;
}

.price-change {
    font-size: 1.1rem;
    font-weight: 600;
}

.positive .price-change {
    color: #10b981;
}

.negative .price-change {
    color: #ef4444;
}

.change-amount {
    margin-right: 0.5rem;
}

.stock-details {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9rem;
}

.label {
    color: #666;
    font-weight: 500;
}

.value {
    color: #1a1a1a;
    font-weight: 600;
}

footer {
    background-color: #1a1a1a;
    color: #ccc;
    text-align: center;
    padding: 2rem 0;
    margin-top: 4rem;
}

footer p {
    margin: 0.5rem 0;
    font-size: 0.9rem;
}

@media (max-width: 768px) {
    header h1 {
        font-size: 2rem;
    }
    
    .subtitle {
        font-size: 1rem;
    }
    
    .stock-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .current-price {
        font-size: 1.75rem;
    }
}
    </style>
</head>
<body>
    <header>
        <h1>Indonesian Stock Market Dashboard</h1>
        <p class="subtitle">Real-time data from Jakarta Stock Exchange (IDX)</p>
        <p class="last-update">Last updated: {{ last_update }}</p>
    </header>

    <main>
        <div class="stock-grid">
            {% for stock in stocks %}
            <div class="stock-card {% if stock.change > 0 %}positive{% elif stock.change < 0 %}negative{% endif %}">
                <div class="stock-header">
                    <h2>{{ stock.symbol }}</h2>
                    <p class="company-name">{{ stock.name }}</p>
                </div>
                
                <div class="price-section">
                    <p class="current-price">Rp {{ "{:,.0f}".format(stock.price) }}</p>
                    <p class="price-change">
                        <span class="change-amount">{{ "{:+,.0f}".format(stock.change) }}</span>
                        <span class="change-percent">({{ "{:+.2f}".format(stock.changePercent) }}%)</span>
                    </p>
                </div>
                
                <div class="stock-details">
                    <div class="detail-row">
                        <span class="label">Volume:</span>
                        <span class="value">{{ "{:,.0f}".format(stock.volume) }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Day Range:</span>
                        <span class="value">{{ "{:,.0f}".format(stock.dayLow) }} - {{ "{:,.0f}".format(stock.dayHigh) }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">52W Range:</span>
                        <span class="value">{{ "{:,.0f}".format(stock.fiftyTwoWeekLow) }} - {{ "{:,.0f}".format(stock.fiftyTwoWeekHigh) }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Market Cap:</span>
                        <span class="value">Rp {{ "{:,.0f}".format(stock.marketCap / 1000000000) }}B</span>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </main>

    <footer>
        <p>Data provided by Yahoo Finance | Built with Python & Flask</p>
        <p>Hosted on GitHub Pages with automated daily updates</p>
    </footer>
</body>
</html>"""

def generate_static_html():
    # Load stock data
    data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data', 'stocks.json')
    
    stocks = []
    last_update = "Never"
    
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
            stocks = data.get('stocks', [])
            last_update = data.get('last_update', 'Never')
    
    # Generate HTML
    template = Template(HTML_TEMPLATE)
    html_content = template.render(stocks=stocks, last_update=last_update)
    
    # Save to index.html in root for GitHub Pages
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Static HTML generated: {output_file}")

if __name__ == "__main__":
    generate_static_html()
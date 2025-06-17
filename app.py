from flask import Flask, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # Load stock data from JSON file
    data_file = os.path.join('static', 'data', 'stocks.json')
    
    stocks = []
    last_update = "Never"
    
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
            stocks = data.get('stocks', [])
            last_update = data.get('last_update', 'Never')
    
    return render_template('index.html', stocks=stocks, last_update=last_update)

if __name__ == '__main__':
    app.run(debug=True)
# Indonesian Stock Market Dashboard

A real-time dashboard displaying Indonesian stock market data from the Jakarta Stock Exchange (IDX). This project scrapes data from Yahoo Finance and displays it in a clean, responsive web interface.

## Features

- Real-time stock prices for top Indonesian companies
- Automatic updates twice daily via GitHub Actions
- Clean, responsive design with no JavaScript required
- Hosted for free on GitHub Pages
- Shows price changes, volume, market cap, and more

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the scraper to fetch data:
```bash
cd scripts
python scraper.py
```

3. Run the Flask app for local development:
```bash
python app.py
```

4. Visit http://localhost:5000

## Deployment

This project is designed to be hosted on GitHub Pages:

1. Fork or clone this repository
2. Enable GitHub Pages in your repository settings
3. Select "Deploy from a branch" and choose the main branch
4. The GitHub Action will automatically update the stock data twice daily

## How It Works

1. GitHub Actions runs the Python scraper twice daily
2. The scraper fetches data from Yahoo Finance for Indonesian stocks
3. A static HTML file is generated with the latest data
4. GitHub Pages serves the static HTML file

## Technologies Used

- Python (Flask, yfinance, BeautifulSoup4)
- HTML/CSS (no JavaScript)
- GitHub Actions for automation
- GitHub Pages for hosting
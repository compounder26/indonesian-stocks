// Bloomberg Terminal Style Application
class BloombergApp {
    constructor() {
        this.dataManager = new DataManager();
        this.currentView = 'market';
        this.currentSort = { field: 'symbol', direction: 'asc' };
        this.selectedStock = null;
        this.charts = {};
        
        this.init();
    }

    async init() {
        // Show loading overlay
        this.showLoading(true);
        
        try {
            // Initialize data
            await this.dataManager.initDB();
            await this.dataManager.loadData();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Render initial view
            this.renderMarketView();
            this.updateSidebars();
            
            // Check market status
            this.updateMarketStatus();
            
            // Hide loading overlay
            this.showLoading(false);
            
            // Set up auto-refresh (every 5 minutes)
            setInterval(() => this.refreshData(), 5 * 60 * 1000);
        } catch (error) {
            console.error('Initialization error:', error);
            this.showLoading(false);
            alert('Error loading market data. Please refresh the page.');
        }
    }

    setupEventListeners() {
        // Navigation tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchView(e.target.dataset.view));
        });
        
        // Search functionality
        const searchInput = document.getElementById('stockSearch');
        searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        
        // Table sorting
        document.querySelectorAll('#stocksTable th[data-sort]').forEach(th => {
            th.addEventListener('click', (e) => this.sortTable(e.target.dataset.sort));
        });
        
        // Grid controls
        document.getElementById('refreshData').addEventListener('click', () => this.refreshData());
        document.getElementById('exportData').addEventListener('click', () => this.exportData());
        document.getElementById('gridDensity').addEventListener('change', (e) => this.changeGridDensity(e.target.value));
        
        // Screener
        document.getElementById('runScreener').addEventListener('click', () => this.runScreener());
        
        // Market movers tabs
        document.querySelectorAll('.mover-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.showMovers(e.target.dataset.type));
        });
        
        // Modal close
        document.querySelector('.modal-close').addEventListener('click', () => this.closeModal());
        document.getElementById('stockDetailModal').addEventListener('click', (e) => {
            if (e.target.id === 'stockDetailModal') this.closeModal();
        });
        
        // Detail tabs
        document.querySelectorAll('.detail-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.showDetailTab(e.target.dataset.tab));
        });
    }

    switchView(view) {
        this.currentView = view;
        
        // Update nav tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.view === view);
        });
        
        // Update view containers
        document.querySelectorAll('.view-container').forEach(container => {
            container.classList.toggle('active', container.id === `${view}View`);
        });
        
        // Render view-specific content
        if (view === 'screener') {
            this.renderScreenerFilters();
        }
    }

    renderMarketView() {
        const tbody = document.getElementById('stocksTableBody');
        tbody.innerHTML = '';
        
        // Sort stocks
        const stocks = this.sortStocks([...this.dataManager.data.stocks]);
        
        stocks.forEach(stock => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="stock-symbol" data-symbol="${stock.symbol}">${stock.symbol}</span></td>
                <td>${stock.name}</td>
                <td class="numeric">${this.dataManager.formatCurrency(stock.price)}</td>
                <td class="numeric ${stock.change >= 0 ? 'positive' : 'negative'}">
                    ${stock.change >= 0 ? '+' : ''}${this.dataManager.formatNumber(stock.change)}
                </td>
                <td class="numeric ${stock.changePercent >= 0 ? 'positive' : 'negative'}">
                    ${stock.changePercent >= 0 ? '+' : ''}${this.dataManager.formatNumber(stock.changePercent)}%
                </td>
                <td class="numeric">${this.dataManager.formatVolume(stock.volume)}</td>
                <td class="numeric">${this.dataManager.formatCurrency(stock.marketCap)}</td>
                <td class="numeric">${stock.pe ? this.dataManager.formatNumber(stock.pe) : '-'}</td>
                <td>${stock.sector || '-'}</td>
                <td class="actions">
                    <div class="action-buttons">
                        <button class="action-btn" onclick="app.showStockDetail('${stock.symbol}')">
                            <i class="fas fa-chart-line"></i>
                        </button>
                        <button class="action-btn" onclick="app.addToWatchlist('${stock.symbol}')">
                            <i class="fas fa-star"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Add click handlers for stock symbols
        document.querySelectorAll('.stock-symbol').forEach(symbol => {
            symbol.addEventListener('click', (e) => this.showStockDetail(e.target.dataset.symbol));
        });
    }

    sortStocks(stocks) {
        const { field, direction } = this.currentSort;
        
        stocks.sort((a, b) => {
            let aVal = a[field];
            let bVal = b[field];
            
            // Handle null/undefined values
            if (aVal === null || aVal === undefined) aVal = -Infinity;
            if (bVal === null || bVal === undefined) bVal = -Infinity;
            
            // Handle string comparison
            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }
            
            if (direction === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });
        
        return stocks;
    }

    sortTable(field) {
        if (this.currentSort.field === field) {
            this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.field = field;
            this.currentSort.direction = 'asc';
        }
        
        this.renderMarketView();
    }

    updateSidebars() {
        // Update market stats
        const stats = this.dataManager.getMarketStats();
        document.getElementById('advancesCount').textContent = stats.advances;
        document.getElementById('declinesCount').textContent = stats.declines;
        document.getElementById('unchangedCount').textContent = stats.unchanged;
        document.getElementById('totalVolume').textContent = this.dataManager.formatVolume(stats.totalVolume);
        
        // Update sectors
        const sectorList = document.getElementById('sectorList');
        sectorList.innerHTML = '';
        
        Object.entries(stats.sectors).forEach(([sector, data]) => {
            const sectorItem = document.createElement('div');
            sectorItem.className = 'sector-item';
            sectorItem.innerHTML = `
                <span>${sector}</span>
                <span class="${data.avgChange >= 0 ? 'positive' : 'negative'}">
                    ${data.avgChange >= 0 ? '+' : ''}${this.dataManager.formatNumber(data.avgChange)}%
                </span>
            `;
            sectorItem.addEventListener('click', () => this.filterBySector(sector));
            sectorList.appendChild(sectorItem);
        });
        
        // Update movers
        this.showMovers('gainers');
        
        // Update data quality
        const realDataCount = this.dataManager.data.stocks.filter(s => s.price > 0).length;
        const totalStocks = this.dataManager.data.stocks.length;
        const qualityPercent = (realDataCount / totalStocks) * 100;
        
        document.getElementById('qualityBar').style.width = `${qualityPercent}%`;
        document.getElementById('qualityPercent').textContent = `${qualityPercent.toFixed(1)}%`;
        document.getElementById('lastUpdateTime').textContent = 
            this.dataManager.data.lastUpdate || 'Unknown';
    }

    showMovers(type) {
        // Update active tab
        document.querySelectorAll('.mover-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.type === type);
        });
        
        // Get movers
        const movers = this.dataManager.getMovers(type, 5);
        
        // Render movers
        const moversList = document.getElementById('moversList');
        moversList.innerHTML = '';
        
        movers.forEach(stock => {
            const item = document.createElement('div');
            item.className = 'mover-item';
            item.innerHTML = `
                <span class="stock-symbol" data-symbol="${stock.symbol}">${stock.symbol}</span>
                <span class="${stock.changePercent >= 0 ? 'positive' : 'negative'}">
                    ${stock.changePercent >= 0 ? '+' : ''}${this.dataManager.formatNumber(stock.changePercent)}%
                </span>
            `;
            item.addEventListener('click', () => this.showStockDetail(stock.symbol));
            moversList.appendChild(item);
        });
    }

    handleSearch(query) {
        const results = this.dataManager.searchStocks(query);
        const resultsContainer = document.getElementById('searchResults');
        
        if (query.length === 0) {
            resultsContainer.style.display = 'none';
            return;
        }
        
        resultsContainer.innerHTML = '';
        resultsContainer.style.display = 'block';
        
        results.slice(0, 5).forEach(stock => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.innerHTML = `
                <span>${stock.symbol} - ${stock.name}</span>
                <span class="${stock.changePercent >= 0 ? 'positive' : 'negative'}">
                    ${this.dataManager.formatCurrency(stock.price)}
                </span>
            `;
            item.addEventListener('click', () => {
                this.showStockDetail(stock.symbol);
                resultsContainer.style.display = 'none';
                document.getElementById('stockSearch').value = '';
            });
            resultsContainer.appendChild(item);
        });
    }

    async showStockDetail(symbol) {
        this.selectedStock = symbol;
        const modal = document.getElementById('stockDetailModal');
        modal.style.display = 'block';
        
        // Load detailed data
        const stockData = await this.dataManager.loadStockDetail(symbol);
        if (!stockData) {
            alert('Error loading stock details');
            return;
        }
        
        // Update modal header
        document.getElementById('modalStockName').textContent = 
            `${stockData.symbol} - ${stockData.basic.name}`;
        
        // Show overview tab by default
        this.showDetailTab('overview', stockData);
    }

    async showDetailTab(tab, stockData = null) {
        // Update active tab
        document.querySelectorAll('.detail-tab').forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tab);
        });
        
        const content = document.getElementById('detailContent');
        
        // Get stock data if not provided
        if (!stockData && this.selectedStock) {
            stockData = await this.dataManager.loadStockDetail(this.selectedStock);
        }
        
        switch (tab) {
            case 'overview':
                this.renderOverviewTab(content, stockData);
                break;
            case 'chart':
                this.renderChartTab(content, stockData);
                break;
            case 'financials':
                this.renderFinancialsTab(content, stockData);
                break;
            case 'technicals':
                this.renderTechnicalsTab(content, stockData);
                break;
        }
    }

    renderOverviewTab(container, data) {
        container.innerHTML = `
            <div class="metric-cards">
                <div class="metric-card">
                    <div class="metric-label">Current Price</div>
                    <div class="metric-value ${data.basic.dayChangePercent >= 0 ? 'positive' : 'negative'}">
                        ${this.dataManager.formatCurrency(data.basic.price)}
                    </div>
                    <div class="${data.basic.dayChangePercent >= 0 ? 'positive' : 'negative'}">
                        ${data.basic.dayChange >= 0 ? '+' : ''}${this.dataManager.formatNumber(data.basic.dayChange)}
                        (${data.basic.dayChangePercent >= 0 ? '+' : ''}${this.dataManager.formatNumber(data.basic.dayChangePercent)}%)
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Market Cap</div>
                    <div class="metric-value">${this.dataManager.formatCurrency(data.basic.marketCap)}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Volume</div>
                    <div class="metric-value">${this.dataManager.formatVolume(data.basic.volume)}</div>
                    <div class="text-muted">Avg: ${this.dataManager.formatVolume(data.basic.avgVolume)}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Day Range</div>
                    <div class="metric-value">
                        ${this.dataManager.formatCurrency(data.basic.dayLow)} - 
                        ${this.dataManager.formatCurrency(data.basic.dayHigh)}
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">52 Week Range</div>
                    <div class="metric-value">
                        ${this.dataManager.formatCurrency(data.basic.fiftyTwoWeekLow)} - 
                        ${this.dataManager.formatCurrency(data.basic.fiftyTwoWeekHigh)}
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">P/E Ratio</div>
                    <div class="metric-value">${data.fundamentals.pe ? this.dataManager.formatNumber(data.fundamentals.pe) : '-'}</div>
                </div>
            </div>
            
            <h3 style="margin-top: 20px; margin-bottom: 10px;">Company Information</h3>
            <div style="background: var(--bg-tertiary); padding: 15px; border: 1px solid var(--border-color);">
                <p><strong>Sector:</strong> ${data.company.sector || '-'}</p>
                <p><strong>Industry:</strong> ${data.company.industry || '-'}</p>
                <p><strong>Website:</strong> ${data.company.website ? `<a href="${data.company.website}" target="_blank">${data.company.website}</a>` : '-'}</p>
                <p style="margin-top: 10px;">${data.company.description || 'No description available.'}</p>
            </div>
        `;
    }

    async renderChartTab(container, data) {
        container.innerHTML = `
            <div class="chart-controls" style="margin-bottom: 20px;">
                <button class="chart-period active" data-period="1D">1D</button>
                <button class="chart-period" data-period="1W">1W</button>
                <button class="chart-period" data-period="1M">1M</button>
                <button class="chart-period" data-period="3M">3M</button>
                <button class="chart-period" data-period="1Y">1Y</button>
            </div>
            <div class="chart-container">
                <canvas id="stockChart"></canvas>
            </div>
        `;
        
        // Load historical data
        const historicalData = await this.dataManager.loadHistoricalData(data.symbol);
        
        // Create chart
        this.createStockChart(historicalData);
        
        // Add event listeners for period buttons
        container.querySelectorAll('.chart-period').forEach(btn => {
            btn.addEventListener('click', (e) => {
                container.querySelectorAll('.chart-period').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.updateChartPeriod(e.target.dataset.period, historicalData);
            });
        });
    }

    createStockChart(data) {
        const ctx = document.getElementById('stockChart').getContext('2d');
        
        // Destroy existing chart
        if (this.charts.stock) {
            this.charts.stock.destroy();
        }
        
        // Prepare data for last 30 days
        const recentData = data.slice(-30);
        
        this.charts.stock = new Chart(ctx, {
            type: 'line',
            data: {
                labels: recentData.map(d => new Date(d.Date).toLocaleDateString()),
                datasets: [{
                    label: 'Close Price',
                    data: recentData.map(d => d.Close),
                    borderColor: '#00ff41',
                    backgroundColor: 'rgba(0, 255, 65, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#333',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: '#333',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#808080',
                            maxRotation: 0,
                            autoSkip: true,
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        position: 'right',
                        grid: {
                            color: '#333',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#808080',
                            callback: (value) => 'Rp ' + value.toLocaleString()
                        }
                    }
                }
            }
        });
    }

    updateChartPeriod(period, fullData) {
        let days;
        switch (period) {
            case '1D': days = 1; break;
            case '1W': days = 7; break;
            case '1M': days = 30; break;
            case '3M': days = 90; break;
            case '1Y': days = 365; break;
            default: days = 30;
        }
        
        const filteredData = fullData.slice(-days);
        
        this.charts.stock.data.labels = filteredData.map(d => new Date(d.Date).toLocaleDateString());
        this.charts.stock.data.datasets[0].data = filteredData.map(d => d.Close);
        this.charts.stock.update();
    }

    renderFinancialsTab(container, data) {
        const f = data.fundamentals;
        const fin = data.financials;
        
        container.innerHTML = `
            <div class="financials-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                <div class="financial-section">
                    <h4 style="margin-bottom: 15px; color: var(--text-secondary);">Valuation Metrics</h4>
                    <table class="financial-table" style="width: 100%;">
                        <tr>
                            <td>P/E Ratio</td>
                            <td class="numeric">${f.pe ? this.dataManager.formatNumber(f.pe) : '-'}</td>
                        </tr>
                        <tr>
                            <td>Forward P/E</td>
                            <td class="numeric">${f.forwardPE ? this.dataManager.formatNumber(f.forwardPE) : '-'}</td>
                        </tr>
                        <tr>
                            <td>P/B Ratio</td>
                            <td class="numeric">${f.pb ? this.dataManager.formatNumber(f.pb) : '-'}</td>
                        </tr>
                        <tr>
                            <td>P/S Ratio</td>
                            <td class="numeric">${f.ps ? this.dataManager.formatNumber(f.ps) : '-'}</td>
                        </tr>
                        <tr>
                            <td>PEG Ratio</td>
                            <td class="numeric">${f.peg ? this.dataManager.formatNumber(f.peg) : '-'}</td>
                        </tr>
                        <tr>
                            <td>EV/Revenue</td>
                            <td class="numeric">${f.evToRevenue ? this.dataManager.formatNumber(f.evToRevenue) : '-'}</td>
                        </tr>
                        <tr>
                            <td>EV/EBITDA</td>
                            <td class="numeric">${f.evToEbitda ? this.dataManager.formatNumber(f.evToEbitda) : '-'}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="financial-section">
                    <h4 style="margin-bottom: 15px; color: var(--text-secondary);">Profitability</h4>
                    <table class="financial-table" style="width: 100%;">
                        <tr>
                            <td>ROE</td>
                            <td class="numeric">${f.roe ? (f.roe * 100).toFixed(2) + '%' : '-'}</td>
                        </tr>
                        <tr>
                            <td>ROA</td>
                            <td class="numeric">${f.roa ? (f.roa * 100).toFixed(2) + '%' : '-'}</td>
                        </tr>
                        <tr>
                            <td>Gross Margin</td>
                            <td class="numeric">${f.grossMargin ? (f.grossMargin * 100).toFixed(2) + '%' : '-'}</td>
                        </tr>
                        <tr>
                            <td>Operating Margin</td>
                            <td class="numeric">${f.operatingMargin ? (f.operatingMargin * 100).toFixed(2) + '%' : '-'}</td>
                        </tr>
                        <tr>
                            <td>Profit Margin</td>
                            <td class="numeric">${f.profitMargin ? (f.profitMargin * 100).toFixed(2) + '%' : '-'}</td>
                        </tr>
                        <tr>
                            <td>Dividend Yield</td>
                            <td class="numeric">${f.dividendYield ? f.dividendYield.toFixed(2) + '%' : '-'}</td>
                        </tr>
                        <tr>
                            <td>Payout Ratio</td>
                            <td class="numeric">${f.payoutRatio ? (f.payoutRatio * 100).toFixed(2) + '%' : '-'}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="financial-section">
                    <h4 style="margin-bottom: 15px; color: var(--text-secondary);">Per Share Data</h4>
                    <table class="financial-table" style="width: 100%;">
                        <tr>
                            <td>EPS</td>
                            <td class="numeric">${f.eps ? this.dataManager.formatCurrency(f.eps) : '-'}</td>
                        </tr>
                        <tr>
                            <td>Book Value</td>
                            <td class="numeric">${f.bookValue ? this.dataManager.formatCurrency(f.bookValue) : '-'}</td>
                        </tr>
                        <tr>
                            <td>Revenue/Share</td>
                            <td class="numeric">${f.revenuePerShare ? this.dataManager.formatCurrency(f.revenuePerShare) : '-'}</td>
                        </tr>
                        <tr>
                            <td>Cash/Share</td>
                            <td class="numeric">${f.totalCashPerShare ? this.dataManager.formatCurrency(f.totalCashPerShare) : '-'}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="financial-section">
                    <h4 style="margin-bottom: 15px; color: var(--text-secondary);">Financial Health</h4>
                    <table class="financial-table" style="width: 100%;">
                        <tr>
                            <td>Current Ratio</td>
                            <td class="numeric">${f.currentRatio ? this.dataManager.formatNumber(f.currentRatio) : '-'}</td>
                        </tr>
                        <tr>
                            <td>Quick Ratio</td>
                            <td class="numeric">${f.quickRatio ? this.dataManager.formatNumber(f.quickRatio) : '-'}</td>
                        </tr>
                        <tr>
                            <td>Debt/Equity</td>
                            <td class="numeric">${f.debtToEquity ? this.dataManager.formatNumber(f.debtToEquity) : '-'}</td>
                        </tr>
                        <tr>
                            <td>Total Assets</td>
                            <td class="numeric">${fin.totalAssets ? this.dataManager.formatCurrency(fin.totalAssets) : '-'}</td>
                        </tr>
                        <tr>
                            <td>Total Equity</td>
                            <td class="numeric">${fin.totalEquity ? this.dataManager.formatCurrency(fin.totalEquity) : '-'}</td>
                        </tr>
                    </table>
                </div>
            </div>
        `;
        
        // Add CSS for financial tables
        const style = document.createElement('style');
        style.textContent = `
            .financial-table {
                border-collapse: collapse;
            }
            .financial-table td {
                padding: 8px 12px;
                border-bottom: 1px solid var(--border-light);
            }
            .financial-table td:first-child {
                color: var(--text-secondary);
            }
            .financial-table td.numeric {
                text-align: right;
                font-family: 'Consolas', monospace;
            }
        `;
        if (!document.getElementById('financial-table-style')) {
            style.id = 'financial-table-style';
            document.head.appendChild(style);
        }
    }

    renderTechnicalsTab(container, data) {
        const t = data.technicals;
        
        container.innerHTML = `
            <div class="technicals-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                <div class="technical-section">
                    <h4 style="margin-bottom: 15px; color: var(--text-secondary);">Moving Averages</h4>
                    <table class="financial-table" style="width: 100%;">
                        <tr>
                            <td>MA 20</td>
                            <td class="numeric">${t.ma_20 ? this.dataManager.formatCurrency(t.ma_20) : '-'}</td>
                        </tr>
                        <tr>
                            <td>MA 50</td>
                            <td class="numeric">${t.ma_50 ? this.dataManager.formatCurrency(t.ma_50) : '-'}</td>
                        </tr>
                        <tr>
                            <td>MA 200</td>
                            <td class="numeric">${t.ma_200 ? this.dataManager.formatCurrency(t.ma_200) : '-'}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="technical-section">
                    <h4 style="margin-bottom: 15px; color: var(--text-secondary);">Technical Indicators</h4>
                    <table class="financial-table" style="width: 100%;">
                        <tr>
                            <td>RSI (14)</td>
                            <td class="numeric">${t.rsi_14 ? this.dataManager.formatNumber(t.rsi_14) : '-'}</td>
                        </tr>
                        <tr>
                            <td>Beta</td>
                            <td class="numeric">${data.basic.beta ? this.dataManager.formatNumber(data.basic.beta) : '-'}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="technical-section">
                    <h4 style="margin-bottom: 15px; color: var(--text-secondary);">Performance</h4>
                    <table class="financial-table" style="width: 100%;">
                        <tr>
                            <td>1 Day</td>
                            <td class="numeric ${t.perf_1d >= 0 ? 'positive' : 'negative'}">
                                ${t.perf_1d ? (t.perf_1d >= 0 ? '+' : '') + this.dataManager.formatNumber(t.perf_1d) + '%' : '-'}
                            </td>
                        </tr>
                        <tr>
                            <td>1 Week</td>
                            <td class="numeric ${t.perf_1w >= 0 ? 'positive' : 'negative'}">
                                ${t.perf_1w ? (t.perf_1w >= 0 ? '+' : '') + this.dataManager.formatNumber(t.perf_1w) + '%' : '-'}
                            </td>
                        </tr>
                        <tr>
                            <td>1 Month</td>
                            <td class="numeric ${t.perf_1m >= 0 ? 'positive' : 'negative'}">
                                ${t.perf_1m ? (t.perf_1m >= 0 ? '+' : '') + this.dataManager.formatNumber(t.perf_1m) + '%' : '-'}
                            </td>
                        </tr>
                        <tr>
                            <td>3 Months</td>
                            <td class="numeric ${t.perf_3m >= 0 ? 'positive' : 'negative'}">
                                ${t.perf_3m ? (t.perf_3m >= 0 ? '+' : '') + this.dataManager.formatNumber(t.perf_3m) + '%' : '-'}
                            </td>
                        </tr>
                        <tr>
                            <td>YTD</td>
                            <td class="numeric ${t.perf_ytd >= 0 ? 'positive' : 'negative'}">
                                ${t.perf_ytd ? (t.perf_ytd >= 0 ? '+' : '') + this.dataManager.formatNumber(t.perf_ytd) + '%' : '-'}
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
        `;
    }

    closeModal() {
        document.getElementById('stockDetailModal').style.display = 'none';
        this.selectedStock = null;
        
        // Destroy chart if exists
        if (this.charts.stock) {
            this.charts.stock.destroy();
            delete this.charts.stock;
        }
    }

    renderScreenerFilters() {
        // Get unique sectors
        const sectors = [...new Set(this.dataManager.data.stocks.map(s => s.sector).filter(Boolean))];
        
        const sectorFilters = document.getElementById('sectorFilters');
        sectorFilters.innerHTML = '';
        
        sectors.forEach(sector => {
            const item = document.createElement('div');
            item.className = 'sector-filter-item';
            item.innerHTML = `
                <input type="checkbox" id="sector-${sector}" value="${sector}">
                <label for="sector-${sector}">${sector}</label>
            `;
            sectorFilters.appendChild(item);
        });
    }

    runScreener() {
        // Gather filter values
        const filters = {
            peMin: parseFloat(document.getElementById('peMin').value) || undefined,
            peMax: parseFloat(document.getElementById('peMax').value) || undefined,
            pbMin: parseFloat(document.getElementById('pbMin').value) || undefined,
            pbMax: parseFloat(document.getElementById('pbMax').value) || undefined,
            marketCapMin: parseFloat(document.getElementById('mcapMin').value) || undefined,
            marketCapMax: parseFloat(document.getElementById('mcapMax').value) || undefined,
            divYieldMin: parseFloat(document.getElementById('divMin').value) || undefined,
            divYieldMax: parseFloat(document.getElementById('divMax').value) || undefined,
            perf1dMin: parseFloat(document.getElementById('perf1dMin').value) || undefined,
            perf1dMax: parseFloat(document.getElementById('perf1dMax').value) || undefined,
            perf1mMin: parseFloat(document.getElementById('perf1mMin').value) || undefined,
            perf1mMax: parseFloat(document.getElementById('perf1mMax').value) || undefined,
            sectors: []
        };
        
        // Get selected sectors
        document.querySelectorAll('#sectorFilters input:checked').forEach(input => {
            filters.sectors.push(input.value);
        });
        
        // Run screener
        const results = this.dataManager.runScreener(filters);
        
        // Display results
        const resultsContainer = document.getElementById('screenerResults');
        resultsContainer.innerHTML = `
            <h3>${results.length} Stocks Found</h3>
            <div class="data-grid" style="margin-top: 20px;">
                <table>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Name</th>
                            <th class="numeric">Price</th>
                            <th class="numeric">Change %</th>
                            <th class="numeric">P/E</th>
                            <th class="numeric">Market Cap</th>
                            <th>Sector</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(stock => `
                            <tr>
                                <td><span class="stock-symbol" data-symbol="${stock.symbol}">${stock.symbol}</span></td>
                                <td>${stock.name}</td>
                                <td class="numeric">${this.dataManager.formatCurrency(stock.price)}</td>
                                <td class="numeric ${stock.changePercent >= 0 ? 'positive' : 'negative'}">
                                    ${stock.changePercent >= 0 ? '+' : ''}${this.dataManager.formatNumber(stock.changePercent)}%
                                </td>
                                <td class="numeric">${stock.pe ? this.dataManager.formatNumber(stock.pe) : '-'}</td>
                                <td class="numeric">${this.dataManager.formatCurrency(stock.marketCap)}</td>
                                <td>${stock.sector || '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        // Add click handlers
        resultsContainer.querySelectorAll('.stock-symbol').forEach(symbol => {
            symbol.addEventListener('click', (e) => this.showStockDetail(e.target.dataset.symbol));
        });
    }

    async refreshData() {
        this.showLoading(true);
        await this.dataManager.loadData();
        this.renderMarketView();
        this.updateSidebars();
        this.showLoading(false);
    }

    exportData() {
        const data = this.dataManager.data.stocks;
        const csv = this.convertToCSV(data);
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `idx-stocks-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    convertToCSV(data) {
        const headers = ['Symbol', 'Name', 'Price', 'Change', 'Change %', 'Volume', 'Market Cap', 'P/E', 'Sector'];
        const rows = data.map(stock => [
            stock.symbol,
            stock.name,
            stock.price,
            stock.change,
            stock.changePercent,
            stock.volume,
            stock.marketCap,
            stock.pe || '',
            stock.sector || ''
        ]);
        
        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    changeGridDensity(density) {
        const table = document.getElementById('stocksTable');
        table.className = `grid-density-${density}`;
        
        // Add CSS for different densities
        const style = document.getElementById('grid-density-style') || document.createElement('style');
        style.id = 'grid-density-style';
        style.textContent = `
            .grid-density-compact td, .grid-density-compact th { padding: 4px 8px; font-size: 11px; }
            .grid-density-comfortable td, .grid-density-comfortable th { padding: 12px 16px; font-size: 13px; }
        `;
        document.head.appendChild(style);
    }

    filterBySector(sector) {
        // Switch to screener view
        this.switchView('screener');
        
        // Set sector filter
        setTimeout(() => {
            const sectorCheckbox = document.getElementById(`sector-${sector}`);
            if (sectorCheckbox) {
                sectorCheckbox.checked = true;
                this.runScreener();
            }
        }, 100);
    }

    addToWatchlist(symbol) {
        // Placeholder for watchlist functionality
        alert(`${symbol} added to watchlist!`);
    }

    updateMarketStatus() {
        const now = new Date();
        const jakartaTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Jakarta"}));
        const hours = jakartaTime.getHours();
        const minutes = jakartaTime.getMinutes();
        const day = jakartaTime.getDay();
        
        // IDX trading hours: 9:00 - 16:00 WIB, Monday-Friday
        const isOpen = day >= 1 && day <= 5 && 
                      ((hours === 9 && minutes >= 0) || (hours > 9 && hours < 16) || (hours === 16 && minutes === 0));
        
        const indicator = document.querySelector('.status-indicator');
        const text = document.querySelector('.status-text');
        
        if (isOpen) {
            indicator.classList.add('open');
            text.textContent = 'Market Open';
        } else {
            indicator.classList.remove('open');
            text.textContent = 'Market Closed';
        }
    }

    showLoading(show) {
        document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BloombergApp();
});
// Data Manager Module - Handles all data operations including IndexedDB
class DataManager {
    constructor() {
        this.db = null;
        this.data = {
            stocks: [],
            fundamentals: {},
            historicals: {},
            screenerCache: {},
            lastUpdate: null
        };
        this.initDB();
    }

    // Initialize IndexedDB
    async initDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('IDXTerminalDB', 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Create object stores
                if (!db.objectStoreNames.contains('stocks')) {
                    const stockStore = db.createObjectStore('stocks', { keyPath: 'symbol' });
                    stockStore.createIndex('sector', 'sector', { unique: false });
                    stockStore.createIndex('marketCap', 'marketCap', { unique: false });
                }
                
                if (!db.objectStoreNames.contains('fundamentals')) {
                    db.createObjectStore('fundamentals', { keyPath: 'symbol' });
                }
                
                if (!db.objectStoreNames.contains('historicals')) {
                    db.createObjectStore('historicals', { keyPath: 'id' });
                }
                
                if (!db.objectStoreNames.contains('metadata')) {
                    db.createObjectStore('metadata', { keyPath: 'key' });
                }
            };
        });
    }

    // Load data from JSON files
    async loadData() {
        try {
            // Check if data exists in IndexedDB first
            const cachedData = await this.getFromDB('metadata', 'lastUpdate');
            const now = new Date();
            
            if (cachedData && cachedData.value) {
                const lastUpdate = new Date(cachedData.value);
                const hoursSinceUpdate = (now - lastUpdate) / (1000 * 60 * 60);
                
                // If data is less than 1 hour old, use cached data
                if (hoursSinceUpdate < 1) {
                    console.log('Using cached data from IndexedDB');
                    await this.loadFromDB();
                    return this.data;
                }
            }
            
            console.log('Loading fresh data from server');
            
            // Load index file
            const indexResponse = await fetch('/data/index.json');
            const indexData = await indexResponse.json();
            
            this.data.stocks = indexData.stocks;
            this.data.lastUpdate = indexData.last_update;
            
            // Load fundamentals
            const fundamentalsResponse = await fetch('/data/fundamentals.json');
            this.data.fundamentals = await fundamentalsResponse.json();
            
            // Load screener cache
            const screenerResponse = await fetch('/data/screener_cache.json');
            this.data.screenerCache = await screenerResponse.json();
            
            // Store in IndexedDB
            await this.saveToIndexedDB();
            
            return this.data;
        } catch (error) {
            console.error('Error loading data:', error);
            // Try to load from IndexedDB as fallback
            await this.loadFromDB();
            return this.data;
        }
    }

    // Load individual stock data
    async loadStockDetail(symbol) {
        try {
            // Check IndexedDB first
            const cached = await this.getFromDB('stocks', symbol);
            if (cached && cached.detailData) {
                return cached.detailData;
            }
            
            // Load from server
            const cleanSymbol = symbol.replace('.JK', '');
            const response = await fetch(`/data/stocks/${cleanSymbol}.json`);
            const stockData = await response.json();
            
            // Update IndexedDB
            const transaction = this.db.transaction(['stocks'], 'readwrite');
            const store = transaction.objectStore('stocks');
            const existing = await this.getFromDB('stocks', symbol);
            if (existing) {
                existing.detailData = stockData;
                store.put(existing);
            }
            
            return stockData;
        } catch (error) {
            console.error(`Error loading detail for ${symbol}:`, error);
            return null;
        }
    }

    // Load historical data
    async loadHistoricalData(symbol, period = 'daily') {
        try {
            const id = `${symbol}_${period}`;
            
            // Check IndexedDB first
            const cached = await this.getFromDB('historicals', id);
            if (cached) {
                return cached.data;
            }
            
            // Load from server
            const cleanSymbol = symbol.replace('.JK', '');
            const response = await fetch(`/data/historicals/${cleanSymbol}_${period}.json`);
            const data = await response.json();
            
            // Store in IndexedDB
            await this.saveToDB('historicals', { id, symbol, period, data });
            
            return data;
        } catch (error) {
            console.error(`Error loading historical data for ${symbol}:`, error);
            return [];
        }
    }

    // Save data to IndexedDB
    async saveToIndexedDB() {
        if (!this.db) return;
        
        const transaction = this.db.transaction(['stocks', 'fundamentals', 'metadata'], 'readwrite');
        
        // Save stocks
        const stockStore = transaction.objectStore('stocks');
        for (const stock of this.data.stocks) {
            stockStore.put(stock);
        }
        
        // Save fundamentals
        const fundamentalStore = transaction.objectStore('fundamentals');
        for (const [symbol, data] of Object.entries(this.data.fundamentals)) {
            fundamentalStore.put({ symbol, ...data });
        }
        
        // Save metadata
        const metadataStore = transaction.objectStore('metadata');
        metadataStore.put({ key: 'lastUpdate', value: new Date().toISOString() });
        metadataStore.put({ key: 'dataLastUpdate', value: this.data.lastUpdate });
    }

    // Load data from IndexedDB
    async loadFromDB() {
        if (!this.db) return;
        
        const transaction = this.db.transaction(['stocks', 'fundamentals', 'metadata'], 'readonly');
        
        // Load stocks
        const stockStore = transaction.objectStore('stocks');
        this.data.stocks = await this.getAllFromStore(stockStore);
        
        // Load fundamentals
        const fundamentalStore = transaction.objectStore('fundamentals');
        const fundamentals = await this.getAllFromStore(fundamentalStore);
        this.data.fundamentals = {};
        fundamentals.forEach(f => {
            this.data.fundamentals[f.symbol] = f;
        });
        
        // Load metadata
        const metadataStore = transaction.objectStore('metadata');
        const lastUpdateData = await this.getFromStore(metadataStore, 'dataLastUpdate');
        if (lastUpdateData) {
            this.data.lastUpdate = lastUpdateData.value;
        }
    }

    // Helper methods for IndexedDB operations
    async getFromDB(storeName, key) {
        if (!this.db) return null;
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(key);
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async saveToDB(storeName, data) {
        if (!this.db) return;
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.put(data);
            
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async getAllFromStore(store) {
        return new Promise((resolve, reject) => {
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getFromStore(store, key) {
        return new Promise((resolve, reject) => {
            const request = store.get(key);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // Screener functionality
    runScreener(filters) {
        let results = [...this.data.stocks];
        
        // Apply filters
        if (filters.peMin !== undefined || filters.peMax !== undefined) {
            results = results.filter(stock => {
                const pe = stock.pe;
                if (pe === null || pe === undefined) return false;
                if (filters.peMin !== undefined && pe < filters.peMin) return false;
                if (filters.peMax !== undefined && pe > filters.peMax) return false;
                return true;
            });
        }
        
        if (filters.pbMin !== undefined || filters.pbMax !== undefined) {
            results = results.filter(stock => {
                const fundamentals = this.data.fundamentals[stock.symbol] || {};
                const pb = fundamentals.pb;
                if (pb === null || pb === undefined) return false;
                if (filters.pbMin !== undefined && pb < filters.pbMin) return false;
                if (filters.pbMax !== undefined && pb > filters.pbMax) return false;
                return true;
            });
        }
        
        if (filters.marketCapMin !== undefined || filters.marketCapMax !== undefined) {
            results = results.filter(stock => {
                const mcap = stock.marketCap / 1000000000; // Convert to billions
                if (mcap === 0) return false;
                if (filters.marketCapMin !== undefined && mcap < filters.marketCapMin) return false;
                if (filters.marketCapMax !== undefined && mcap > filters.marketCapMax) return false;
                return true;
            });
        }
        
        if (filters.divYieldMin !== undefined || filters.divYieldMax !== undefined) {
            results = results.filter(stock => {
                const fundamentals = this.data.fundamentals[stock.symbol] || {};
                const divYield = fundamentals.dividendYield;
                if (divYield === null || divYield === undefined) return false;
                if (filters.divYieldMin !== undefined && divYield < filters.divYieldMin) return false;
                if (filters.divYieldMax !== undefined && divYield > filters.divYieldMax) return false;
                return true;
            });
        }
        
        if (filters.sectors && filters.sectors.length > 0) {
            results = results.filter(stock => filters.sectors.includes(stock.sector));
        }
        
        if (filters.perf1dMin !== undefined || filters.perf1dMax !== undefined) {
            results = results.filter(stock => {
                const perf = stock.changePercent;
                if (filters.perf1dMin !== undefined && perf < filters.perf1dMin) return false;
                if (filters.perf1dMax !== undefined && perf > filters.perf1dMax) return false;
                return true;
            });
        }
        
        return results;
    }

    // Get market statistics
    getMarketStats() {
        const stats = {
            advances: 0,
            declines: 0,
            unchanged: 0,
            totalVolume: 0,
            sectors: {}
        };
        
        this.data.stocks.forEach(stock => {
            // Count advances/declines
            if (stock.changePercent > 0) {
                stats.advances++;
            } else if (stock.changePercent < 0) {
                stats.declines++;
            } else {
                stats.unchanged++;
            }
            
            // Sum volume
            stats.totalVolume += stock.volume || 0;
            
            // Group by sector
            const sector = stock.sector || 'Unknown';
            if (!stats.sectors[sector]) {
                stats.sectors[sector] = {
                    count: 0,
                    totalChange: 0,
                    stocks: []
                };
            }
            stats.sectors[sector].count++;
            stats.sectors[sector].totalChange += stock.changePercent || 0;
            stats.sectors[sector].stocks.push(stock);
        });
        
        // Calculate average change per sector
        Object.keys(stats.sectors).forEach(sector => {
            const sectorData = stats.sectors[sector];
            sectorData.avgChange = sectorData.totalChange / sectorData.count;
        });
        
        return stats;
    }

    // Get top movers
    getMovers(type = 'gainers', limit = 5) {
        let sorted = [...this.data.stocks];
        
        switch (type) {
            case 'gainers':
                sorted.sort((a, b) => (b.changePercent || 0) - (a.changePercent || 0));
                break;
            case 'losers':
                sorted.sort((a, b) => (a.changePercent || 0) - (b.changePercent || 0));
                break;
            case 'active':
                sorted.sort((a, b) => (b.volume || 0) - (a.volume || 0));
                break;
        }
        
        return sorted.slice(0, limit);
    }

    // Search stocks
    searchStocks(query) {
        if (!query) return [];
        
        const searchTerm = query.toLowerCase();
        return this.data.stocks.filter(stock => 
            stock.symbol.toLowerCase().includes(searchTerm) ||
            stock.name.toLowerCase().includes(searchTerm)
        );
    }

    // Format currency
    formatCurrency(value) {
        if (value === null || value === undefined || value === 0) return '-';
        
        if (value >= 1000000000000) {
            return `Rp ${(value / 1000000000000).toFixed(2)}T`;
        } else if (value >= 1000000000) {
            return `Rp ${(value / 1000000000).toFixed(2)}B`;
        } else if (value >= 1000000) {
            return `Rp ${(value / 1000000).toFixed(2)}M`;
        } else {
            return `Rp ${value.toLocaleString('id-ID')}`;
        }
    }

    // Format number
    formatNumber(value, decimals = 2) {
        if (value === null || value === undefined) return '-';
        return value.toFixed(decimals);
    }

    // Format volume
    formatVolume(value) {
        if (value === null || value === undefined || value === 0) return '-';
        
        if (value >= 1000000000) {
            return `${(value / 1000000000).toFixed(2)}B`;
        } else if (value >= 1000000) {
            return `${(value / 1000000).toFixed(2)}M`;
        } else if (value >= 1000) {
            return `${(value / 1000).toFixed(2)}K`;
        } else {
            return value.toString();
        }
    }
}

// Export as global
window.DataManager = DataManager;
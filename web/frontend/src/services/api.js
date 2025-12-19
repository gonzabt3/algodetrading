import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const tradingApi = {
  // Strategies
  getStrategies: () => api.get('/strategies'),
  
  // Backtests
  getBacktests: (params) => api.get('/backtests', { params }),
  getBacktest: (id) => api.get(`/backtests/${id}`),
  runBacktest: (data) => api.post('/backtests/run', data),
  
  // Stats
  getStats: () => api.get('/stats/summary'),
  
  // Market Data
  getMarketData: (symbol, days) => api.get(`/market-data/${symbol}`, { params: { days } }),
};

export default api;

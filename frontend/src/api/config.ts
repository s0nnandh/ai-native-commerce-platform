// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  ENDPOINTS: {
    ASSIST: '/api/assist',
    HEALTH: '/health',
    PRODUCTS: '/api/products'
  },
  TIMEOUT: 30000, // 30 seconds
};

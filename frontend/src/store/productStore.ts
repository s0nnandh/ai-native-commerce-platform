import { create } from 'zustand';
import type { BackendProduct, Product } from '../types';
import { mockProducts } from '../utils/mockData';
import { convertBackendProduct, productApi } from '../api/productApi';

interface ProductState {
  products: Product[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setProducts: (products: Product[]) => void;
  updateProductsByResponse: (products: BackendProduct[]) => void;
  clearProducts: () => void;
  loadInitialProducts: () => void;
  loadAllProducts: () => Promise<void>; // New method to load all products
}

export const useProductStore = create<ProductState>((set) => ({
  products: [],
  isLoading: false,
  error: null,
  
  setProducts: (products) => set({ products }),
  
  updateProductsByResponse: (products) => {
    console.log(products);
    set({ 
      products: products.map(convertBackendProduct),
      isLoading: false,
      error: null
    });
  },
  
  clearProducts: () => set({ products: [] }),
  
  // Load initial products (a subset for initial display)
  loadInitialProducts: async () => {
    set({ isLoading: true, error: null });
    
    try {
      // Fetch products from API
      const products = await productApi.getAllProducts();
      
      // Only show a subset initially
      const initialProducts = products.slice(0, 3);
      
      set({
        products: initialProducts,
        isLoading: false,
        error: null
      });
    } catch (error) {
      console.error('Failed to load initial products:', error);
      
      // Fallback to mock data if API fails
      set({
        products: mockProducts.slice(0, 3),
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to load products'
      });
    }
  },
  
  // Load all products (used when assist API returns empty products)
  loadAllProducts: async () => {
    set({ isLoading: true, error: null });
    
    try {
      // Fetch all products from API
      const products = await productApi.getAllProducts();
      
      set({
        products,
        isLoading: false,
        error: null
      });
    } catch (error) {
      console.error('Failed to load all products:', error);
      
      // Fallback to mock data if API fails
      set({
        products: mockProducts,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to load products'
      });
    }
  }
}));

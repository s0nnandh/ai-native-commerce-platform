import apiClient from './client';
import { API_CONFIG } from './config';
import type { ProductsResponse, BackendProduct, Product } from '../types';

// Helper function to convert backend product to frontend product
export const convertBackendProduct = (backendProduct: BackendProduct): Product => {
  return {
    id: backendProduct.product_id,
    name: backendProduct.name,
    description: backendProduct.description,
    price: backendProduct.price_usd,
    category: backendProduct.category,
    marginRank: Math.round(backendProduct.margin_percent),
    // Default image URL - in a real app, this would come from the backend or be generated
    imageUrl: `/images/products/${backendProduct.category}/${backendProduct.product_id}.jpg`,
    // Default to in stock
    inStock: true,
    // Convert pipe-delimited tags to array
    tags: backendProduct.tags ? backendProduct.tags.split('|').map(tag => tag.trim()) : [],
    // Convert semicolon-delimited ingredients to array
    ingredients: backendProduct.top_ingredients ? backendProduct.top_ingredients.split(';').map(ing => ing.trim()) : []
  };
};

// API service for product endpoints
export const productApi = {
  /**
   * Get all products
   * @returns Promise with the products response
   */
  getAllProducts: async (): Promise<Product[]> => {
    try {
      const response = await apiClient.get<ProductsResponse>(
        API_CONFIG.ENDPOINTS.PRODUCTS
      );
      
      // Convert backend products to frontend products
      return response.data.products.map(convertBackendProduct);
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  },

  /**
   * Get product by ID
   * @param id Product ID
   * @returns Promise with the product
   */
  getProductById: async (id: string): Promise<Product | null> => {
    try {
      // For now, fetch all products and find the one with matching ID
      // In a real app, this would be a separate API endpoint
      const products = await productApi.getAllProducts();
      return products.find(product => product.id === id) || null;
    } catch (error) {
      console.error(`Error fetching product with ID ${id}:`, error);
      throw error;
    }
  }
};

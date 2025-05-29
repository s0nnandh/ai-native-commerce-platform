import type { Product, Citation, AssistResponse } from '../types';

// Mock product data
export const mockProducts: Product[] = [
  {
    id: '1',
    name: 'Hydrating Facial Cleanser',
    description: 'A gentle, hydrating cleanser that removes impurities without stripping the skin of its natural moisture.',
    price: 24.99,
    imageUrl: 'https://images.unsplash.com/photo-1556228720-195a672e8a03?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
    category: 'Skincare',
    marginRank: 4,
    inStock: true,
    tags: ['cleanser', 'hydrating', 'sensitive skin']
  },
  {
    id: '2',
    name: 'Vitamin C Serum',
    description: 'Brightening serum with 15% vitamin C to reduce dark spots and improve skin texture.',
    price: 39.99,
    imageUrl: 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
    category: 'Skincare',
    marginRank: 5,
    inStock: true,
    tags: ['serum', 'brightening', 'vitamin c']
  },
  {
    id: '3',
    name: 'Hyaluronic Acid Moisturizer',
    description: 'Deeply hydrating moisturizer with hyaluronic acid to plump and hydrate the skin.',
    price: 32.50,
    imageUrl: 'https://images.unsplash.com/photo-1570194065650-d99fb4abbd90?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
    category: 'Skincare',
    marginRank: 3,
    inStock: true,
    tags: ['moisturizer', 'hydrating', 'hyaluronic acid']
  },
  {
    id: '4',
    name: 'Retinol Night Cream',
    description: 'Anti-aging night cream with retinol to reduce fine lines and wrinkles while you sleep.',
    price: 45.00,
    imageUrl: 'https://images.unsplash.com/photo-1567721913486-6585f069b332?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
    category: 'Skincare',
    marginRank: 5,
    inStock: false,
    tags: ['night cream', 'anti-aging', 'retinol']
  },
  {
    id: '5',
    name: 'SPF 50 Sunscreen',
    description: 'Broad-spectrum SPF 50 sunscreen that protects against UVA and UVB rays without leaving a white cast.',
    price: 28.00,
    imageUrl: 'https://images.unsplash.com/photo-1576426863848-c21f53c60b19?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
    category: 'Skincare',
    marginRank: 2,
    inStock: true,
    tags: ['sunscreen', 'spf', 'protection']
  },
  {
    id: '6',
    name: 'Exfoliating Face Scrub',
    description: 'Gentle exfoliating scrub that removes dead skin cells and unclogs pores for a smoother complexion.',
    price: 22.99,
    imageUrl: 'https://images.unsplash.com/photo-1601049676869-702ea24cfd58?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
    category: 'Skincare',
    marginRank: 3,
    inStock: true,
    tags: ['exfoliator', 'scrub', 'pores']
  }
];

// Mock citations
export const mockCitations: Citation[] = [
  {
    id: '1',
    snippet: 'Research on hyaluronic acid efficacy',
    text: 'Journal of Dermatology, 2023',
    source: 'Research on hyaluronic acid efficacy',
    url: 'https://example.com/research1'
  },
  {
    id: '2',
    snippet: 'Sunscreen recommendations',
    text: 'American Academy of Dermatology',
    source: 'Sunscreen recommendations',
    url: 'https://example.com/research2'
  },
  {
    id: '3',
    snippet: 'Product ingredients analysis',
    text: 'Skincare Product Database',
    source: 'Product ingredients analysis',
    url: 'https://example.com/database'
  }
];

// Mock response for skincare products
export const mockSkincareResponse: AssistResponse = {
  text: "Here are some skincare products that match your search. I've included a variety of products for different skin concerns. Would you like more specific recommendations based on your skin type or concerns?",
  products: [],
  citations: mockCitations,
  latency_ms: 250
};

// Mock response for no results
export const mockNoResultsResponse: AssistResponse = {
  text: "I couldn't find any products matching your search. Please try a different query or browse our categories.",
  products: [],
  citations: [],
  latency_ms: 150
};

// Function to simulate API response with delay
export const getMockResponse = (query: string): Promise<AssistResponse> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      if (query.toLowerCase().includes('skincare') || 
          query.toLowerCase().includes('skin') || 
          query.toLowerCase().includes('face')) {
        resolve(mockSkincareResponse);
      } else {
        resolve(mockNoResultsResponse);
      }
    }, 1000); // Simulate network delay
  });
};

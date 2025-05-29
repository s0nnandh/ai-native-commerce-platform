// Product Types
export interface BackendProduct {
  product_id: string;
  name: string;
  category: string;
  description: string;
  top_ingredients: string;
  tags: string;
  price_usd: number;
  margin_percent: number;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
  category: string;
  marginRank?: number;
  inStock: boolean;
  tags?: string[];
  ingredients?: string[];
}

// Product Response Type
export interface ProductsResponse {
  products: BackendProduct[];
  count: number;
  timestamp: number;
}

// Citation Types
export interface Citation {
  id: string;
  snippet: string;
  text?: string;    // For backward compatibility
  url?: string;     // For backward compatibility
  source?: string;  // For backward compatibility
}

// API Response Types
export interface AssistResponse {
  text: string;
  products: BackendProduct[];
  citations: Citation[];
  latency_ms: number;
  session_id?: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
}

// API Request Types
export interface AssistRequest {
  session_id?: string;
  message: string;
}

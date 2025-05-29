import { useState } from 'react';
import type { Product } from '../../types';

interface ProductCardProps {
  product: Product;
}

const ProductCard = ({ product }: ProductCardProps) => {
  const [isHovered, setIsHovered] = useState(false);
  
  // Default image if none provided
  const imageUrl = product.imageUrl || 'https://via.placeholder.com/300x300?text=No+Image';
  
  return (
    <div 
      className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-lg relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Product Image */}
      <div className="aspect-square overflow-hidden">
        <img 
          src={imageUrl} 
          alt={product.name} 
          className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
        />
      </div>
      
      {/* Product Info */}
      <div className="p-4">
        <h3 className="text-lg font-medium text-text-primary dark:text-white truncate">
          {product.name}
        </h3>
        
        <p className="text-text-secondary dark:text-gray-300 text-sm mt-1 line-clamp-2">
          {product.description}
        </p>
        
        <div className="mt-3 flex justify-between items-center">
          <span className="text-lg font-bold text-primary dark:text-primary">
            ${product.price.toFixed(2)}
          </span>
          
          {product.inStock ? (
            <span className="text-xs px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
              In Stock
            </span>
          ) : (
            <span className="text-xs px-2 py-1 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded-full">
              Out of Stock
            </span>
          )}
        </div>
      </div>
      
      {/* Hover Details */}
      {isHovered && (
        <div className="absolute inset-0 bg-black bg-opacity-75 flex flex-col justify-center items-center p-4 text-white opacity-0 hover:opacity-100 transition-opacity duration-300">
          <h3 className="text-lg font-medium mb-2">{product.name}</h3>
          <p className="text-sm text-center mb-3">{product.description}</p>
          
          {product.tags && product.tags.length > 0 && (
            <div className="flex flex-wrap justify-center gap-1 mt-2">
              {product.tags.map((tag, index) => (
                <span 
                  key={index} 
                  className="text-xs px-2 py-1 bg-primary bg-opacity-30 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
          
          <button className="mt-4 px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors">
            View Details
          </button>
        </div>
      )}
    </div>
  );
};

export default ProductCard;

import { useProductStore } from '../../store/productStore';
import ProductCard from './ProductCard';

const ProductGrid = () => {
  const { products, isLoading, error } = useProductStore();
  
  // Enhanced loading state with skeleton cards and loading indicator
  const renderSkeletonCards = () => {
    return Array(6).fill(0).map((_, index) => (
      <div key={index} className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="aspect-square bg-gray-200 dark:bg-gray-700 animate-pulse relative">
          {/* Shimmer effect */}
          <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
        </div>
        <div className="p-4">
          <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2 relative overflow-hidden">
            <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
          </div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-3/4 mb-3 relative overflow-hidden">
            <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
          </div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-1/2 mb-2 relative overflow-hidden">
            <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
          </div>
          <div className="mt-3 flex justify-between items-center">
            <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-1/4 relative overflow-hidden">
              <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
            </div>
            <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-1/4 relative overflow-hidden">
              <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
            </div>
          </div>
        </div>
      </div>
    ));
  };
  
  // Main loading indicator
  const renderLoadingIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      <div className="relative">
        <div className="h-12 w-12 rounded-full border-t-4 border-b-4 border-primary animate-spin"></div>
        <div className="absolute top-0 left-0 h-12 w-12 rounded-full border-t-4 border-b-4 border-primary animate-ping opacity-20"></div>
      </div>
      <span className="ml-3 text-lg font-medium text-primary">Loading products...</span>
    </div>
  );
  
  return (
    <div className="mt-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-text-primary dark:text-white">
          {isLoading ? 'Discovering Products' : `Products ${products.length > 0 ? `(${products.length})` : ''}`}
        </h2>
        <div className="w-16 h-1 bg-primary mx-auto mt-2 rounded-full"></div>
      </div>
      
      {isLoading && renderLoadingIndicator()}
      
      {!error && products.length === 0 && !isLoading && (
        <div className="bg-gray-50 dark:bg-gray-800 p-8 rounded-lg text-center">
          <p className="text-text-secondary dark:text-gray-400">
            No products to display. Try searching for something specific.
          </p>
        </div>
      )}
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {isLoading ? renderSkeletonCards() : products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
};

export default ProductGrid;

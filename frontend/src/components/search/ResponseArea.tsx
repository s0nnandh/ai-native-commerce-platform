import { useConversationStore } from '../../store/conversationStore';

interface ResponseAreaProps {
  compact?: boolean;
}

const ResponseArea = ({ compact = false }: ResponseAreaProps) => {
  const { displayedResponse, isLoading, isStreaming, error } = useConversationStore();
  
  // If there's no response yet, don't render anything
  if (!displayedResponse && !isLoading && !isStreaming && !error) {
    return null;
  }
  
  // Enhanced loading animation - compact version for sticky header
  const renderLoader = () => {
    if (compact) {
      return (
        <div className="flex items-center justify-center py-2">
          <div className="relative w-8 h-8 mr-3">
            <div className="absolute inset-0 border-2 border-primary/30 rounded-full"></div>
            <div className="absolute inset-0 border-2 border-transparent border-t-primary rounded-full animate-spin"></div>
          </div>
          <div className="flex items-center text-sm text-primary dark:text-primary-light">
            <span>Thinking</span>
            <span className="inline-flex space-x-1">
              <span className="animate-bounce" style={{ animationDelay: '0ms' }}>.</span>
              <span className="animate-bounce" style={{ animationDelay: '150ms' }}>.</span>
              <span className="animate-bounce" style={{ animationDelay: '300ms' }}>.</span>
            </span>
          </div>
        </div>
      );
    }
    
    return (
      <div className="flex flex-col items-center justify-center py-6">
        <div className="relative w-16 h-16 mb-4">
          {/* Outer circle */}
          <div className="absolute inset-0 border-4 border-primary/30 rounded-full"></div>
          {/* Spinning circle */}
          <div className="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"></div>
          {/* Inner dot */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-2 h-2 bg-primary rounded-full"></div>
          </div>
        </div>
        
        {/* Text loading animation */}
        <div className="flex items-center space-x-2 text-primary dark:text-primary-light">
          <span>Thinking</span>
          <span className="inline-flex space-x-1">
            <span className="animate-bounce" style={{ animationDelay: '0ms' }}>.</span>
            <span className="animate-bounce" style={{ animationDelay: '150ms' }}>.</span>
            <span className="animate-bounce" style={{ animationDelay: '300ms' }}>.</span>
          </span>
        </div>
        
        {/* Skeleton content */}
        <div className="animate-pulse flex space-x-4 w-full mt-6">
          <div className="flex-1 space-y-4 py-1">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  // Render response content - different styling for compact mode
  const renderResponseContent = () => {
    if (compact) {
      return (
        <div className="text-center py-2">
          <p className="text-sm font-medium text-primary dark:text-primary-light">
            {displayedResponse}
            {isStreaming && (
              <span className="inline-block w-1.5 h-4 ml-1 bg-primary animate-pulse"></span>
            )}
          </p>
        </div>
      );
    }
    
    return (
      <div className="text-center mb-8">
        <h2 className="text-xl md:text-2xl font-semibold text-primary dark:text-primary-light mb-2">
          {displayedResponse}
          {isStreaming && (
            <span className="inline-block w-2 h-5 ml-1 bg-primary animate-pulse"></span>
          )}
        </h2>
        <div className="w-16 h-1 bg-primary mx-auto mt-2 rounded-full"></div>
      </div>
    );
  };
  
  return (
    <div className={`w-full ${!compact ? 'max-w-3xl mx-auto mt-6' : ''}`}>
      {isLoading ? renderLoader() : renderResponseContent()}
    </div>
  );
};

export default ResponseArea;

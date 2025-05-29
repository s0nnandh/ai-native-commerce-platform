import { useConversationStore } from '../../store/conversationStore';

const ResponseArea = () => {
  const { displayedResponse, isLoading, isStreaming, error } = useConversationStore();
  
  // If there's no response yet, don't render anything
  if (!displayedResponse && !isLoading && !isStreaming && !error) {
    return null;
  }
  
  return (
    <div className="w-full max-w-3xl mx-auto mt-6">
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-4">
          <div className="animate-pulse flex space-x-4 w-full">
            <div className="flex-1 space-y-4 py-1">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
              </div>
            </div>
          </div>
          <p className="text-text-secondary dark:text-gray-400 mt-4">Generating response...</p>
        </div>
      ) : (
        <div className="text-center mb-8">
          <h2 className="text-xl md:text-2xl font-semibold text-primary dark:text-primary-light mb-2">
            {displayedResponse}
            {isStreaming && (
              <span className="inline-block w-2 h-5 ml-1 bg-primary animate-pulse"></span>
            )}
          </h2>
          <div className="w-16 h-1 bg-primary mx-auto mt-2 rounded-full"></div>
        </div>
      )}
    </div>
  );
};

export default ResponseArea;

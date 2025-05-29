import type { FormEvent } from 'react';
import { useConversationStore } from '../../store/conversationStore';

const SearchBar = () => {
  const { userMessage, setUserMessage, submitMessage, isLoading, isStreaming } = useConversationStore();
  
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!userMessage.trim() || isLoading || isStreaming) return;
    
    try {
      // Submit message to the API
      await submitMessage(userMessage);
      
      // Note: product updates are now handled in the conversation store
    } catch (error) {
      console.error('Error submitting message:', error);
    }
  };
  
  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          placeholder="Ask about products, categories, or recommendations..."
          className="w-full py-4 pl-5 pr-16 text-lg rounded-full shadow-lg focus:ring-2 focus:ring-primary focus:ring-opacity-50 border-none dark:bg-gray-800 dark:text-white transition-all duration-300"
          disabled={isLoading || isStreaming}
          aria-label="Search input"
        />
        <button
          type="submit"
          className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-3 rounded-full text-white shadow-md ${
            isLoading || isStreaming 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-primary hover:bg-primary-dark transition-colors'
          }`}
          disabled={isLoading || isStreaming || !userMessage.trim()}
          aria-label="Search"
        >
          {isLoading ? (
            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          )}
        </button>
      </form>
    </div>
  );
};

export default SearchBar;

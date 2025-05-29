import { useEffect } from 'react';
import { useUIStore } from '../../store/uiStore';
import SearchBar from './SearchBar';
import ResponseArea from './ResponseArea';
import { useConversationStore } from '../../store/conversationStore';

const StickySearchHeader = () => {
  const { showStickyHeader, setScrollState, setShowStickyHeader } = useUIStore();
  const { displayedResponse, isLoading, isStreaming } = useConversationStore();
  
  useEffect(() => {
    const handleScroll = () => {
      // Check if we've scrolled past the search section (approximately 800px)
      const scrollPosition = window.scrollY;
      const scrollThreshold = 1200;
      
      // Update scroll state
      setScrollState(scrollPosition > 100);
      
      // Show sticky header when scrolled past the search section
      // Hide it when scrolled back to the top
      if (scrollPosition > scrollThreshold && !showStickyHeader) {
        setShowStickyHeader(true);
      } else if (scrollPosition <= scrollThreshold && showStickyHeader) {
        setShowStickyHeader(false);
      }
    };
    
    // Add scroll event listener
    window.addEventListener('scroll', handleScroll);
    
    // Clean up
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [showStickyHeader, setScrollState, setShowStickyHeader]);
  
  // Determine if we should show the response area in the sticky header
  const showResponseInHeader = showStickyHeader && (displayedResponse || isLoading || isStreaming);
  
  return (
    <div 
      className={`fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-800 shadow-md transition-transform duration-300 ${
        showStickyHeader ? 'translate-y-0' : '-translate-y-full'
      }`}
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.083 9h1.946c.089-1.546.383-2.97.837-4.118A6.004 6.004 0 004.083 9zM10 2a8 8 0 100 16 8 8 0 000-16zm0 2c-.076 0-.232.032-.465.262-.238.234-.497.623-.737 1.182-.389.907-.673 2.142-.766 3.556h3.936c-.093-1.414-.377-2.649-.766-3.556-.24-.56-.5-.948-.737-1.182C10.232 4.032 10.076 4 10 4zm3.971 5c-.089-1.546-.383-2.97-.837-4.118A6.004 6.004 0 0115.917 9h-1.946zm-2.003 2H8.032c.093 1.414.377 2.649.766 3.556.24.56.5.948.737 1.182.233.23.389.262.465.262.076 0 .232-.032.465-.262.238-.234.498-.623.737-1.182.389-.907.673-2.142.766-3.556zm1.166 4.118c.454-1.147.748-2.572.837-4.118h1.946a6.004 6.004 0 01-2.783 4.118zm-6.268 0C6.412 13.97 6.118 12.546 6.03 11H4.083a6.004 6.004 0 002.783 4.118z" clipRule="evenodd" />
              </svg>
            </div>
            <h1 className="text-lg font-bold text-primary dark:text-white">
              EverGlow Labs
            </h1>
          </div>
          
          <div className="flex-grow mx-4">
            <SearchBar />
          </div>
        </div>
        
        {/* Compact Response Area in sticky header */}
        {showResponseInHeader && (
          <div className="mt-2 max-h-20 overflow-y-auto">
            <ResponseArea compact={true} />
          </div>
        )}
      </div>
    </div>
  );
};

export default StickySearchHeader;

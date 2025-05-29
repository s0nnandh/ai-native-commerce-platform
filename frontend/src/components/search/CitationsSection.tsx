import { useState } from 'react';
import { useConversationStore } from '../../store/conversationStore';
import type { Citation } from '../../types';

const CitationCard = ({ citation }: { citation: Citation }) => {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div 
      className="relative bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-3 transition-all duration-200 hover:shadow-md"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Citation Icon */}
      <div className="flex items-center mb-2">
        <span className="w-5 h-5 mr-2 text-primary">
          {citation.url ? (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
            </svg>
          )}
        </span>
        <span className="font-medium text-sm truncate">
          {citation.id}
        </span>
      </div>
      
      {/* Preview Text */}
      <p className="text-xs text-gray-600 dark:text-gray-300 line-clamp-2">
        {citation.snippet}
      </p>
      
      {/* Hover Popup */}
      {isHovered && (
        <div className="absolute z-10 bottom-full left-0 mb-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4 transition-all duration-200">
          <h4 className="font-medium text-sm mb-2">Citation #{citation.id}</h4>
          <p className="text-xs text-gray-600 dark:text-gray-300 mb-2">{citation.snippet}</p>
          {citation.url && (
            <a 
              href={citation.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-primary hover:underline text-xs flex items-center"
            >
              <span className="mr-1">View Source</span>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          )}
        </div>
      )}
    </div>
  );
};

const CitationsSection = () => {
  const { citations, isLoading, isStreaming } = useConversationStore();
  
  // If there are no citations or still loading/streaming, don't render anything
  if (citations.length === 0 || (isLoading && !isStreaming)) {
    return null;
  }

  // print citations
  console.log(citations);
  
  
  // Show skeleton loader during streaming
  if (isStreaming) {
    return (
      <div className="w-full max-w-3xl mx-auto mt-6 mb-6">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 text-center">Sources</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {[1, 2, 3].map((index) => (
            <div 
              key={index} 
              className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-3 animate-pulse"
            >
              <div className="flex items-center mb-2">
                <div className="w-5 h-5 mr-2 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full mb-1"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }
  
  return (
    <div className="w-full max-w-3xl mx-auto mt-6 mb-6">
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 text-center">Sources</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {citations.map((citation: Citation, index: number) => (
          <CitationCard key={index} citation={citation} />
        ))}
      </div>
    </div>
  );
};

export default CitationsSection;

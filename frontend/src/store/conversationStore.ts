import { create } from 'zustand';
import type { Citation } from '../types';
import { assistApi } from '../api/assistApi';
import { getMockResponse } from '../utils/mockData';
import { useProductStore } from './productStore';
import { v4 as uuidv4 } from 'uuid';

// Set this to false to use the real API instead of mock data
const USE_MOCK_DATA = false;

// Configuration for streaming effect
const STREAMING_DELAY_MS = 15; // Delay between characters for streaming effect

// Ensure session ID exists
const ensureSessionId = (): string => {
  let sessionId = localStorage.getItem('sessionId');
  if (!sessionId) {
    sessionId = uuidv4();
    localStorage.setItem('sessionId', sessionId);
  }
  return sessionId;
};

// Initialize session ID on app load
ensureSessionId();

interface ConversationState {
  userMessage: string;
  aiResponse: string;
  displayedResponse: string; // For streaming effect
  citations: Citation[];
  isLoading: boolean;
  isStreaming: boolean; // Flag for streaming state
  error: string | null; // Still track errors internally but don't show in UI
  
  // Actions
  setUserMessage: (message: string) => void;
  submitMessage: (message: string) => Promise<any>;
  clearConversation: () => void;
}

export const useConversationStore = create<ConversationState>((set) => ({
  userMessage: '',
  aiResponse: 'Hey, How can i help you',
  displayedResponse: 'Hey, How can i help you',
  citations: [],
  isLoading: false,
  isStreaming: false,
  error: null, // Not shown in UI
  
  setUserMessage: (message) => set({ userMessage: message }),
  
  submitMessage: async (message) => {
    try {
      set({ isLoading: true, error: null });
      
      // Store the user message
      set({ userMessage: message });
      
      let response;
      
      if (USE_MOCK_DATA) {
        // Use mock data
        response = await getMockResponse(message);
      } else {
        // Call the real API
        response = await assistApi.sendMessage({
          message,
          session_id: localStorage.getItem('sessionId') || undefined,
        });
        
        // Store the session ID if it's the first message
        if (!localStorage.getItem('sessionId') && response.session_id) {
          localStorage.setItem('sessionId', response.session_id);
        }
      }
      
      // Update the state with the response
      set({
        aiResponse: response.text,
        displayedResponse: '', // Start with empty displayed response for streaming effect
        citations: response.citations || [],
        isLoading: false,
        isStreaming: true, // Start streaming
        userMessage: '', // Clear the input field
      });
      
      // Get the product store to update products
      const productStore = useProductStore.getState();
      
      // If the response has products, update the product store
      if (response.products && response.products.length > 0) {
        productStore.updateProductsByResponse(response.products);
      } else {
        // If no products in response, fetch all products
        productStore.loadAllProducts();
      }
      
      // Simulate streaming effect
      const fullResponse = response.text;
      let currentIndex = 0;
      
      const streamText = () => {
        if (currentIndex < fullResponse.length) {
          const nextChar = fullResponse.charAt(currentIndex);
          set(state => ({ 
            displayedResponse: state.displayedResponse + nextChar 
          }));
          currentIndex++;
          setTimeout(streamText, STREAMING_DELAY_MS);
        } else {
          // Streaming complete
          set({ isStreaming: false });
        }
      };
      
      // Start streaming
      streamText();
      
      return response;
    } catch (error) {
      console.error('Error submitting message:', error);
      set({
        error: error instanceof Error ? error.message : 'An unknown error occurred',
        isLoading: false,
        isStreaming: false,
      });
      throw error;
    }
  },
  
  clearConversation: () => {
    // Clear the conversation state and session ID
    localStorage.removeItem('sessionId');
    set({
      userMessage: '',
      aiResponse: 'Hey, How can i help you',
      displayedResponse: 'Hey, How can i help you',
      citations: [],
      isStreaming: false,
      error: null,
    });
  },
}));

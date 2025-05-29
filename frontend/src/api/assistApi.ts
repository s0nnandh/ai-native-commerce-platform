import apiClient from './client';
import { API_CONFIG } from './config';
import type { AssistRequest, AssistResponse } from '../types';

// API service for the assist endpoint
export const assistApi = {
  /**
   * Send a message to the assist endpoint
   * @param request The assist request
   * @returns Promise with the assist response
   */
  sendMessage: async (request: AssistRequest): Promise<AssistResponse> => {
    try {
      const response = await apiClient.post<AssistResponse>(
        API_CONFIG.ENDPOINTS.ASSIST,
        request
      );
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  /**
   * Check the health of the API
   * @returns Promise with the health status
   */
  checkHealth: async (): Promise<{ status: string; timestamp: number }> => {
    try {
      const response = await apiClient.get(API_CONFIG.ENDPOINTS.HEALTH);
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  },
};

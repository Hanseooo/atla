import api from './api';
import type { 
  ChatRequest, 
  ChatResponse, 
  ChatSession, 
  ItineraryResponse 
} from '../types/chat';

/**
 * Chat API Client
 * 
 * This module acts as the bridge between the frontend UI and the backend AI endpoints.
 * It handles sending messages, answering clarification questions, and fetching the 
 * finalized itinerary data.
 */
export const chatApi = {
  /**
   * Sends the user's initial message to the AI.
   * The backend will return either a ClarificationResponse (if info is missing)
   * or an ItineraryResponse (if the intent is fully populated).
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/api/chat/', request);
    return response.data;
  },

  /**
   * Submits the user's answer to a specific clarification question.
   * e.g., passing { budget: "low" } back to the active session.
   */
  async submitClarification(sessionId: string, answers: Record<string, unknown>): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>(`/api/chat/${sessionId}/clarify`, answers);
    return response.data;
  },

  /**
   * Manually triggers the generation of the final itinerary.
   * Usually called once all clarification questions have been answered.
   */
  async generateItinerary(sessionId: string): Promise<ItineraryResponse> {
    const response = await api.post<ItineraryResponse>(`/api/chat/${sessionId}/generate-itinerary`);
    return response.data;
  },

  /**
   * Fetches the current state/history of a specific chat session.
   * Useful for restoring a chat if the user refreshes the page.
   */
  async getSession(sessionId: string): Promise<ChatSession> {
    const response = await api.get<ChatSession>(`/api/chat/${sessionId}`);
    return response.data;
  }
};


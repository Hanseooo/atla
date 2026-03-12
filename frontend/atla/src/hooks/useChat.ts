import { useMutation, useQuery } from '@tanstack/react-query';
import { chatApi } from '../lib/chat-api';
import type { 
  ChatRequest, 
  ChatResponse, 
  ChatSession, 
  ItineraryResponse 
} from '../types/chat';

/**
 * Query Keys
 * 
 * Centralized query keys for TanStack Query to ensure cache consistency.
 * Used for invalidating or fetching specific chat sessions.
 */
export const chatKeys = {
  all: ['chat'] as const,
  session: (sessionId: string) => [...chatKeys.all, 'session', sessionId] as const,
};

/**
 * Hook to fetch an existing chat session from the backend.
 * Automatically disabled if no sessionId is provided.
 */
export function useChatSession(sessionId?: string | null) {
  return useQuery<ChatSession>({
    queryKey: chatKeys.session(sessionId!),
    queryFn: () => chatApi.getSession(sessionId!),
    enabled: !!sessionId,
    retry: false, // Don't retry on 404s if session doesn't exist
  });
}

/**
 * Hook to send a new message to the AI.
 * Handles the loading (isPending) and error states automatically during the fetch.
 */
export function useSendMessage() {
  return useMutation<ChatResponse, Error, ChatRequest>({
    mutationFn: (request) => chatApi.sendMessage(request),
  });
}

/**
 * Hook to submit answers to clarification questions.
 * Passes the specific session ID and the key-value pair of the answered question.
 */
export function useSubmitClarification() {
  return useMutation<
    ChatResponse,
    Error,
    { sessionId: string; answers: Record<string, unknown> }
  >({
    mutationFn: ({ sessionId, answers }) => chatApi.submitClarification(sessionId, answers),
  });
}

/**
 * Hook to manually trigger the final itinerary generation.
 */
export function useGenerateItinerary() {
  return useMutation<ItineraryResponse, Error, string>({
    mutationFn: (sessionId) => chatApi.generateItinerary(sessionId),
  });
}

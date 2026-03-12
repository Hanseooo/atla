import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ChatResponse } from "../types/chat";

/**
 * Interface representing a single message bubble in the chat UI.
 * The data property stores the raw backend response so we can render
 * interactive elements (like clarification questions or itinerary cards).
 */
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  data?: ChatResponse;
}

/**
 * Zustand store for managing the local chat state.
 * This keeps track of the conversation history and the current sessionId
 * without needing to pass props down through the entire component tree.
 */
interface ChatState {
  // States
  sessionId: string | null;
  messages: ChatMessage[];

  // Actions
  setSessionId: (id: string | null) => void;
  addMessage: (message: Omit<ChatMessage, "id">) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>()(
  // The persist middleware automatically saves this store's state to localStorage
  // This ensures the user's chat history and active session survive page reloads
  persist(
    (set) => ({
      // Initial states
      sessionId: null,
      messages: [],

      // Actions
      setSessionId: (id) => set({ sessionId: id }),
      addMessage: (msg) =>
        set((state) => ({
          messages: [
            ...state.messages,
            { ...msg, id: Math.random().toString(36).substring(7) },
          ],
        })),
      clearMessages: () => set({ messages: [], sessionId: null }),
    }),
    {
      name: "chat-session-storage",
    }
  )
);

import { useEffect, useRef } from 'react';
import { useChatStore } from '../../stores/chatStore';
import { isClarificationResponse, isItineraryResponse } from '../../types/chat';
import { ClarificationOptions } from './ClarificationOptions';
import { ItinerarySummaryCard } from './ItinerarySummaryCard';
import { Alert, AlertDescription } from '../ui/alert';

interface MessageListProps {
  isPending: boolean;
  error?: string | null;
  onAnswerQuestion: (field: string, answer: unknown) => void;
}

export function MessageList({ isPending, error, onAnswerQuestion }: MessageListProps) {
  const messages = useChatStore((state) => state.messages);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isPending]);

  return (
    <div className="flex-1 overflow-y-auto space-y-4 p-4" ref={scrollRef}>
      {messages.length === 0 ? (
        <div className="text-center text-muted-foreground py-8">
          <p>Try saying:</p>
          <p className="mt-2">"I want to visit Palawan for 3 days"</p>
        </div>
      ) : (
        messages.map((msg, i) => {
          const isClarification = msg.data && isClarificationResponse(msg.data);
          const isItinerary = msg.data && isItineraryResponse(msg.data);
          // Check if this is the latest assistant message (to avoid re-rendering old buttons)
          const isLatestAssistant = i === messages.length - 1 && msg.role === 'assistant';

          return (
            <div key={i} className="flex flex-col gap-2">
              <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[90%] md:max-w-[80%] rounded-lg px-4 py-2 whitespace-pre-wrap text-sm md:text-base ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  {msg.content}
                </div>
              </div>

              {/* Render Clarification Options */}
              {isClarification && isLatestAssistant && msg?.data?.type === 'clarification' && (
                <ClarificationOptions
                  data={msg.data}
                  isPending={isPending}
                  onAnswer={onAnswerQuestion}
                />
              )}

              {/* Render Itinerary Summary */}
              {isItinerary && msg?.data?.type === 'itinerary' && (
                <ItinerarySummaryCard data={msg.data} />
              )}
            </div>
          );
        })
      )}

      {isPending && (
        <div className="flex justify-start">
          <div className="max-w-[80%] rounded-lg px-4 py-2 bg-muted text-muted-foreground animate-pulse">
            AI is thinking...
          </div>
        </div>
      )}

      {error && (
        <Alert variant="destructive" className="mt-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
}

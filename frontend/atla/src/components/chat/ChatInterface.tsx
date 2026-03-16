import { useEffect } from 'react';
import { useSendMessage, useSubmitClarification, useChatSession } from '../../hooks/useChat';
import { useChatStore } from '../../stores/chatStore';
import { getErrorMessage } from '../../lib/api';
import type { ChatResponse } from '../../types/chat';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { Button } from '../ui/button';
import { RefreshCcw } from 'lucide-react';

export function ChatInterface() {
  const { addMessage, sessionId, setSessionId, clearMessages, messages } = useChatStore();

  // Use the session query to verify if the backend still remembers this session
  const { 
    isError: isSessionError, 
    isFetching: isFetchingSession 
  } = useChatSession(sessionId);

  // If the backend session doesn't exist (example: server restarted), wipe the local storage and start fresh
  useEffect(() => {
    if (isSessionError) {
      clearMessages();
      addMessage({
        role: 'assistant',
        content: "Oops! It looks like your previous session expired. Let's start a brand new plan! Where would you like to go?"
      });
    }
  }, [isSessionError, clearMessages, addMessage]);

  const sendMessageMutation = useSendMessage();
  const submitClarificationMutation = useSubmitClarification();

  const handleResetSession = () => {
    if (window.confirm("Are you sure you want to start a new trip plan? This will clear your current conversation.")) {
      clearMessages();
    }
  };

  const formatAnswer = (answer: unknown): string => {
    if (typeof answer === 'string') return answer;
    if (typeof answer === 'number' || typeof answer === 'boolean') return String(answer);
    if (Array.isArray(answer)) return answer.join(', ');
    if (answer && typeof answer === 'object') return JSON.stringify(answer);
    return 'Provided answer';
  };

  const handleProcessResponse = (response: ChatResponse) => {
    if (response.type !== 'error' && response.session_id && response.session_id !== sessionId) {
      setSessionId(response.session_id);
    }

    if (response.type === 'error') {
      addMessage({ role: 'assistant', content: `Error: ${response.message}` });
    } else {
      addMessage({ role: 'assistant', content: response.message, data: response });
    }
  };

  const handleSend = async (userMessage: string) => {
    addMessage({ role: 'user', content: userMessage });

    try {
      const response = await sendMessageMutation.mutateAsync({
        message: userMessage,
        session_id: sessionId || undefined,
      });
      handleProcessResponse(response);
    } catch (error: unknown) {
      addMessage({ role: 'assistant', content: `Sorry, an error occurred: ${getErrorMessage(error)}` });  
    }
  };

  const handleAnswerQuestion = async (field: string, answer: unknown) => {
    if (!sessionId) return;

    addMessage({ role: 'user', content: formatAnswer(answer) });

    try {
      const response = await submitClarificationMutation.mutateAsync({
        sessionId,
        answers: { [field]: answer },
      });
      handleProcessResponse(response);
    } catch (error: unknown) {
      addMessage({ role: 'assistant', content: `Sorry, an error occurred: ${getErrorMessage(error)}` });  
    }
  };

  const isPending = sendMessageMutation.isPending || submitClarificationMutation.isPending || isFetchingSession;
  const error = (sendMessageMutation.isError || submitClarificationMutation.isError)
    ? getErrorMessage(sendMessageMutation.error ?? submitClarificationMutation.error)
    : null;

  return (
    <>
      {/* Temporary place of Start New Plan btn until we have a finalized UI/UX design for session management */}
      {messages.length > 0 && (
        <div className="absolute top-4 right-4 z-20">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleResetSession}
            className="text-muted-foreground hover:text-destructive text-xs flex items-center gap-1.5"
          >
            <RefreshCcw className="w-3.5 h-3.5" />
            Start New Plan
          </Button>
        </div>
      )}

      <MessageList
        isPending={isPending} 
        error={error}
        onAnswerQuestion={handleAnswerQuestion}
      />
      <ChatInput
        onSend={handleSend}
        isPending={isPending}
      />
    </>
  );
}

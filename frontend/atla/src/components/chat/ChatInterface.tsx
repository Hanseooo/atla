import { useSendMessage, useSubmitClarification } from '../../hooks/useChat';
import { useChatStore } from '../../stores/chatStore';
import { getErrorMessage } from '../../lib/api';
import type { ChatResponse } from '../../types/chat';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

export function ChatInterface() {
  const { addMessage, sessionId, setSessionId } = useChatStore();
  
  const sendMessageMutation = useSendMessage();
  const submitClarificationMutation = useSubmitClarification();

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

  const isPending = sendMessageMutation.isPending || submitClarificationMutation.isPending;
  const error = (sendMessageMutation.isError || submitClarificationMutation.isError) 
    ? getErrorMessage(sendMessageMutation.error ?? submitClarificationMutation.error) 
    : null;

  return (
    <>
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

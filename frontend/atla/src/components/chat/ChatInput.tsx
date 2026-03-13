import { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';

interface ChatInputProps {
  onSend: (message: string) => void;
  isPending: boolean;
}

export function ChatInput({ onSend, isPending }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim() || isPending) return;
    
    onSend(input.trim());
    setInput('');
  };

  return (
    <div className="p-4 border-t mt-auto">
      <div className="flex gap-2">
        <Input
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          disabled={isPending}
        />
        <Button 
          onClick={handleSend}
          disabled={isPending || !input.trim()}
        >
          Send
        </Button>
      </div>
    </div>
  );
}

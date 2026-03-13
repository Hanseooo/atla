import { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import type { ClarificationQuestion } from '../../types/chat';
import { Check } from 'lucide-react';

interface ClarificationCardProps {
  question: ClarificationQuestion;
  onAnswer: (field: string, answer: unknown) => void;
  disabled: boolean;
}

export function ClarificationCard({ question, onAnswer, disabled }: ClarificationCardProps) {
  const [textValue, setTextValue] = useState('');
  const [multiSelect, setMultiSelect] = useState<string[]>([]);

  const toggleMultiSelect = (id: string) => {
    setMultiSelect((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleMultiSubmit = () => {
    if (multiSelect.length > 0) {
      onAnswer(question.field, multiSelect);
    }
  };

  const handleTextSubmit = () => {
    if (textValue.trim()) {
      onAnswer(question.field, textValue.trim());
    }
  };

  return (
    <div className="bg-card border rounded-lg p-4 w-full max-w-[95%] md:max-w-[80%] shadow-sm">
      <p className="font-medium mb-3">{question.question}</p>

      {question.type === 'single_choice' && question.options && (
        <div className="flex flex-wrap gap-2">
          {question.options.map((opt) => (
            <Button
              key={opt.id}
              variant="outline"
              size="sm"
              onClick={() => onAnswer(question.field, opt.id)}
              disabled={disabled}
            >
              {opt.label}
            </Button>
          ))}
        </div>
      )}

      {question.type === 'multiple_choice' && question.options && (
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {question.options.map((opt) => {
              const isSelected = multiSelect.includes(opt.id);
              return (
                <Button
                  key={opt.id}
                  variant={isSelected ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => toggleMultiSelect(opt.id)}
                  disabled={disabled}
                  className="flex items-center gap-1.5"
                >
                  {isSelected && <Check className="w-3.5 h-3.5" />}
                  {opt.label}
                </Button>
              );
            })}
          </div>
          <Button
            size="sm"
            onClick={handleMultiSubmit}
            disabled={disabled || multiSelect.length === 0}
            className="w-full sm:w-auto"
          >
            Submit Selection
          </Button>
        </div>
      )}

      {question.type === 'text' && (
        <div className="flex gap-2">
          <Input
            placeholder={question.placeholder || 'Type your answer...'}
            value={textValue}
            onChange={(e) => setTextValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleTextSubmit()}
            disabled={disabled}
          />
          <Button size="sm" onClick={handleTextSubmit} disabled={disabled || !textValue.trim()}>
            Submit
          </Button>
        </div>
      )}

      {question.type === 'date' && (
        <div className="flex gap-2">
          <Input
            type="date"
            value={textValue}
            onChange={(e) => setTextValue(e.target.value)}
            disabled={disabled}
          />
          <Button size="sm" onClick={handleTextSubmit} disabled={disabled || !textValue}>
            Submit
          </Button>
        </div>
      )}
    </div>
  );
}

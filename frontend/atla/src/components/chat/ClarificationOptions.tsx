import { type ClarificationResponse } from '../../types/chat';
import { ClarificationCard } from './ClarificationCard';

interface ClarificationOptionsProps {
  data: ClarificationResponse;
  isPending: boolean;
  onAnswer: (field: string, answer: unknown) => void;
}

export function ClarificationOptions({ data, isPending, onAnswer }: ClarificationOptionsProps) {
  if (!data.questions || data.questions.length === 0) return null;

  return (
    <div className="flex flex-col items-start gap-3 mt-2 ml-4">
      {/* Progress Bar */}
      {data.progress && (
        <div className="w-full max-w-[80%] space-y-1">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Planning Progress</span>
            <span>
              {data.progress.completed} of {data.progress.total} details
            </span>
          </div>
          <div className="w-full bg-secondary h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-primary h-full transition-all duration-500 ease-in-out"
              style={{ width: `${data.progress.percentage}%` }}
            />
          </div>
        </div>
      )}

      {data.questions.map((question) => (
        <ClarificationCard
          key={question.id}
          question={question}
          onAnswer={onAnswer}
          disabled={isPending}
        />
      ))}
    </div>
  );
}

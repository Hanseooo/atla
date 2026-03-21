import { type TripDayData } from '../../types/chat';
import { type TripDay } from '../../types/trip';
import { ActivityTimelineItem } from './ActivityTimelineItem';
import { Coffee, UtensilsCrossed, Moon } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

interface TripDayTimelineProps {
  dayData: TripDayData | TripDay;
  startDate?: Date;
}

export function TripDayTimeline({ dayData, startDate }: TripDayTimelineProps) {
  // Calculate the actual date if a start date is provided using native Intl API
  let actualDate = `Day ${dayData.day_number}`;

  if (startDate) {
    const targetDate = new Date(startDate.getTime() + (dayData.day_number - 1) * 24 * 60 * 60 * 1000);
    actualDate = new Intl.DateTimeFormat('en-US', {
      weekday: 'long',
      month: 'short',
      day: 'numeric'
    }).format(targetDate);
  }

  // Type guards to handle optional properties gracefully
  const meals = 'meals' in dayData ? dayData.meals : undefined;
  const daily_tips = 'daily_tips' in dayData ? dayData.daily_tips : [];

  const cleanTitle = dayData.title.replace(
    /^Day \d+[:-]?\s*/i,
    ""
  );

  return (
    <Card className="border-0 shadow-none bg-transparent py-0">
      <CardHeader className={`px-0 pt-0 pb-4 ${dayData.day_number > 1 && 'border-t'}`}>
        <div className={`flex items-center gap-3 ${dayData.day_number > 0 && 'pt-8'}`}>
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary font-bold">
            {dayData.day_number}
          </div>
          <div>
            <CardTitle className="text-xl">{cleanTitle}</CardTitle>
            <p className="text-sm text-muted-foreground font-medium">{actualDate}</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="px-0 space-y-6">

        {/* Timeline of Activities */}
        <div className="mt-2">
          {dayData.activities.map((activity, index) => (
            <ActivityTimelineItem 
              key={`${dayData.day_number}-${index}`} 
              activity={activity} 
              isLast={index === dayData.activities.length - 1} 
            />
          ))}
        </div>

        {/* Daily Meals Highlights (if provided specifically) */}
        {meals && (Object.keys(meals).length > 0) && (
          <div className="bg-muted/40 rounded-lg p-4 mt-6">
            <h4 className="text-sm font-semibold mb-3 text-foreground/80">Dining Highlights</h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {meals.breakfast && (
                <div className="flex items-start gap-2 text-sm">
                  <Coffee className="h-4 w-4 text-orange-500 mt-0.5" />
                  <div>
                    <span className="font-medium block text-xs uppercase text-muted-foreground">Breakfast</span>
                    <span>{meals.breakfast}</span>
                  </div>
                </div>
              )}
              {meals.lunch && (
                <div className="flex items-start gap-2 text-sm">
                  <UtensilsCrossed className="h-4 w-4 text-green-500 mt-0.5" />
                  <div>
                    <span className="font-medium block text-xs uppercase text-muted-foreground">Lunch</span>    
                    <span>{meals.lunch}</span>
                  </div>
                </div>
              )}
              {meals.dinner && (
                <div className="flex items-start gap-2 text-sm">
                  <Moon className="h-4 w-4 text-indigo-500 mt-0.5" />
                  <div>
                    <span className="font-medium block text-xs uppercase text-muted-foreground">Dinner</span>   
                    <span>{meals.dinner}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Daily Tips */}
        {daily_tips && daily_tips.length > 0 && (
          <div className="bg-blue-50/50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/50 rounded-lg p-4">
            <h4 className="text-sm font-semibold mb-2 text-blue-800 dark:text-blue-300">Daily Tips</h4>
            <ul className="space-y-1.5">
              {daily_tips.map((tip, idx) => (
                <li key={idx} className="text-sm text-blue-900/80 dark:text-blue-200/80 flex items-start gap-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

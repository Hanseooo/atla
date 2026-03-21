import { 
  MapPin, 
  Clock, 
  Wallet, 
  Info,
  Utensils,
  Camera,
  Car,
  Bed,
  Activity as ActivityIcon
} from 'lucide-react';
import { Badge } from '../ui/badge';
import type { ActivityData, ActivityCategory } from '../../types/chat';
import type { Activity } from '../../types/trip';
import { Button } from '../ui/button';

interface ActivityTimelineItemProps {
  activity: ActivityData | Activity;
  isLast?: boolean;
}

const CategoryIcon = ({ category, className }: { category: ActivityCategory | string, className?: string }) => {
  switch (category) {
    case 'restaurant': return <Utensils className={className} />;
    case 'attraction': return <Camera className={className} />;
    case 'transport': return <Car className={className} />;
    case 'accommodation': return <Bed className={className} />;
    default: return <ActivityIcon className={className} />;
  }
};

const getCategoryColor = (category: ActivityCategory | string) => {
  switch (category) {
    case 'restaurant': return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 border-orange-200 dark:border-orange-800';
    case 'attraction': return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800';
    case 'transport': return 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 border-purple-200 dark:border-purple-800';
    case 'accommodation': return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800';
    default: return 'bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-400 border-zinc-200 dark:border-zinc-700';
  }
};

export function ActivityTimelineItem({ activity, isLast }: ActivityTimelineItemProps) {
  // Safe access to properties that might not exist on all types
  const start_time = 'start_time' in activity ? activity.start_time : undefined;
  const duration_minutes = 'duration_minutes' in activity ? activity.duration_minutes : undefined;
  const cost_min = 'cost_min' in activity ? activity.cost_min : undefined;
  const cost_max = 'cost_max' in activity ? activity.cost_max : undefined;
  const notes = 'notes' in activity ? activity.notes : undefined;
  const latitude = 'latitude' in activity ? activity.latitude : undefined;
  const longitude = 'longitude' in activity ? activity.longitude : undefined;

  const formatTime = (timeStr?: string) => {
    if (!timeStr) return null;
    try {
      // Assuming timeStr is HH:MM or ISO string. Let's make it robust using native Intl API
      const date = new Date(`2000-01-01T${timeStr}`);
      return new Intl.DateTimeFormat('en-US', {
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
      }).format(date);
    } catch {
      return timeStr;
    }
  };

  const formatCost = (min?: number, max?: number) => {
    if (min === 0 && max === 0) return 'Free';
    if (!min && !max) return null;
    if (min && !max) return `₱${min.toLocaleString()}`;
    if (!min && max) return `Up to ₱${max.toLocaleString()}`;
    if (min === max) return `₱${min?.toLocaleString()}`;
    return `₱${min?.toLocaleString()} - ₱${max?.toLocaleString()}`;
  };

  const timeString = formatTime(start_time);
  const costString = formatCost(cost_min, cost_max);

  return (
    <div className="relative flex gap-4 pb-6">
      {/* Timeline Line */}
      {!isLast && (
        <div className="absolute left-6 top-10 bottom-0 w-px bg-border -translate-x-1/2" />
      )}

      {/* Icon Circle */}
      <div className={`relative z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border shadow-sm ${getCategoryColor(activity.category)}`}>
        <CategoryIcon category={activity.category} className="h-5 w-5" />
      </div>

      {/* Content */}
      <div className="flex flex-col flex-1 pt-1 space-y-2">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-1">
          <div>
            <h4 className="font-semibold text-base leading-none">{activity.name}</h4>
            <div className="flex flex-wrap items-center gap-2 mt-1.5 text-xs text-muted-foreground">
              {timeString && (
                <div className="flex items-center gap-1 font-medium text-foreground/80">
                  <Clock className="h-3 w-3" />
                  {timeString}
                </div>
              )}
              {duration_minutes && (
                <>
                  <span className="hidden sm:inline text-border">•</span>
                  <span>{duration_minutes} min</span>
                </>
              )}
            </div>
          </div>
          
          {costString && (
            <Badge variant="secondary" className="w-fit shrink-0 bg-background border shadow-sm">
              <Wallet className="h-3 w-3 mr-1" />
              {costString}
            </Badge>
          )}
        </div>

        {activity.description && (
          <p className="text-sm text-muted-foreground leading-relaxed">
            {activity.description}
          </p>
        )}

        {(notes || (latitude && longitude)) && (
          <div className="flex flex-wrap gap-3 mt-2 text-xs">
            {notes && (
              <div className="flex items-start gap-1.5 text-muted-foreground bg-muted/50 p-2 rounded-md flex-1">
                <Info className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                <span>{notes}</span>
              </div>
            )}
            {latitude && longitude && (
              <Button variant="outline" size="sm" className="h-auto py-1 px-2 text-xs" asChild>
                <a href={`https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`} target="_blank" rel="noopener noreferrer">
                  <MapPin className="h-3.5 w-3.5 mr-1" />
                  View Map
                </a>
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

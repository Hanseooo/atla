import { useState } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger
} from '../ui/dialog';
import { Button } from '../ui/button';
import { 
  MapPin, 
  Calendar, 
  Wallet, 
  Users, 
  ArrowRight,
  Sparkles,
  PlaneTakeoff,
  Luggage
} from 'lucide-react';
import type { ItineraryResponse } from '../../types/chat';
import { TripDayTimeline } from '../trips/TripDayTimeline';

interface ItinerarySummaryCardProps {
  data: ItineraryResponse;
}

export function ItinerarySummaryCard({ data }: ItinerarySummaryCardProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="flex flex-col items-start mt-2 ml-4 w-full max-w-[90%]">
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        {/* The Chat Bubble Card */}
        <div className="w-full bg-primary/5 border border-primary/20 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-primary/10">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <MapPin className="h-5 w-5 text-primary" />
              Your Trip to {data.destination}
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              I've put together a complete itinerary based on your preferences!
            </p>
          </div>
          
          <div className="p-4 space-y-4">
            <div className="flex flex-wrap gap-2 text-sm">
              <div className="flex items-center gap-1.5 bg-background px-3 py-1 rounded-full border shadow-sm">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{data.days} Days</span>
              </div>
              {data.budget && (
                <div className="flex items-center gap-1.5 bg-background px-3 py-1 rounded-full border shadow-sm">
                  <Wallet className="h-4 w-4 text-muted-foreground" />
                  <span className="capitalize font-medium">{data.budget}</span>
                </div>
              )}
              {data.companions && (
                <div className="flex items-center gap-1.5 bg-background px-3 py-1 rounded-full border shadow-sm">
                  <Users className="h-4 w-4 text-muted-foreground" />
                  <span className="capitalize font-medium">{data.companions}</span>
                </div>
              )}
            </div>

            <div className="bg-background/80 p-3 rounded-lg border shadow-sm">
              <h4 className="font-semibold text-xs uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1.5">
                <Sparkles className="h-3.5 w-3.5" /> Highlights
              </h4>
              <ul className="space-y-1.5">
                {data.highlights.slice(0, 3).map((highlight: string, idx: number) => (
                  <li key={idx} className="flex items-start gap-2 text-sm">
                    <div className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary flex-shrink-0" />
                    <span className="line-clamp-1">{highlight}</span>
                  </li>
                ))}
                {data.highlights.length > 3 && (
                  <li className="text-xs text-muted-foreground pl-3.5 italic">
                    + {data.highlights.length - 3} more
                  </li>
                )}
              </ul>
            </div>

            {data.estimated_cost && (
              <div className="text-sm font-semibold flex items-center justify-between border-t pt-3 mt-1">
                <span className="text-muted-foreground">Est. Total:</span>
                <span className="text-lg text-primary">
                  {data.estimated_cost.currency || '₱'}
                  {data.estimated_cost.total_min?.toLocaleString()} -{' '}
                  {data.estimated_cost.total_max?.toLocaleString()}
                </span>
              </div>
            )}
          </div>
          
          <div className="p-3 bg-muted/30 border-t">
            <DialogTrigger asChild>
              <Button className="w-full font-semibold shadow-sm" size="lg">
                View Full Itinerary <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </DialogTrigger>
          </div>
        </div>

        {/* The Full Screen Dialog Modal */}
        <DialogContent className="max-w-4xl w-[95vw] md:w-full h-[95vh] md:h-[85vh] p-0 flex flex-col overflow-hidden rounded-xl md:rounded-xl">
          <DialogHeader className="p-4 md:p-6 pb-4 border-b bg-card z-10 shrink-0 text-left">
            <div className="flex items-start justify-between pr-4 md:pr-6">
              <div>
                <DialogTitle className="text-2xl md:text-4xl font-extrabold flex items-center gap-2 mb-2 md:mb-3">
                  <PlaneTakeoff className="h-6 w-6 md:h-8 md:w-8 text-primary" />
                  {data.days} Days in {data.destination}
                </DialogTitle>
                <DialogDescription className="text-sm md:text-base text-foreground/80 leading-relaxed max-w-3xl text-justify hyphens-auto">
                  {data.summary}
                </DialogDescription>
              </div>
            </div>
            
            <div className="flex flex-col md:flex-row md:justify-center items-center gap-2 mt-4 pt-4 border-t border-border/50">
              <div className='flex justify-center items-center gap-2'>
                <div className="flex items-center gap-1.5 bg-muted px-3 py-1.5 rounded-md text-xs md:text-sm font-medium">
                  <Wallet className="h-3.5 w-3.5 md:h-4 md:w-4 text-muted-foreground" />
                  <span className="capitalize">{data.budget} Budget</span>
                </div>
                <div className="flex items-center gap-1.5 bg-muted px-3 py-1.5 rounded-md text-xs md:text-sm font-medium">
                  <Users className="h-3.5 w-3.5 md:h-4 md:w-4 text-muted-foreground" />
                  <span className="capitalize">{data.companions}</span>
                </div>
              </div>
              {data.estimated_cost && (
                <div className="flex items-center gap-1.5 bg-primary/10 text-primary px-3 py-1.5 rounded-md text-sm md:text-base font-bold">
                  Total: {data.estimated_cost.currency || '₱'}
                  {data.estimated_cost.total_min?.toLocaleString()} - {data.estimated_cost.total_max?.toLocaleString()}
                </div>
              )}
            </div>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto bg-muted/20 scroll-smooth">
            <div className="px-4 py-6 md:px-8 md:py-8 max-w-3xl mx-auto space-y-12 pb-16">
              
              {/* Daily Itinerary */}
              <div className="space-y-10">
                {data.days_data && data.days_data.map((day) => (
                  <TripDayTimeline key={`day-${day.day_number}`} dayData={day} />
                ))}
              </div>

              <hr className="border-border/60" />

              {/* General Tips */}
              {data.tips && data.tips.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-amber-500" />
                    Important Tips
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {data.tips.map((tip, idx) => (
                      <div key={idx} className="bg-card border rounded-lg p-4 text-sm shadow-sm text-muted-foreground">
                        {tip}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Packing List */}
              {data.packing_suggestions && data.packing_suggestions.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Luggage className="h-5 w-5 text-indigo-500" />
                    What to Pack
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {data.packing_suggestions.map((item, idx) => (
                      <div key={idx} className="bg-card border rounded-full px-4 py-2 text-sm shadow-sm font-medium">
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

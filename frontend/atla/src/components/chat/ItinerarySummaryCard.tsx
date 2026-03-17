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
  Luggage,
  Bed,
  Camera,
  Utensils,
  Car
} from 'lucide-react';
import type { ItineraryResponse } from '../../types/chat';
import { TripDayTimeline } from '../trips/TripDayTimeline';

interface ItinerarySummaryCardProps {
  data: ItineraryResponse;
}

export function ItinerarySummaryCard({ data }: ItinerarySummaryCardProps) {
  const [isOpen, setIsOpen] = useState(false);
  const safeCurrency = data.estimated_cost?.currency || '₱';

  return (
    <div className="flex flex-col items-start mt-2 w-full max-w-full overflow-hidden">
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        {/* The Chat Bubble Card */}
        <div className="w-full bg-primary/5 border border-primary/20 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-primary/10">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <MapPin className="h-5 w-5 text-primary" />
              Your Trip to {data.destination || 'Unknown Destination'}
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              I've put together a complete itinerary based on your preferences!
            </p>
          </div>

          <div className="p-4 space-y-4">
            <div className="flex flex-wrap gap-2 text-sm">
              <div className="flex items-center gap-1.5 bg-background px-3 py-1 rounded-full border shadow-sm">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{data.days ? `${data.days} Days` : 'Duration unspecified'}</span>
              </div>
              <div className="flex items-center gap-1.5 bg-background px-3 py-1 rounded-full border shadow-sm">
                <Wallet className="h-4 w-4 text-muted-foreground" />
                <span className={data.budget ? "capitalize font-medium" : "text-muted-foreground italic"}>
                  {data.budget ? `${data.budget} Budget` : 'Budget unspecified'}
                </span>
              </div>
              <div className="flex items-center gap-1.5 bg-background px-3 py-1 rounded-full border shadow-sm">
                <Users className="h-4 w-4 text-muted-foreground" />
                <span className={data.companions ? "capitalize font-medium" : "text-muted-foreground italic"}>
                  {data.companions || 'Companions unspecified'}
                </span>
              </div>
            </div>

            <div className="bg-background/80 p-3 rounded-lg border shadow-sm">
              <h4 className="font-semibold text-xs uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1.5">
                <Sparkles className="h-3.5 w-3.5" /> Highlights
              </h4>
              <ul className="space-y-1.5">
                {data.highlights && data.highlights.length > 0 ? (
                  <>
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
                  </>
                ) : (
                  <li className="text-sm text-muted-foreground italic">No highlights available</li>
                )}
              </ul>
            </div>

            <div className="text-sm font-semibold flex items-center justify-between border-t pt-3 mt-1">
              <span className="text-muted-foreground">Est. Total:</span>
              <span className="text-lg text-primary">
                {data.estimated_cost && (data.estimated_cost.total_min || data.estimated_cost.total_max) ? (
                  <>
                    {safeCurrency}
                    {data.estimated_cost.total_min?.toLocaleString() || 0} -{' '}
                    {data.estimated_cost.total_max?.toLocaleString() || 0}
                  </>
                ) : (
                  <span className="text-sm text-muted-foreground italic font-normal">Cost estimate pending</span>
                )}
              </span>
            </div>
          </div>

          <div className="p-4 bg-muted/30 border-t">
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
            <div className="flex items-start justify-between pr-4 md:pr-2">
              <div>
                <DialogTitle className="text-2xl md:text-4xl font-extrabold flex items-center gap-2 mb-2 md:mb-3">
                  <PlaneTakeoff className="h-6 w-6 md:h-8 md:w-8 text-primary" />
                  {data.days ? `${data.days} Days in` : 'Trip to'} {data.destination || 'Unknown Destination'}
                </DialogTitle>
                <DialogDescription className="text-sm md:text-base text-foreground/80 leading-relaxed max-w-3xl text-justify hyphens-auto">
                  {data.summary || 'No summary available for this itinerary.'}
                </DialogDescription>
              </div>
            </div>

            <div className="flex flex-col md:flex-row md:justify-center items-center gap-2 mt-4 pt-4 border-t border-border/50">
              <div className='flex justify-center items-center gap-2'>
                <div className="flex items-center gap-1.5 bg-muted px-3 py-1.5 rounded-md text-xs md:text-sm font-medium">
                  <Wallet className="h-3.5 w-3.5 md:h-4 md:w-4 text-muted-foreground" />
                  <span className={data.budget ? "capitalize" : "text-muted-foreground italic"}>
                    {data.budget ? `${data.budget} Budget` : 'Budget not specified'}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 bg-muted px-3 py-1.5 rounded-md text-xs md:text-sm font-medium">
                  <Users className="h-3.5 w-3.5 md:h-4 md:w-4 text-muted-foreground" />
                  <span className={data.companions ? "capitalize" : "text-muted-foreground italic"}>
                    {data.companions || 'Companions not specified'}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-1.5 bg-muted text-primary px-3 py-1.5 rounded-md text-xs md:text-sm font-medium">
                Total:{' '}
                {data.estimated_cost && (data.estimated_cost.total_min || data.estimated_cost.total_max) ? (
                  <>
                    {safeCurrency}
                    {data.estimated_cost.total_min?.toLocaleString() || 0} - {data.estimated_cost.total_max?.toLocaleString() || 0}
                  </>
                ) : (
                  <span className="text-xs md:text-sm text-primary/70 italic font-normal">Total cost pending</span>
                )}
              </div>
            </div>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto bg-muted/20 scroll-smooth">
            <div className="px-4 py-2 md:px-8 max-w-3xl mx-auto space-y-12 pb-10">

              {/* Detailed Cost Breakdown */}
              <div className="space-y-3">
                <h3 className="text-[18.5px] md:text-xl font-bold flex items-center justify-center md:justify-start gap-1.5">
                  <Wallet className="h-5 w-5 text-emerald-600" />
                  <p className='-mt-0.5 md:-mt-1 '>Estimated Cost Breakdown</p>
                </h3>

                {data.estimated_cost ? (
                  <div className="grid gap-3">
                    <div className="bg-card border rounded-xl p-4 shadow-sm flex flex-col justify-between">
                      <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 flex items-center gap-1.5">
                        <Bed className="h-3.5 w-3.5" /> Stay
                      </span>
                      <div>
                        {data.estimated_cost.accommodation ? (
                          <>
                            <div className="flex items-center gap-1.5">
                              <p className=' font-bold text-base text-foreground'>
                              {safeCurrency}{data.estimated_cost.accommodation.min?.toLocaleString() || 0} - {data.estimated_cost.accommodation.max?.toLocaleString() || 0}
                              </p>
                              {data.estimated_cost.accommodation.per_night && (
                              <div className="text-[10px] text-muted-foreground font-semibold">per night</div>
                            )}
                            </div>
                        
                            {data.estimated_cost.accommodation.note && (
                              <div className="text-[10px] text-muted-foreground italic mt-1 leading-tight border-t pt-1 border-border/50">
                                {data.estimated_cost.accommodation.note}
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-sm text-muted-foreground italic">N/A</div>
                        )}
                      </div>
                      </div>

                      <div className="bg-card border rounded-xl p-4 shadow-sm flex flex-col justify-between">
                      <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 flex items-center gap-1.5">
                        <Camera className="h-3.5 w-3.5" /> Activities
                      </span>
                      <div>
                        {data.estimated_cost.activities ? (
                          <>
                            <div className="font-bold text-base text-foreground">
                              {safeCurrency}{data.estimated_cost.activities.min?.toLocaleString() || 0} - {data.estimated_cost.activities.max?.toLocaleString() || 0}
                            </div>
                            {data.estimated_cost.activities.note && (
                              <div className="text-[10px] text-muted-foreground italic mt-1 leading-tight border-t pt-1 border-border/50">
                                {data.estimated_cost.activities.note}
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-sm text-muted-foreground italic">N/A</div>
                        )}
                      </div>
                      </div>

                      <div className="bg-card border rounded-xl p-4 shadow-sm flex flex-col justify-between">
                      <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 flex items-center gap-1.5">
                        <Utensils className="h-3.5 w-3.5" /> Food
                      </span>
                      <div>
                        {data.estimated_cost.food ? (
                          <>
                            <div className="flex items-center gap-1.5">
                              <p className='font-bold text-base text-foreground'>
                                {safeCurrency}{data.estimated_cost.food.min?.toLocaleString() || 0} - {data.estimated_cost.food.max?.toLocaleString() || 0}
                              </p>
                            {data.estimated_cost.food.per_day && (
                              <div className="text-[10px] text-muted-foreground font-semibold">per day</div>
                            )}
                            </div>
                            {data.estimated_cost.food.note && (
                              <div className="text-[10px] text-muted-foreground italic mt-1 leading-tight border-t pt-1 border-border/50">
                                {data.estimated_cost.food.note}
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-sm text-muted-foreground italic">N/A</div>
                        )}
                      </div>
                      </div>

                      <div className="bg-card border rounded-xl p-4 shadow-sm flex flex-col justify-between">
                      <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 flex items-center gap-1.5">
                        <Car className="h-3.5 w-3.5" /> Transport
                      </span>
                      <div>
                        {data.estimated_cost.transport ? (
                          <>
                            <div className="font-bold text-base text-foreground">
                              {safeCurrency}{data.estimated_cost.transport.min?.toLocaleString() || 0} - {data.estimated_cost.transport.max?.toLocaleString() || 0}
                            </div>
                            {data.estimated_cost.transport.note && (
                              <div className="text-[10px] text-muted-foreground italic mt-1 leading-tight border-t pt-1 border-border/50">
                                {data.estimated_cost.transport.note}
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-sm text-muted-foreground italic">N/A</div>
                        )}
                      </div>                    </div>
                  </div>
                ) : (
                  <div className="bg-card border rounded-xl p-6 text-center text-sm text-muted-foreground italic shadow-sm">
                    Cost breakdown is currently unavailable for this itinerary.
                  </div>
                )}
              </div>

              <hr className='mb-4 border-border/60' />

              {/* Daily Itinerary */}
              <div className="space-y-10">
                {data.days_data && data.days_data.length > 0 ? (
                  data.days_data.map((day) => (
                    <TripDayTimeline key={`day-${day.day_number}`} dayData={day} />
                  ))
                ) : (
                  <div className="text-center py-8 text-muted-foreground italic bg-card border rounded-xl shadow-sm">
                    No daily itinerary data available.
                  </div>
                )}
              </div>

              <hr className="border-border/60" />

              {/* General Tips */}
              <div>
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-amber-500" />
                  Important Tips
                </h3>
                {data.tips && data.tips.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {data.tips.map((tip, idx) => (
                      <div key={idx} className="bg-card border rounded-lg p-4 text-sm shadow-sm text-muted-foreground">
                        {tip}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground italic">No tips provided.</p>
                )}
              </div>

              {/* Packing List */}
              <div>
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Luggage className="h-5 w-5 text-indigo-500" />
                  What to Pack
                </h3>
                {data.packing_suggestions && data.packing_suggestions.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {data.packing_suggestions.map((item, idx) => (
                      <div key={idx} className="bg-card border rounded-full px-4 py-2 text-sm shadow-sm font-medium">
                        {item}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground italic">No packing suggestions provided.</p>
                )}
              </div>

            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

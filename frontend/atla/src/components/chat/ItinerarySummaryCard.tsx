import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../ui/card';
import { Button } from '../ui/button';
import { MapPin, Calendar, Wallet, Users, ArrowRight } from 'lucide-react';
import type { ItineraryResponse } from '../../types/chat';

interface ItinerarySummaryCardProps {
  data: ItineraryResponse;
}

export function ItinerarySummaryCard({ data }: ItinerarySummaryCardProps) {
  return (
    <div className="flex flex-col items-start mt-2 ml-4 w-full max-w-[90%]">
      <Card className="w-full bg-primary/5 border-primary/20">
        <CardHeader className="pb-3">
          <CardTitle className="text-xl flex items-center gap-2">
            <MapPin className="h-5 w-5 text-primary" />
            Your Trip to {data.destination}
          </CardTitle>
          <CardDescription>
            I've put together a complete itinerary based on your preferences!
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-1.5 bg-background px-3 py-1.5 rounded-full border shadow-sm">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span>{data.days} Days</span>
            </div>
            {data.budget && (
              <div className="flex items-center gap-1.5 bg-background px-3 py-1.5 rounded-full border shadow-sm">
                <Wallet className="h-4 w-4 text-muted-foreground" />
                <span className="capitalize">{data.budget} Budget</span>
              </div>
            )}
            {data.companions && (
              <div className="flex items-center gap-1.5 bg-background px-3 py-1.5 rounded-full border shadow-sm">
                <Users className="h-4 w-4 text-muted-foreground" />
                <span className="capitalize">{data.companions}</span>
              </div>
            )}
          </div>

          <div className="bg-background p-4 rounded-lg border shadow-sm space-y-3">
            <h4 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">
              Highlights
            </h4>
            <ul className="space-y-2">
              {data.highlights.map((highlight: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2 text-sm">
                  <div className="mt-1 h-1.5 w-1.5 rounded-full bg-primary flex-shrink-0" />
                  <span>{highlight}</span>
                </li>
              ))}
            </ul>
          </div>

          {data.estimated_cost && (
            <div className="text-sm font-medium pt-2">
              Estimated Total: {data.estimated_cost.currency || 'P'}
              {data.estimated_cost.total_min?.toLocaleString()} -{' '}
              {data.estimated_cost.total_max?.toLocaleString()}
            </div>
          )}
        </CardContent>
        <CardFooter>
          <Button className="w-full sm:w-auto" type="button">
            View Full Itinerary Details <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../ui/card';
import { Button } from '../ui/button';
import { Link } from '@tanstack/react-router';
import { MapPin, Calendar, Wallet, Users, ArrowRight } from 'lucide-react';
import type { Trip } from '../../types/trip';

interface TripCardProps {
  trip: Trip;
}

export function TripCard({ trip }: TripCardProps) {
  const safeCurrency = '₱'; // Fallback since the summary might not have currency info

  return (
    <Card className="flex flex-col h-full overflow-hidden hover:shadow-md transition-shadow">
      <CardHeader className="bg-primary/5 py-4 border-primary/10">
        <CardTitle className="text-lg flex items-start justify-between gap-2">
          <span className="line-clamp-2">{trip.title || `Trip to ${trip.destination}` || `Title Unspecified`}</span>
        </CardTitle>
        <CardDescription className="flex items-center gap-1.5 text-primary/80 font-medium">
          <MapPin className="h-3.5 w-3.5" />
          {trip.destination || `Destination Unspecified`}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1 p-4 space-y-4">
        <p className="text-sm text-muted-foreground line-clamp-3">
          {trip.summary || 'No description available for this itinerary.'}
        </p>

        <div className="flex flex-wrap gap-2 text-xs">
          <div className="flex items-center gap-1.5 bg-muted px-2.5 py-1 rounded-md text-muted-foreground font-medium">
            <Calendar className="h-3.5 w-3.5" />
            <span>{trip.days ? `${trip.days} Days` : 'Duration Unspecified'}</span>
          </div>
          <div className="flex items-center gap-1.5 bg-muted px-2.5 py-1 rounded-md text-muted-foreground font-medium capitalize">
            <Wallet className="h-3.5 w-3.5" />
            <span>{trip.budget || 'Budget unspecified'}</span>
          </div>
          <div className="flex items-center gap-1.5 bg-muted px-2.5 py-1 rounded-md text-muted-foreground font-medium capitalize">
            <Users className="h-3.5 w-3.5" />
            <span>{trip.companions || 'Companions unspecified'}</span>
          </div>
        </div>
      </CardContent>
      
      <CardFooter className="p-4 border-t bg-muted/20 flex items-center justify-between">
        <div className="text-sm font-semibold">
          {(trip.total_budget_min || trip.total_budget_max) ? (
            <span className="text-foreground">
              {safeCurrency}{trip.total_budget_min?.toLocaleString() || 0} - {trip.total_budget_max?.toLocaleString() || 0}
            </span>
          ) : (
            <span className="text-muted-foreground italic font-normal">Total cost pending</span>
          )}
        </div>
        
        <Link to="/trips/$tripId" params={{ tripId: trip.id.toString() }}>
           <Button variant="ghost" size="sm" className="h-8 gap-1 px-2">
              View <ArrowRight className="h-3.5 w-3.5" />
           </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}

import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Link } from '@tanstack/react-router'
import { useUserTrips } from '../hooks/useTrips'
import { TripCard } from '../components/trips/TripCard'
import { Loader2 } from 'lucide-react'

export function HomePage() {
  // Fetch only the 2 most recent trips for the dashboard
  const { data: recentTrips, isLoading, isError, error } = useUserTrips(0, 2);

  const is404Error = isError && (error as { response?: { status?: number } })?.response?.status === 404;
  const showEmptyState = (!isLoading && !isError && recentTrips?.length === 0) || is404Error;
  const showRealError = isError && !is404Error;

  return (
    <div className="min-h-screen p-4 md:p-0 pb-[80px] md:pb-8 bg-muted/10">
      <div className="max-w-4xl mx-auto space-y-6 mt-4 md:mt-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Trip Dashboard</h1>
         

        <Card className="border shadow-sm">
          <CardHeader className="pb-3 flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-xl text-primary">Your Trips</CardTitle>
              <CardDescription>
                View and manage your Philippine travel plans
              </CardDescription>
            </div>
            {recentTrips && recentTrips.length > 0 && !showRealError && (
              <Link to="/trips">
                <Button variant="ghost" size="sm" className="hidden sm:flex">
                  View All
                </Button>
              </Link>
            )}
          </CardHeader>
          <CardContent>
            {isLoading && (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            )}
            
            {showRealError && (
              <div className="text-center py-8 text-destructive text-sm">
                Failed to load recent trips.
              </div>
            )}

            {showEmptyState && (
              <div className="bg-muted/30 border border-dashed rounded-lg p-8 text-center flex flex-col items-center justify-center">
                <p className="text-muted-foreground mb-4">
                  No trips yet. Start planning your first adventure!
                </p>
                <Link to="/chat">
                  <Button variant="secondary" size="sm">Start Planning</Button>
                </Link>
              </div>
            )}

            {!isLoading && !showRealError && recentTrips && recentTrips.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {recentTrips.map((trip) => (
                  <TripCard key={trip.id} trip={trip} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="border shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Link to="/chat" className="block w-full">
                <Button className="w-full h-12 text-md font-semibold shadow-sm transition-transform active:scale-[0.98]">
                  Plan New Trip
                </Button>
              </Link>
              <Link to="/explore" className="block w-full">
                <Button variant="outline" className="w-full h-12 text-md transition-transform active:scale-[0.98]">
                  Explore Places
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="border shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-24 flex items-center justify-center text-sm text-muted-foreground italic">
                No recent activity
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

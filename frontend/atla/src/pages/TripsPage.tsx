import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Link } from "@tanstack/react-router";
import { useUserTrips } from "../hooks/useTrips";
import { Loader2, Plus, AlertCircle, Map } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "../components/ui/alert";
import { TripCard } from "../components/trips/TripCard";

export function TripsPage() {
  const { data: trips, isLoading, isError, error, refetch } = useUserTrips();

  // If the backend returns a 404, it means the user has no trips yet.
  // We should treat this as an empty state, not a fatal error.
  const is404Error = isError && (error as { response?: { status?: number } })?.response?.status === 404;
  const showEmptyState =(!isLoading && !isError && trips?.length === 0) || is404Error;
  const showRealError = isError && !is404Error;

  return (
    <div className="min-h-screen p-4 md:p-0 pb-[80px] md:pb-8 bg-muted/10">
      <div className="max-w-4xl mx-auto mt-4 md:mt-8">
        <div className="flex justify-between items-center mb-6 px-1">
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            My Trips
          </h1>
          {!showEmptyState && (
            <Link to="/chat">
              <Button size="sm" className="hidden sm:flex gap-1.5">
                <Plus className="h-4 w-4" /> Plan New Trip
              </Button>
            </Link>
          )}
        </div>

        <Card className="border shadow-sm overflow-hidden bg-card/50">
          <CardHeader className="bg-card border-b pb-4">
            <CardTitle className="text-xl">Your Travel Plans</CardTitle>
            <CardDescription>
              All your saved Philippine adventures in one place
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0 sm:p-6">
            {/* Loading State */}
            {isLoading && (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
                <p>Loading your adventures...</p>
              </div>
            )}

            {/* Error State */}
            {showRealError && (
              <div className="p-6">
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription className="flex flex-col gap-2">
                    <p>
                      Failed to load your trips.{" "}
                      {(error as Error)?.message || "Please try again."}
                    </p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => refetch()}
                      className="w-fit"
                    >
                      Try Again
                    </Button>
                  </AlertDescription>
                </Alert>
              </div>
            )}

            {/* Empty State */}
            {showEmptyState && (
              <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
                <div className="h-20 w-20 bg-primary/10 rounded-full flex items-center justify-center mb-6">
                  <Map className="h-10 w-10 text-primary opacity-80" />
                </div>
                <h3 className="text-xl font-bold mb-2">No trips yet</h3>
                <p className="text-muted-foreground max-w-md mb-8">
                  You haven't saved any itineraries. Start planning your first
                  perfect Philippine getaway using our AI travel assistant!
                </p>
                <Link to="/chat" className="w-full sm:w-auto">
                  <Button size="lg" className="w-full sm:w-auto gap-2">
                    <Plus className="h-5 w-5" /> Start Planning Now
                  </Button>
                </Link>
              </div>
            )}

            {/* Data State */}
            {!isLoading && !showRealError && trips && trips.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 sm:p-0">
                {trips.map((trip) => (
                  <TripCard key={trip.id} trip={trip} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

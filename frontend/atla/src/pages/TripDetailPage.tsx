import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { useParams, Link } from "@tanstack/react-router";
import { useTripDetail } from "../hooks/useTrips";
import {
  Loader2,
  ArrowLeft,
  Wallet,
  Users,
  Map as MapIcon,
} from "lucide-react";
import { TripDayTimeline } from "../components/trips/TripDayTimeline";
import { useState } from "react";

export function TripDetailPage() {
  const { tripId } = useParams({ from: "/trips/$tripId" });
  const { data: trip, isLoading, isError } = useTripDetail(Number(tripId));
  const [activeTab, setActiveTab] = useState<"itinerary" | "map" | "budget">(
    "itinerary"
  );

  if (isLoading) {
    return (
      <div className="min-h-screen p-4 flex flex-col items-center justify-center pb-[80px] md:pb-8 bg-muted/10">
        <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground">Loading trip details...</p>
      </div>
    );
  }

  if (isError || !trip) {
    return (
      <div className="min-h-screen p-4 flex flex-col items-center justify-center pb-[80px] md:pb-8 bg-muted/10">
        <h2 className="text-xl font-bold mb-2">Trip Not Found</h2>
        <p className="text-muted-foreground mb-4">
          We couldn't load the details for this trip.
        </p>
        <Link to="/trips">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Trips
          </Button>
        </Link>
      </div>
    );
  }

  const safeCurrency = "₱";

  return (
    <div className="min-h-screen pb-[80px] md:pb-8 bg-muted/20 max-w-4xl mx-auto px-3 md:px-0 overflow-hidden">
      {/* Match with ItinerarySummaryCard  as of now*/}
      <Link
        to="/trips"
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground my-4 transition-colors"
      >
        <ArrowLeft className="mr-1 h-4 w-4" /> Back to Trips
      </Link>

      <div className="max-w-4xl">
        <div>
          <h1 className="text-2xl font-extrabold flex items-center gap-3 mb-3 text-foreground">
            {trip.title || `Trip to ${trip.destination}` || `Title Unspecified`}
          </h1>
          <p className="text-sm md:text-base text-foreground/80 leading-relaxed text-justify hyphens-auto"  >
            {`${trip.summary}` || `No summary available for this itinerary`}
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-2 my-6 py-4 border-t border-b border-border/50">
        <div className="flex flex-col md:flex-row items-center gap-2">
          <div className="flex space-x-2 w-full md:w-auto">
            {/* Budget */}
            <div className="flex flex-1 justify-center md:flex-none md:justify-start items-center gap-1.5 bg-muted px-3 py-1.5 rounded-md text-xs md:text-sm font-medium">
              <Wallet className="h-3.5 w-3.5 md:h-4 md:w-4 text-muted-foreground" />
              <span
                className={
                  trip.budget ? "capitalize" : "text-muted-foreground italic"
                }
              >
                {trip.budget ? `${trip.budget} Budget` : 'Budget not specified'}
              </span>
            </div>

            {/* Companions */}
            <div className="flex flex-1 justify-center md:flex-none md:justify-start items-center gap-1.5 bg-muted px-3 py-1.5 rounded-md text-xs md:text-sm font-medium">
              <Users className="h-3.5 w-3.5 md:h-4 md:w-4 text-muted-foreground" />
              <span
                className={
                  trip.companions
                    ? "capitalize"
                    : "text-muted-foreground italic"
                }
              >
                {trip.companions || 'Companions not specified'}
              </span>
            </div>
          </div>

          {/* Estimated Total Budget */}
          <div className="flex w-full justify-center md:w-auto md:justify-start items-center gap-1.5 bg-muted text-primary px-3 py-1.5 rounded-md text-xs md:text-sm font-medium">
            Est. Total:{" "}
            {trip.total_budget_min || trip.total_budget_max ? (
              <>
                {safeCurrency}
                {trip.total_budget_min?.toLocaleString() || 0} -{" "}
                {trip.total_budget_max?.toLocaleString() || 0}
              </>
            ) : (
              <span className="text-xs md:text-sm text-primary/70 italic font-normal">
                Total budget pending
              </span>
            )}
          </div>
        </div>

        {/* Tab Navigation Buttons */}
        <div className="flex space-x-2">
          <Button
            variant={activeTab === "itinerary" ? "default" : "outline"}
            onClick={() => setActiveTab("itinerary")}
            className="rounded-full px-6 whitespace-nowrap snap-start"
          >
            Itinerary
          </Button>
          <Button
            variant={activeTab === "budget" ? "default" : "outline"}
            onClick={() => setActiveTab("budget")}
            className="rounded-full px-6 whitespace-nowrap snap-start"
          >
            Budget
          </Button>
          <Button
            variant={activeTab === "map" ? "default" : "outline"}
            onClick={() => setActiveTab("map")}
            className="rounded-full px-6 whitespace-nowrap snap-start"
          >
            Map
          </Button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto">
        {/* Tab Content Area */}
        <div className="pb-10">
          {/* ITINERARY TAB */}
          {activeTab === "itinerary" && (
            <div className="space-y-10">
              {trip.trip_days && trip.trip_days.length > 0 ? (
                trip.trip_days.map((day) => {
                  return (
                    <TripDayTimeline
                      key={`day-${day.day_number}`}
                      dayData={day}
                    />
                  );
                })
              ) : (
                <div className="text-center py-16 text-muted-foreground italic bg-card border rounded-xl shadow-sm">
                  No daily itinerary data available for this trip.
                </div>
              )}
            </div>
          )}

          {/* BUDGET TAB */}
          {activeTab === "budget" && (
              <Card className="border shadow-sm py-0 gap-0">
                <CardHeader className="bg-muted/30 pb-0 py-5 border-b">
                  <CardTitle className="text-xl flex items-center gap-2">
                    <Wallet className="h-5 w-5 text-emerald-600" />
                    Budget Cost Breakdown
                  </CardTitle>
                </CardHeader>
                <CardContent className="py-10 space-y-6">
                  <div className="text-center">
                    {trip.total_budget_min || trip.total_budget_max ? (
                      <div className="text-4xl font-extrabold text-foreground mb-2">
                        {safeCurrency}
                        {trip.total_budget_min?.toLocaleString() || 0} -{" "}
                        {safeCurrency}
                        {trip.total_budget_max?.toLocaleString() || 0}
                      </div>
                    ) : (
                      <div className="text-2xl font-bold text-muted-foreground italic mb-2">
                        Budget estimate pending
                      </div>
                    )}
                    <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider">
                      Estimated Total Cost
                    </p>
                  </div>
                </CardContent>
              </Card>
          )}

          {/* MAP TAB */}
          {activeTab === "map" && (
            <Card className="border shadow-sm overflow-hidden">
              <div className="h-[500px] bg-muted/30 flex flex-col items-center justify-center p-6 text-center">
                <div className="h-24 w-24 bg-primary/10 rounded-full flex items-center justify-center mb-6">
                  <MapIcon className="h-12 w-12 text-primary opacity-60" />
                </div>
                <h3 className="text-2xl font-bold mb-2">Interactive Map</h3>
                <p className="text-muted-foreground max-w-md">
                  Map integration is still in development. You will soon be able
                  to view all your daily activities pinned on a live map of{" "}
                  {trip.destination}!
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

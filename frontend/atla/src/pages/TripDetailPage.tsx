import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { useParams } from '@tanstack/react-router'

export function TripDetailPage() {
  const { tripId } = useParams({ from: '/trips/$tripId' })
  
  return (
    <div className="min-h-screen p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Trip Details</h1>
          <div className="flex gap-2">
            <Button variant="outline">Edit</Button>
            <Button variant="destructive">Delete</Button>
          </div>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Trip #{tripId}</CardTitle>
            <CardDescription>
              View and manage your trip details
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 mb-4">
              <Button variant="default">Itinerary</Button>
              <Button variant="outline">Map</Button>
              <Button variant="outline">Budget</Button>
            </div>
            <p className="text-muted-foreground">
              Trip details will appear here. Connect to your backend to load real trip data.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

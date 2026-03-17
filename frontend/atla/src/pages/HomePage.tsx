import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Link } from '@tanstack/react-router'

export function HomePage() {
  return (
    <div className="min-h-screen p-4 md:p-0 pb-[80px] md:pb-8 bg-muted/10">
      <div className="max-w-4xl mx-auto space-y-6 mt-4 md:mt-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Trip Dashboard</h1>
         

        <Card className="border shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-xl text-primary">Your Trips</CardTitle>
            <CardDescription>
              View and manage your Philippine travel plans
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-muted/30 border border-dashed rounded-lg p-8 text-center flex flex-col items-center justify-center">
              <p className="text-muted-foreground mb-4">
                No trips yet. Start planning your first adventure!
              </p>
              <Link to="/chat">
                <Button variant="secondary" size="sm">Start Planning</Button>
              </Link>
            </div>
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

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'

import { Link } from '@tanstack/react-router'

export function TripsPage() {
  return (
    <div className="min-h-screen p-4 md:p-0 pb-[80px] md:pb-8 bg-muted/10">
      <div className="max-w-4xl mx-auto mt-4 md:mt-8">
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground mb-6">My Trips</h1>
        <Card className="border shadow-sm">
          <CardHeader>
            <CardTitle>Your Trips</CardTitle>
            <CardDescription>
              All your Philippine travel plans in one place
            </CardDescription>
          </CardHeader>
          <CardContent className='space-y-4'>
            <p className="text-muted-foreground text-center">
              No trips yet. Start planning your first adventure!
            </p>
            <Link to='/chat'>
              <Button  className='w-full mx-auto'>Plan New Trip</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

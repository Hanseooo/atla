import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { useState } from 'react'

export function ExplorePage() {
  const [search, setSearch] = useState('')
  
  return (
    <div className="min-h-screen p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Explore Places</h1>
        
        <div className="flex gap-2 mb-6">
          <Input
            placeholder="Search places..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <Button>Search</Button>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Popular Destinations</CardTitle>
            <CardDescription>
              Discover amazing places in the Philippines
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-center py-8">
              Search for destinations to see results
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

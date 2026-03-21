import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { useState } from 'react'
import { usePlacesSearch } from '../hooks/usePlaces'
import { Loader2, MapPin, Search } from 'lucide-react'

export function ExplorePage() {
  const [searchInput, setSearchInput] = useState('')
  const [activeSearch, setActiveSearch] = useState('')
  
  const { data: places, isLoading, isError } = usePlacesSearch(activeSearch)

  const handleSearch = (e?: React.FormEvent) => {
    e?.preventDefault()
    if (searchInput.trim()) {
      setActiveSearch(searchInput.trim())
    }
  }
  
  return (
    <div className="min-h-screen p-4 md:p-0 pb-[80px] md:pb-8 bg-muted/10">
      <div className="max-w-4xl mx-auto mt-4 md:mt-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-foreground mb-6 px-1">Explore Places</h1>
        
        <form onSubmit={handleSearch} className="flex gap-2 mb-6 px-1">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search destinations (e.g. Palawan, Boracay)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="pl-9 h-12"
            />
          </div>
          <Button type="submit" className="h-12 px-6">Search</Button>
        </form>
        
        <Card className="border shadow-sm overflow-hidden">
          <CardHeader className="bg-card border-b pb-4">
            <CardTitle className="text-xl text-primary">Discover Destinations</CardTitle>
            <CardDescription>
              {activeSearch ? `Search results for "${activeSearch}"` : 'Search for places to see simulated results'}
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0 sm:p-6">
            
            {!activeSearch && !isLoading && (
              <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
                <div className="h-20 w-20 bg-muted rounded-full flex items-center justify-center mb-4">
                  <MapPin className="h-8 w-8 text-muted-foreground opacity-50" />
                </div>
                <p className="text-muted-foreground">
                  Try searching for popular spots like "Cebu" or "Siargao"
                </p>
                <p className="text-xs text-muted-foreground italic mt-2">
                  (Note: Currently using simulated data while backend API is pending)
                </p>
              </div>
            )}

            {isLoading && (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
                <p>Searching destinations...</p>
              </div>
            )}

            {isError && (
              <div className="text-center py-8 text-destructive text-sm">
                Failed to load search results.
              </div>
            )}

            {!isLoading && activeSearch && places?.length === 0 && (
              <div className="text-center py-16 text-muted-foreground">
                <p className="mb-2">No destinations found matching "{activeSearch}".</p>
                <Button variant="link" onClick={() => { setSearchInput(''); setActiveSearch(''); }}>
                  Clear search
                </Button>
              </div>
            )}

            {!isLoading && places && places.length > 0 && (
              <div className="flex flex-col divide-y">
                {places.map((place) => (
                  <div key={place.id} className="p-4 hover:bg-muted/50 transition-colors flex items-start gap-4">
                    <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                      <MapPin className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-bold text-lg">{place.name}</h3>
                      <p className="text-sm text-muted-foreground mt-1 leading-relaxed">
                        {place.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

          </CardContent>
        </Card>
      </div>
    </div>
  )
}

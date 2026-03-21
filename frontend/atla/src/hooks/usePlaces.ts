import { useQuery, type UseQueryResult } from '@tanstack/react-query';

// Temporary mock data until backend places API is implemented
const MOCK_PLACES = [
  { id: '1', name: 'Palawan', description: 'Known for its crystal-clear waters and underground river.' },
  { id: '2', name: 'Boracay', description: 'Famous for its white sand beaches and vibrant nightlife.' },
  { id: '3', name: 'Siargao', description: 'The surfing capital of the Philippines.' },
  { id: '4', name: 'Bohol', description: 'Home to the Chocolate Hills and tarsiers.' },
  { id: '5', name: 'Cebu', description: 'Rich in history with beautiful waterfalls and diving spots.' },
];

export const placeKeys = {
  all: ['places'] as const,
  search: (query: string) => [...placeKeys.all, 'search', query] as const,
};

type MockPlace = typeof MOCK_PLACES[0];

export function usePlacesSearch(query: string): UseQueryResult<MockPlace[], Error> {
  return useQuery({
    queryKey: placeKeys.search(query),
    queryFn: async () => {
      // Simulate network latency
      await new Promise((resolve) => setTimeout(resolve, 800));
      
      if (!query.trim()) {
        return [];
      }

      const lowerQuery = query.toLowerCase();
      return MOCK_PLACES.filter(
        place => 
          place.name.toLowerCase().includes(lowerQuery) || 
          place.description.toLowerCase().includes(lowerQuery)
      );
    },
    enabled: query.length > 0,
    staleTime: 1000 * 60 * 5,
  });
}

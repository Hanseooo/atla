import { http, HttpResponse, type HttpHandler } from 'msw';
import type { ClarificationResponse, ItineraryResponse } from '../types/chat';

export const mockSessionId = 'test-session-123';

export const mockClarificationResponse: ClarificationResponse = {
  type: 'clarification',
  session_id: mockSessionId,
  message: "I need a few more details to plan your perfect trip.",
  progress: { completed: 1, total: 4, percentage: 25 },
  questions: [
    {
      id: 'q_budget',
      field: 'budget',
      type: 'single_choice',
      question: "What's your budget range?",
      required: true,
      priority: 1,
      options: [
        { id: 'low', label: 'Budget-friendly', description: 'Under P5,000/day' },
        { id: 'mid', label: 'Moderate', description: 'P5,000-15,000/day' },
      ],
    }
  ],
  current_intent: {
    destination: 'Palawan',
    days: undefined,
    budget: undefined,
    companions: undefined,
    travel_style: [],
    time_of_year: undefined,
    extra_notes: {
      must_visit: [],
      avoid: [],
      interests: [],
    },
    missing_info: ['days', 'budget', 'companions'],
    confidence: 0.8,
  }
};

export const mockItineraryResponse: ItineraryResponse = {
  type: 'itinerary',
  session_id: mockSessionId,
  message: "Your itinerary is ready!",
  destination: 'Palawan',
  days: 3,
  budget: 'low',
  companions: 'solo',
  summary: "A budget-friendly 3-day solo trip to Palawan.",
  highlights: ["Island Hopping", "Underground River"],
  estimated_cost: {
    currency: '₱',
    total_min: 5000,
    total_max: 8000,
    accommodation: { min: 1500, max: 2000, per_night: true },
    activities: { min: 2000, max: 3000 },
    food: { min: 1000, max: 2000, per_day: true },
    transport: { min: 500, max: 1000 }
  },
  days_data: [
    {
      day_number: 1,
      title: "Arrival and City Tour",
      daily_tips: ["Drink water"],
      activities: [
        {
          name: "Puerto Princesa City Tour",
          category: "attraction",
          cost_min: 0,
          cost_max: 500,
        }
      ]
    }
  ],
  tips: ["Bring sunscreen"],
  packing_suggestions: ["Swimwear"]
};

export const handlers: HttpHandler[] = [
  // 1. Initial send -> clarification response
  http.post('http://localhost:8000/api/chat/', async ({ request }) => {
    const body = await request.json() as { message?: string };

    // Simulate error scenario if the test sends a specific message
    if (body.message === 'TRIGGER_ERROR') {
      return HttpResponse.json(
        { detail: "Simulated server error" },
        { status: 500 }
      );
    }

    return HttpResponse.json(mockClarificationResponse);
  }),

  // 2. Clarification submit -> itinerary response
  http.post('http://localhost:8000/api/chat/*/clarify', async () => {
    return HttpResponse.json(mockItineraryResponse);
  }),

  // 3. Manual itinerary generation when gets requested -> itinerary response
  http.post('http://localhost:8000/api/chat/*/generate-itinerary', async () => {
    return HttpResponse.json(mockItineraryResponse);
  }),

  // 4. Session restore behavior
  http.get('http://localhost:8000/api/chat/*', async ({ request }) => {
    const url = new URL(request.url);
    const pathParts = url.pathname.split('/');
    const sessionId = pathParts[pathParts.length - 1];

    if (sessionId === 'expired-session-404') {
      return HttpResponse.json(
        { detail: "Session not found" },
        { status: 404 }
      );
    }

    return HttpResponse.json({
      id: mockSessionId,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      current_intent: mockClarificationResponse.current_intent
    });
  })
];

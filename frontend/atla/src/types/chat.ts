/**
 * Chat and AI Types
 * 
 * TypeScript types for the AI-powered chat system.
 * Generated from Python Pydantic models in app/schemas/chat_api.py
 * and app/ai/schemas/intent.py, app/ai/schemas/itinerary.py
 */

// ============================================================================
// Request/Response Types
// ============================================================================

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export type ChatResponse = 
  | ClarificationResponse 
  | ItineraryResponse 
  | ErrorResponse;

export interface ErrorResponse {
  type: "error";
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
  retry_after?: number;
}

// ============================================================================
// Intent Types (from app/ai/schemas/intent.py)
// ============================================================================

export type BudgetLevel = "low" | "mid" | "luxury";
export type CompanionType = "solo" | "couple" | "family" | "group";
export type TravelStyle = "adventure" | "relaxation" | "culture" | "food" | "beach" | "nature" | "nightlife";
export type PreferredPace = "relaxed" | "moderate" | "packed";
export type AccommodationType = "hotel" | "resort" | "hostel" | "airbnb";
export type TransportPreference = "public" | "private" | "rental";

export interface ExtraNotes {
  dietary_restrictions?: string;
  accessibility_needs?: string;
  must_visit: string[];
  avoid: string[];
  interests: string[];
  special_occasion?: string;
  preferred_pace?: PreferredPace;
  accommodation_type?: AccommodationType;
  budget_flexibility?: string;
  transport_preference?: TransportPreference;
}

export interface TravelIntent {
  destination?: string;
  days?: number;
  budget?: BudgetLevel;
  travel_style: TravelStyle[];
  companions?: CompanionType;
  time_of_year?: string;
  extra_notes: ExtraNotes;
  missing_info: string[];
  confidence: number;
}

export interface QuestionOption {
  id: string;
  label: string;
  description?: string;
}

export type QuestionType = "single_choice" | "multiple_choice" | "text" | "date";

export interface ClarificationQuestion {
  id: string;
  field: string;
  type: QuestionType;
  question: string;
  options?: QuestionOption[];
  placeholder?: string;
  required: boolean;
  priority: number;
}

export interface ProgressInfo {
  completed: number;
  total: number;
  percentage: number;
}

export interface ClarificationResponse {
  type: "clarification";
  session_id?: string;
  questions: ClarificationQuestion[];
  current_intent: TravelIntent;
  progress: ProgressInfo;
  message: string;
}

// ============================================================================
// Itinerary Types (from app/ai/schemas/itinerary.py)
// ============================================================================

export type ActivityCategory = "attraction" | "restaurant" | "transport" | "activity" | "accommodation";

export interface ActivityData {
  name: string;
  description?: string;
  category: ActivityCategory;
  start_time?: string;
  duration_minutes?: number;
  cost_min?: number;
  cost_max?: number;
  latitude?: number;
  longitude?: number;
  notes?: string;
}

export interface TripDayData {
  day_number: number;
  title: string;
  activities: ActivityData[];
  meals?: {
    breakfast?: string;
    lunch?: string;
    dinner?: string;
  };
  daily_tips: string[];
}

export interface EstimatedCost {
  accommodation?: {
    min: number;
    max: number;
    per_night?: boolean;
    note?: string;
  };
  activities?: {
    min: number;
    max: number;
    note?: string;
  };
  food?: {
    min: number;
    max: number;
    per_day?: boolean;
    note?: string;
  };
  transport?: {
    min: number;
    max: number;
    note?: string;
  };
  total_min?: number;
  total_max?: number;
  currency?: string;
}

export interface ItineraryResponse {
  type: "itinerary";
  session_id: string;
  trip_id?: number;
  destination: string;
  days: number;
  budget?: BudgetLevel;
  companions?: CompanionType;
  days_data: TripDayData[];
  summary: string;
  highlights: string[];
  estimated_cost: EstimatedCost;
  tips: string[];
  packing_suggestions: string[];
  message: string;
}

// ============================================================================
// Session Types
// ============================================================================

export interface ChatSession {
  id: string;
  user_id?: string;
  current_intent?: TravelIntent;
  last_clarification?: ClarificationResponse;
  created_at: string;
  updated_at: string;
}

export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
}

export interface SessionState {
  session_id: string;
  intent: TravelIntent | null;
  history: ConversationMessage[];
  is_complete: boolean;
}

// ============================================================================
// Follow-up Types (for modifying existing plans)
// ============================================================================

export type FollowupType = "clarification" | "modification" | "new_intent" | "unsure" | "unknown";

export interface Suggestion {
  destination: string;
  reason: string;
  highlights?: string[];
  best_for: TravelStyle[];
  source: "static" | "search";
}

export interface FollowupResponse {
  type: FollowupType;
  updated_intent?: TravelIntent;
  message: string;
  requires_regeneration?: boolean;
  suggestions?: Suggestion[];
  questions?: ClarificationQuestion[];
}

// ============================================================================
// API Helper Types
// ============================================================================

export interface ChatApiOptions {
  baseUrl?: string;
  onSessionUpdate?: (sessionId: string) => void;
}

export interface MessageInput {
  text: string;
  attachments?: File[];
}

export type ResponseHandler<T> = (response: T) => void;
export type ErrorHandler = (error: ErrorResponse) => void;

// ============================================================================
// Constants
// ============================================================================

export const REQUIRED_FIELDS = ["destination", "days", "budget", "companions"] as const;

export const VALID_BUDGETS: BudgetLevel[] = ["low", "mid", "luxury"];
export const VALID_COMPANIONS: CompanionType[] = ["solo", "couple", "family", "group"];
export const VALID_TRAVEL_STYLES: TravelStyle[] = ["adventure", "relaxation", "culture", "food", "beach", "nature", "nightlife"];

export const BUDGET_LABELS: Record<BudgetLevel, string> = {
  low: "Budget-friendly (Under P5,000/day)",
  mid: "Moderate (P5,000-15,000/day)",
  luxury: "Luxury (P15,000+/day)",
};

export const COMPANION_LABELS: Record<CompanionType, string> = {
  solo: "Solo",
  couple: "Partner",
  family: "Family",
  group: "Group",
};

export const TRAVEL_STYLE_LABELS: Record<TravelStyle, string> = {
  adventure: "Adventure",
  beach: "Beach & Water",
  culture: "Culture & History",
  food: "Food & Dining",
  nature: "Nature & Wildlife",
  relaxation: "Relaxation",
  nightlife: "Nightlife",
};

// ============================================================================
// Helper Functions
// ============================================================================

export function isClarificationResponse(response: ChatResponse): response is ClarificationResponse {
  return response.type === "clarification";
}

export function isItineraryResponse(response: ChatResponse): response is ItineraryResponse {
  return response.type === "itinerary";
}

export function isErrorResponse(response: ChatResponse): response is ErrorResponse {
  return response.type === "error";
}

export function isIntentComplete(intent: TravelIntent): boolean {
  return REQUIRED_FIELDS.every(field => {
    const value = intent[field as keyof TravelIntent];
    return value !== undefined && value !== null && value !== "";
  });
}

export function getMissingFields(intent: TravelIntent): string[] {
  return REQUIRED_FIELDS.filter(field => {
    const value = intent[field as keyof TravelIntent];
    return value === undefined || value === null || value === "";
  });
}

export function getProgressPercentage(intent: TravelIntent): number {
  const total = REQUIRED_FIELDS.length;
  const completed = total - getMissingFields(intent).length;
  return Math.round((completed / total) * 100);
}

"""Prompt templates for follow-up handler chain."""

FOLLOWUP_TYPE_DETECTION_PROMPT = """You are a travel planning assistant. Classify the user's latest message based on the conversation context.

CONVERSATION HISTORY:
{conversation_history}

CURRENT TRAVEL INTENT:
{current_intent}

LATEST USER MESSAGE:
{message}

Classify this message into ONE of these categories:

1. "clarification" - User is answering questions about their trip (e.g., "5 days", "mid budget", "Cebu")
2. "modification" - User wants to change something in their existing plan (e.g., "make it 7 days instead", "change destination to Palawan")
3. "new_intent" - User is providing completely new trip information (e.g., "Actually I want to go to Baguio")
4. "unsure" - User doesn't know what they want (e.g., "I'm not sure", "I don't know where to go", "what do you suggest?")
5. "unknown" - Message is unclear or unrelated to travel planning

Respond with JSON only:
{{
    "type": "<category>",
    "confidence": <0.0-1.0>,
    "reasoning": "<brief explanation>"
}}"""

MODIFICATION_DETECTION_PROMPT = """You are a travel planning assistant. Extract the modification request from the user's message.

CURRENT TRAVEL INTENT:
{current_intent}

USER MESSAGE:
{message}

Identify what the user wants to modify. Valid modification types:
- "change": Replace a value (e.g., "change destination to Palawan")
- "add": Add to a list (e.g., "add more beach activities")
- "remove": Remove from a list (e.g., "no more hiking")
- "extend": Increase a value (e.g., "extend to 7 days", "add 2 more days")
- "shorten": Decrease a value (e.g., "shorten the trip")

Valid targets: destination, days, budget, companions, travel_style

Respond with JSON only:
{{
    "action": "<action_type>",
    "target": "<what_to_modify>",
    "new_value": <new_value_or_null>,
    "confidence": <0.0-1.0>
}}

Examples:
- "Make it 5 days instead of 3" -> {{"action": "change", "target": "days", "new_value": 5, "confidence": 0.95}}
- "Can we extend the trip by 2 days" -> {{"action": "extend", "target": "days", "new_value": 2, "confidence": 0.9}}
- "Change to Palawan instead" -> {{"action": "change", "target": "destination", "new_value": "Palawan", "confidence": 0.95}}
- "I want more adventure activities" -> {{"action": "add", "target": "travel_style", "new_value": ["adventure"], "confidence": 0.85}}"""

SUGGESTION_EXTRACTION_PROMPT = """You are a Philippine travel expert. Extract destination suggestions from search results that match the user's preferences.

USER PREFERENCES:
- Companions: {companions}
- Travel Style: {travel_style}
- Budget: {budget}

SEARCH RESULTS:
{search_results}

Extract 3-5 destination suggestions. For each:
1. Name of destination (must be in the Philippines)
2. A compelling reason why it matches their preferences (1-2 sentences)
3. List of travel styles it's best for

Respond with JSON only:
{{
    "suggestions": [
        {{
            "destination": "Boracay",
            "reason": "Perfect for families with kids due to calm waters and kid-friendly resorts.",
            "best_for": ["beach", "relaxation", "nightlife"]
        }}
    ]
}}"""

STATIC_SUGGESTIONS = {
    "beach": [
        {
            "destination": "Boracay",
            "reason": "Famous White Beach, vibrant nightlife, water sports.",
            "best_for": ["beach", "nightlife", "relaxation"],
        },
        {
            "destination": "El Nido, Palawan",
            "reason": "Stunning lagoons, island hopping, crystal waters.",
            "best_for": ["beach", "nature", "adventure"],
        },
        {
            "destination": "Coron, Palawan",
            "reason": "World-class diving, pristine lakes, dramatic scenery.",
            "best_for": ["beach", "adventure", "nature"],
        },
        {
            "destination": "Siargao",
            "reason": "Surfing capital, laid-back vibe, beautiful beaches.",
            "best_for": ["beach", "adventure", "nature"],
        },
    ],
    "adventure": [
        {
            "destination": "Cebu",
            "reason": "Canyoneering at Kawasan Falls, whale sharks, diving.",
            "best_for": ["adventure", "nature", "beach"],
        },
        {
            "destination": "Siargao",
            "reason": "Surfing, cliff diving, island hopping, rock pools.",
            "best_for": ["adventure", "beach", "nature"],
        },
        {
            "destination": "Davao",
            "reason": "Mt. Apo hiking, Philippine Eagle, white water rafting.",
            "best_for": ["adventure", "nature"],
        },
    ],
    "culture": [
        {
            "destination": "Vigan, Ilocos",
            "reason": "Spanish colonial architecture, heritage walking tours.",
            "best_for": ["culture", "food"],
        },
        {
            "destination": "Manila",
            "reason": "Intramuros, museums, historical sites, vibrant food scene.",
            "best_for": ["culture", "food", "nightlife"],
        },
        {
            "destination": "Cebu City",
            "reason": "Oldest city in PH, Magellan's Cross, heritage sites.",
            "best_for": ["culture", "food"],
        },
    ],
    "food": [
        {
            "destination": "Manila",
            "reason": "Diverse culinary scene from street food to fine dining.",
            "best_for": ["food", "culture", "nightlife"],
        },
        {
            "destination": "Cebu",
            "reason": "Lechon capital, fresh seafood, local delicacies.",
            "best_for": ["food", "beach", "culture"],
        },
        {
            "destination": "Iloilo",
            "reason": "La Paz Batchoy, heritage dishes, food festivals.",
            "best_for": ["food", "culture"],
        },
    ],
    "nature": [
        {
            "destination": "Palawan",
            "reason": "Underground River, pristine forests, diverse wildlife.",
            "best_for": ["nature", "beach", "adventure"],
        },
        {
            "destination": "Bohol",
            "reason": "Chocolate Hills, tarsiers, Loboc River cruise.",
            "best_for": ["nature", "culture", "beach"],
        },
        {
            "destination": "Batanes",
            "reason": "Rolling hills, dramatic cliffs, unspoiled landscapes.",
            "best_for": ["nature", "culture"],
        },
    ],
    "relaxation": [
        {
            "destination": "Boracay",
            "reason": "Beachfront spas, sunset views, chill atmosphere.",
            "best_for": ["relaxation", "beach"],
        },
        {
            "destination": "Batangas",
            "reason": "Nearby beach resorts, diving, quick getaway.",
            "best_for": ["relaxation", "beach"],
        },
        {
            "destination": "Tagaytay",
            "reason": "Cool climate, Taal views, cafes, relaxation.",
            "best_for": ["relaxation", "food", "nature"],
        },
    ],
    "nightlife": [
        {
            "destination": "Boracay",
            "reason": "Beach parties, bars, live music until dawn.",
            "best_for": ["nightlife", "beach"],
        },
        {
            "destination": "Makati/BGC, Manila",
            "reason": "Rooftop bars, clubs, live entertainment.",
            "best_for": ["nightlife", "food", "culture"],
        },
    ],
}

COMPANION_SUGGESTION_FILTERS = {
    "family": {
        "avoid": ["nightlife"],
        "prioritize": ["beach", "nature", "culture"],
        "context": "family-friendly with activities for all ages",
    },
    "solo": {
        "avoid": [],
        "prioritize": ["adventure", "culture", "nature"],
        "context": "safe, social, easy to navigate",
    },
    "couple": {
        "avoid": [],
        "prioritize": ["beach", "relaxation", "food"],
        "context": "romantic spots and couple activities",
    },
    "group": {
        "avoid": [],
        "prioritize": ["adventure", "nightlife", "beach"],
        "context": "activities for various interests, group-friendly",
    },
}

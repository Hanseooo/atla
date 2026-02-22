"""
AI agent module for travel planning.

This package contains the core AI components used to power travel planning
features, including:

- Large language model (LLM) interfaces and configuration.
- Tooling and utilities for querying external travel services (e.g., flights,
  hotels, and activities).
- Orchestration logic (chains/agents) for intent extraction, constraint
  handling, and itinerary generation.
- Shared schemas and data models used to represent user intents, search
  parameters, and structured travel itineraries.

Modules within ``backend.app.ai`` are intended to be composed by higher-level
API endpoints to transform natural language travel requests into actionable,
structured responses.
"""
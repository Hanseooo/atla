"""Supabase client initialization for backend.

This module initializes the Supabase client with service role key for backend operations.
The service role key has admin privileges and bypasses RLS policies.
"""
from supabase import create_client, Client
from app.config import settings

# Initialize Supabase client with service role key
# Service role key has full admin access and can verify any user's token
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

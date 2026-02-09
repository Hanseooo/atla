"""Add username unique constraint and user creation trigger

Revision ID: 744a589777ad
Revises: dd94b48b3f25
Create Date: 2026-02-09 03:07:38.968346

NOTE: The trigger on auth.users only works in Supabase (production).
For local development, profile creation is handled by the application.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '744a589777ad'
down_revision: Union[str, Sequence[str], None] = 'dd94b48b3f25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add unique constraint on username
    op.create_unique_constraint('uq_user_profiles_username', 'user_profiles', ['username'])
    
    # 2. Create index for case-insensitive username lookups
    op.create_index('ix_user_profiles_username_lower', 'user_profiles', [sa.text('LOWER(username)')], unique=False)
    
    # 3. Make username nullable (for trigger-created profiles)
    # Note: username was already nullable in the initial migration, but let's ensure it
    op.alter_column('user_profiles', 'username', 
                    existing_type=sa.String(length=50),
                    nullable=True)
    
    # 4. Create trigger function (works in any PostgreSQL)
    op.execute("""
        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = public
        AS $$
        BEGIN
            -- Create user profile with minimal data (username will be added later via API)
            INSERT INTO public.user_profiles (
                id,
                username,
                email,
                avatar_url,
                preferences,
                created_at,
                updated_at
            ) VALUES (
                NEW.id,
                NULL,  -- Username will be set via API call after signup
                NEW.email,
                NULL,
                '{}'::jsonb,
                NOW(),
                NOW()
            )
            ON CONFLICT (id) DO NOTHING;
            
            RETURN NEW;
        EXCEPTION
            WHEN OTHERS THEN
                -- Log error but don't block signup
                RAISE WARNING 'Error creating user profile: %', SQLERRM;
                RETURN NEW;
        END;
        $$;
    """)
    
    # 5. Create trigger on auth.users table (only if auth schema exists - Supabase only)
    # Use DO block to handle missing schema gracefully
    op.execute("""
        DO $$
        BEGIN
            -- Check if auth schema exists (Supabase environment)
            IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth') THEN
                -- Check if auth.users table exists
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'auth' AND table_name = 'users') THEN
                    -- Create trigger
                    CREATE TRIGGER on_auth_user_created
                    AFTER INSERT ON auth.users
                    FOR EACH ROW
                    EXECUTE FUNCTION public.handle_new_user();
                    
                    RAISE NOTICE 'Created trigger on auth.users';
                ELSE
                    RAISE NOTICE 'auth.users table not found - trigger not created';
                END IF;
            ELSE
                RAISE NOTICE 'auth schema not found - running in local development mode';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Drop trigger (only if it exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth') THEN
                DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
            END IF;
        END $$;
    """)
    
    # 2. Drop function
    op.execute("DROP FUNCTION IF EXISTS public.handle_new_user();")
    
    # 3. Drop index
    op.drop_index('ix_user_profiles_username_lower', table_name='user_profiles')
    
    # 4. Drop unique constraint
    op.drop_constraint('uq_user_profiles_username', 'user_profiles', type_='unique')

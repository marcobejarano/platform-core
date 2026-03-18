from supabase import Client, create_client

from services.auth_service.app.settings import settings


def get_admin_supabase_client() -> Client:
    return create_client(
        settings.auth_service_supabase_url,
        settings.auth_service_supabase_secret_key.get_secret_value(),
    )

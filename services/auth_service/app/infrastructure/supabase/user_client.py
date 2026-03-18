from supabase import Client, create_client

from services.auth_service.app.settings import settings


def get_user_supabase_client(access_token: str) -> Client:
    client = create_client(
        settings.auth_service_supabase_url,
        settings.auth_service_supabase_publishable_key,
    )

    client.auth.set_session(
        access_token=access_token,
        refresh_token="",  # Not required for mutations
    )

    return client

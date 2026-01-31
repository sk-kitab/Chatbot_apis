from supabase import create_client, Client
from modules.config import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

async def sign_up_user(email: str, password: str):
    return supabase.auth.sign_up({"email": email, "password": password})

async def login_user(email: str, password: str):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

async def get_user(token: str):
    return supabase.auth.get_user(token)

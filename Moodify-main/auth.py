import os
import hashlib
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client():
    """Creates and returns a Supabase client."""
    try:
        import streamlit as st
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Supabase credentials not found.")

    return create_client(url, key)


def hash_password(password):
    """Hashes a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def sign_up(email, username, password, country):
    """
    Registers a new user.
    Returns (success: bool, message: str, user: dict or None)
    """
    try:
        supabase = get_supabase_client()

        # Check if email already exists
        existing = supabase.table("users").select("id").eq("email", email).execute()
        if existing.data:
            return False, "An account with this email already exists.", None

        # Check if username already exists
        existing_username = supabase.table("users").select("id").eq("username", username).execute()
        if existing_username.data:
            return False, "This username is already taken.", None

        # Create user
        hashed_pw = hash_password(password)
        user_data = {
            "email": email,
            "username": username,
            "password_hash": hashed_pw,
            "country": country
        }

        result = supabase.table("users").insert(user_data).execute()

        if result.data:
            user = result.data[0]
            return True, f"Welcome to Moodify, {username}!", user
        else:
            return False, "Registration failed. Please try again.", None

    except Exception as e:
        return False, f"Error: {str(e)}", None


def sign_in(email, password):
    """
    Logs in an existing user.
    Returns (success: bool, message: str, user: dict or None)
    """
    try:
        supabase = get_supabase_client()
        hashed_pw = hash_password(password)

        result = supabase.table("users").select("*").eq("email", email).eq("password_hash", hashed_pw).execute()

        if result.data:
            user = result.data[0]
            return True, f"Welcome back, {user['username']}!", user
        else:
            return False, "Incorrect email or password.", None

    except Exception as e:
        return False, f"Error: {str(e)}", None


def update_country(user_id, country):
    """Updates the user's country preference."""
    try:
        supabase = get_supabase_client()
        supabase.table("users").update({"country": country}).eq("id", user_id).execute()
        return True
    except Exception:
        return False

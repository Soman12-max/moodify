import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

MOOD_SEARCH_TERMS = {
    "sadness": {
        "calm":     "relaxing ambient peaceful",
        "focus":    "study focus instrumental",
        "energise": "upbeat motivational happy",
    },
    "anger": {
        "calm":     "calming meditation peaceful",
        "focus":    "deep focus concentration",
        "energise": "positive energy upbeat",
    },
    "fear": {
        "calm":     "soothing gentle calm",
        "focus":    "focus instrumental steady",
        "energise": "confidence boost upbeat",
    },
    "disgust": {
        "calm":     "peaceful relaxing soft",
        "focus":    "instrumental focus minimal",
        "energise": "happy feel good dance",
    },
    "joy": {
        "calm":     "chill mellow relaxed",
        "focus":    "lo-fi focus productive",
        "energise": "party dance high energy",
    },
    "surprise": {
        "calm":     "ambient relaxing soft",
        "focus":    "focus deep work",
        "energise": "energetic upbeat fun",
    },
    "neutral": {
        "calm":     "relaxing peaceful ambient",
        "focus":    "focus study instrumental",
        "energise": "upbeat energetic motivational",
    },
}


def get_recommendations(detected_emotion, target_mood, limit=8):
    """
    Searches Spotify for tracks matching the mood transition.
    Reads credentials at call time so st.secrets is fully loaded.
    """
    try:
        # Read credentials at call time not import time
        client_id = None
        client_secret = None

        # Try st.secrets first
        try:
            import streamlit as st
            client_id = st.secrets["SPOTIPY_CLIENT_ID"]
            client_secret = st.secrets["SPOTIPY_CLIENT_SECRET"]
        except Exception:
            pass

        # Fall back to environment variables
        if not client_id:
            client_id = os.getenv("SPOTIPY_CLIENT_ID")
        if not client_secret:
            client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

        if not client_id or not client_secret:
            return {"error": "Spotify credentials not found. Please check your secrets configuration."}

        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        emotion = detected_emotion.lower()
        target = target_mood.lower()

        if emotion not in MOOD_SEARCH_TERMS:
            emotion = "neutral"

        query = MOOD_SEARCH_TERMS[emotion][target]
        results = sp.search(q=query, type="track", limit=limit)

        tracks = []
        for track in results["tracks"]["items"]:
            tracks.append({
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "uri": track["uri"],
                "url": track["external_urls"]["spotify"]
            })

        return tracks

    except spotipy.exceptions.SpotifyException as e:
        return {"error": f"Spotify API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
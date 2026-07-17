import os
from supabase import create_client
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


def save_session(user_id, user_input, mood_result, target_mood, country, tracks, feedback=None):
    """
    Saves a mood session to the database.

    Args:
        user_id: UUID of the logged in user
        user_input: the text the user typed
        mood_result: dict returned by detect_mood()
        target_mood: calm, focus, or energise
        country: user's selected country
        tracks: list of track dicts returned by get_recommendations()
        feedback: optional feedback string from user
    """
    try:
        supabase = get_supabase_client()

        # Simplify tracks for storage — only store essential fields
        tracks_data = [
            {
                "name": t["name"],
                "artist": t["artist"],
                "url": t["url"],
                "is_local": t.get("is_local", False)
            }
            for t in tracks
        ] if tracks else []

        session_data = {
            "user_id": user_id,
            "user_input": user_input,
            "primary_emotion": mood_result.get("primary_emotion", "neutral"),
            "primary_category": mood_result.get("primary_category", "neutral"),
            "confidence": float(mood_result.get("confidence", 0.0)),
            "intensity": mood_result.get("intensity", "Low"),
            "sentiment": mood_result.get("sentiment", "neutral"),
            "top_emotions": mood_result.get("top_emotions", []),
            "keywords": mood_result.get("keywords", []),
            "target_mood": target_mood,
            "country": country,
            "tracks_returned": tracks_data,
            "feedback": feedback
        }

        result = supabase.table("mood_sessions").insert(session_data).execute()
        return True if result.data else False

    except Exception as e:
        print(f"Error saving session: {e}")
        return False


def save_feedback(session_id, feedback):
    """Updates feedback for an existing session."""
    try:
        supabase = get_supabase_client()
        supabase.table("mood_sessions").update(
            {"feedback": feedback}
        ).eq("id", session_id).execute()
        return True
    except Exception:
        return False


def get_user_history(user_id, limit=20):
    """
    Retrieves the most recent mood sessions for a user.
    Returns list of session dicts.
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("mood_sessions").select("*").eq(
            "user_id", user_id
        ).order("created_at", desc=True).limit(limit).execute()

        return result.data if result.data else []

    except Exception as e:
        print(f"Error fetching history: {e}")
        return []


def get_mood_stats(user_id):
    """
    Calculates mood statistics for the dashboard.
    Returns dict with emotion counts, target mood counts,
    average confidence, and feedback summary.
    """
    try:
        sessions = get_user_history(user_id, limit=100)

        if not sessions:
            return None

        emotion_counts = {}
        target_counts = {}
        feedback_counts = {"Yes, calmer": 0, "Feeling energised": 0, "Not really": 0}
        confidences = []
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}

        for s in sessions:
            # Count emotions
            emotion = s.get("primary_emotion", "unknown")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

            # Count target moods
            target = s.get("target_mood", "unknown")
            target_counts[target] = target_counts.get(target, 0) + 1

            # Count feedback
            fb = s.get("feedback")
            if fb and fb in feedback_counts:
                feedback_counts[fb] += 1

            # Collect confidence scores
            conf = s.get("confidence", 0)
            if conf:
                confidences.append(float(conf))

            # Count sentiments
            sent = s.get("sentiment", "neutral")
            if sent in sentiments:
                sentiments[sent] += 1

        avg_confidence = round(sum(confidences) / len(confidences) * 100, 1) if confidences else 0

        return {
            "total_sessions": len(sessions),
            "emotion_counts": emotion_counts,
            "target_counts": target_counts,
            "feedback_counts": feedback_counts,
            "avg_confidence": avg_confidence,
            "sentiments": sentiments
        }

    except Exception as e:
        print(f"Error calculating stats: {e}")
        return None

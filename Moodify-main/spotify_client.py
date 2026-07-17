import os
import spotipy
import random
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from location import build_local_query, split_playlist

load_dotenv()

# ── Dynamic mood search terms ─────────────────────────────────
# Built around emotion category + target mood combinations
# Uses richer, more varied queries than the old fixed keyword sets

MOOD_QUERIES = {
    "sadness": {
        "calm":       ["sad acoustic calm", "melancholic chill", "healing gentle music"],
        "focus":      ["sad focus instrumental", "melancholic study music", "emotional concentration"],
        "energise":   ["uplifting sad to happy", "motivational overcome sadness", "energetic emotional"],
        "happy":      ["cheer up sad", "happy uplift from sadness", "feel good overcome sadness"],
        "sleep":      ["sad lullaby sleep", "melancholic sleep music", "gentle sad bedtime"],
        "confidence": ["sad to confident", "overcome sadness confidence", "empowerment from sadness"],
        "romance":    ["sad romance music", "melancholic love songs", "emotional romantic"],
        "workout":    ["sad to powerful workout", "overcome sadness exercise", "emotional gym music"],
    },
    "anger": {
        "calm":       ["anger release calm", "soothing after stress", "peaceful meditation anger"],
        "focus":      ["intense focus work", "anger channeled concentration", "deep work power"],
        "energise":   ["anger release energy", "powerful workout motivation", "intense energetic"],
        "happy":      ["anger to happiness", "calm down feel good", "positive after anger"],
        "sleep":      ["anger release sleep", "calm down bedtime", "soothing after frustration"],
        "confidence": ["controlled anger confidence", "powerful assertive music", "strength from anger"],
        "romance":    ["passion romance music", "intense love songs", "emotional romantic passion"],
        "workout":    ["angry workout music", "rage gym motivation", "intense exercise anger"],
    },
    "fear": {
        "calm":       ["anxiety relief calm", "fear soothing gentle", "peaceful reassuring music"],
        "focus":      ["overcome anxiety focus", "calm concentration fearless", "steady mind focus"],
        "energise":   ["confidence boost fearless", "overcome fear energetic", "empowerment upbeat"],
        "happy":      ["fear to joy music", "overcome anxiety happy", "relief happy music"],
        "sleep":      ["anxiety sleep music", "fear relief bedtime", "calming sleep anxiety"],
        "confidence": ["fearless confidence music", "overcome fear empowerment", "brave strong music"],
        "romance":    ["vulnerable romantic music", "gentle love songs fear", "soft romantic reassuring"],
        "workout":    ["fearless workout music", "brave exercise motivation", "conquer fear gym"],
    },
    "disgust": {
        "calm":       ["cleansing peaceful music", "refresh calm reset", "soothing positive reset"],
        "focus":      ["clear mind focus", "reset concentration music", "minimal focus instrumental"],
        "energise":   ["positive reset energy", "feel good happy dance", "upbeat mood boost"],
        "happy":      ["disgust to happiness", "feel clean happy music", "positive refresh mood"],
        "sleep":      ["cleansing sleep music", "reset bedtime calm", "peaceful sleep refresh"],
        "confidence": ["fresh start confidence", "reset empowerment music", "new beginning motivation"],
        "romance":    ["fresh romance music", "new love positive", "clean romantic vibes"],
        "workout":    ["reset workout motivation", "fresh start exercise", "cleansing gym music"],
    },
    "joy": {
        "calm":       ["happy chill relaxed", "joyful mellow wind down", "content peaceful calm"],
        "focus":      ["happy focus productive", "positive energy concentration", "upbeat work music"],
        "energise":   ["euphoric dance party", "maximum energy happy", "high energy celebration"],
        "happy":      ["pure happiness music", "joyful celebration songs", "feel amazing happy"],
        "sleep":      ["happy lullaby sleep", "joyful bedtime calm", "content sleep music"],
        "confidence": ["joyful confidence music", "happy empowerment songs", "celebrate yourself"],
        "romance":    ["happy love songs", "joyful romance music", "celebration love"],
        "workout":    ["happy workout music", "joyful exercise motivation", "fun gym songs"],
    },
    "surprise": {
        "calm":       ["unexpected calm beautiful", "soothing discovery music", "peaceful wonder"],
        "focus":      ["curious focus exploration", "wonder concentration music", "discovery work"],
        "energise":   ["exciting surprise energetic", "spontaneous upbeat fun", "adventure energy"],
        "happy":      ["surprised happiness music", "unexpected joy songs", "delightful happy music"],
        "sleep":      ["peaceful surprise calm", "wonder bedtime music", "gentle discovery sleep"],
        "confidence": ["surprise confidence boost", "unexpected empowerment", "bold surprise music"],
        "romance":    ["surprise romantic music", "unexpected love songs", "spontaneous romance"],
        "workout":    ["surprise energy workout", "unexpected motivation gym", "spontaneous exercise"],
    },
    "neutral": {
        "calm":       ["relaxing ambient peaceful", "neutral calm background", "soft instrumental"],
        "focus":      ["focus study instrumental", "neutral concentration music", "lo-fi work"],
        "energise":   ["upbeat energetic motivational", "neutral to energised", "positive energy boost"],
        "happy":      ["neutral to happy music", "feel good from neutral", "mood lift songs"],
        "sleep":      ["neutral sleep music", "ambient bedtime sounds", "peaceful sleep instrumental"],
        "confidence": ["neutral confidence boost", "motivation from neutral", "empowerment build up"],
        "romance":    ["neutral romantic music", "ambient love songs", "soft romantic background"],
        "workout":    ["neutral workout motivation", "build up exercise music", "steady gym music"],
    },
    "excitement": {
        "calm":       ["excitement wind down", "post excitement calm", "relaxing after fun"],
        "focus":      ["excited focus channel", "high energy concentration", "motivated work music"],
        "energise":   ["maximum excitement energy", "hype celebration music", "euphoric dance"],
        "happy":      ["excited happiness music", "hype happy songs", "celebration excitement"],
        "sleep":      ["excitement to sleep", "wind down after excitement", "calm after hype"],
        "confidence": ["excited confidence music", "hype empowerment songs", "celebration strength"],
        "romance":    ["excited romantic music", "passionate love songs", "hype romance"],
        "workout":    ["excited workout music", "hype gym motivation", "maximum energy exercise"],
    },
    "anxiety": {
        "calm":       ["anxiety relief calm", "panic to peace music", "soothing anxiety healing"],
        "focus":      ["anxiety focus calm", "nervous energy concentration", "steady anxious mind"],
        "energise":   ["anxiety to confidence", "nervous to powerful", "empowerment overcome anxiety"],
        "happy":      ["anxiety to happiness", "worry to joy music", "relief happy songs"],
        "sleep":      ["anxiety sleep music", "worry relief bedtime", "calm anxious mind sleep"],
        "confidence": ["anxiety confidence boost", "overcome worry empowerment", "brave despite anxiety"],
        "romance":    ["anxious romantic music", "gentle reassuring love", "soft anxiety romance"],
        "workout":    ["anxiety release workout", "nervous energy gym", "channel anxiety exercise"],
    },
    "grief": {
        "calm":       ["grief healing music", "loss peaceful comfort", "mourning gentle calm"],
        "focus":      ["grief processing focus", "healing concentration music", "moving forward instrumental"],
        "energise":   ["grief to hope music", "healing uplift energy", "resilience after loss"],
        "happy":      ["grief to acceptance", "healing happy music", "hope after loss songs"],
        "sleep":      ["grief sleep music", "loss comfort bedtime", "healing rest music"],
        "confidence": ["grief resilience music", "strength after loss", "healing empowerment"],
        "romance":    ["grief romantic memories", "bittersweet love songs", "healing romance music"],
        "workout":    ["grief release workout", "healing exercise music", "strength through loss gym"],
    },
}


def get_spotify_client():
    """Creates Spotify client reading credentials at call time."""
    client_id = None
    client_secret = None

    try:
        import streamlit as st
        client_id = st.secrets["SPOTIPY_CLIENT_ID"]
        client_secret = st.secrets["SPOTIPY_CLIENT_SECRET"]
    except Exception:
        pass

    if not client_id:
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
    if not client_secret:
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("Spotify credentials not found.")

    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def search_tracks(sp, query, limit=8, offset=None):
    """Executes a Spotify search and returns formatted track list."""
    try:
        # Random offset makes Spotify return different results each time
        if offset is None:
            offset = random.randint(0, 40)

        results = sp.search(q=query, type="track", limit=limit, offset=offset)
        tracks = []
        for track in results["tracks"]["items"]:
            tracks.append({
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "uri": track["uri"],
                "url": track["external_urls"]["spotify"],
                "popularity": track.get("popularity", 0)
            })

        # Shuffle the results so order varies each session
        random.shuffle(tracks)
        return tracks
    except Exception:
        return []


def build_global_query(mood_result, target_mood, keywords):
    """
    Builds a dynamic global search query using:
    - Primary emotion category
    - KeyBERT extracted keywords
    - Target mood
    - Random query rotation
    """
    category = mood_result.get("primary_category", "neutral")

    # Get query options for this emotion/target combination
    query_options = MOOD_QUERIES.get(category, MOOD_QUERIES["neutral"])
    base_queries = query_options.get(target_mood, query_options["calm"])

    # Randomly pick from available query options each time
    base_query = random.choice(base_queries)

    # Enrich query with extracted keywords if available
    if keywords:
        # Randomly use 1 or 2 keywords for variety
        num_keywords = random.randint(1, min(2, len(keywords)))
        selected_keywords = random.sample(keywords, num_keywords)
        keyword_str = " ".join(selected_keywords)
        enriched_query = f"{base_query} {keyword_str}"
    else:
        enriched_query = base_query

    return enriched_query


def get_recommendations(mood_result, target_mood, country="Global", limit=8):
    """
    Main recommendation function.
    Fetches global and local tracks then merges into a 50/50 playlist.

    Args:
        mood_result: dict returned by detect_mood()
        target_mood: "calm", "focus", or "energise"
        country: user's selected country
        limit: total number of tracks to return

    Returns:
        list of track dicts or dict with error key
    """
    try:
        sp = get_spotify_client()
        keywords = mood_result.get("keywords", [])

        # ── Global query ──────────────────────────────────────
        global_query = build_global_query(mood_result, target_mood, keywords)
        global_tracks = search_tracks(sp, global_query, limit=limit)

        # ── Local query ───────────────────────────────────────
        local_query = build_local_query(country, mood_result.get("primary_category", "neutral"), target_mood)
        local_tracks = []
        if local_query:
            local_tracks = search_tracks(sp, local_query, limit=limit // 2, offset=random.randint(0, 20))

        # ── Merge into 50/50 playlist ─────────────────────────
        final_tracks = split_playlist(global_tracks, local_tracks, total=limit)

        # Tag each track as local or global for UI display
        local_uris = {t['uri'] for t in local_tracks}
        for track in final_tracks:
            track['is_local'] = track['uri'] in local_uris

        return final_tracks

    except ValueError as e:
        return {"error": str(e)}
    except spotipy.exceptions.SpotifyException as e:
        return {"error": f"Spotify API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

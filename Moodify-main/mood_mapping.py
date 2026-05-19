# Mood shift mapping
# Structure: detected_emotion -> target_mood -> Spotify audio feature ranges
# valence: musical positivity (0.0 to 1.0)
# energy: intensity and activity (0.0 to 1.0)

MOOD_MAP = {
    "sadness": {
        "calm":     {"min_valence": 0.3, "max_valence": 0.5, "min_energy": 0.1, "max_energy": 0.3},
        "focus":    {"min_valence": 0.4, "max_valence": 0.6, "min_energy": 0.3, "max_energy": 0.5},
        "energise": {"min_valence": 0.6, "max_valence": 0.9, "min_energy": 0.7, "max_energy": 1.0},
    },
    "anger": {
        "calm":     {"min_valence": 0.3, "max_valence": 0.5, "min_energy": 0.1, "max_energy": 0.3},
        "focus":    {"min_valence": 0.4, "max_valence": 0.6, "min_energy": 0.3, "max_energy": 0.5},
        "energise": {"min_valence": 0.5, "max_valence": 0.8, "min_energy": 0.6, "max_energy": 0.9},
    },
    "fear": {
        "calm":     {"min_valence": 0.4, "max_valence": 0.6, "min_energy": 0.1, "max_energy": 0.3},
        "focus":    {"min_valence": 0.5, "max_valence": 0.7, "min_energy": 0.3, "max_energy": 0.5},
        "energise": {"min_valence": 0.6, "max_valence": 0.9, "min_energy": 0.6, "max_energy": 0.9},
    },
    "disgust": {
        "calm":     {"min_valence": 0.3, "max_valence": 0.5, "min_energy": 0.1, "max_energy": 0.3},
        "focus":    {"min_valence": 0.4, "max_valence": 0.6, "min_energy": 0.3, "max_energy": 0.5},
        "energise": {"min_valence": 0.6, "max_valence": 0.9, "min_energy": 0.6, "max_energy": 0.9},
    },
    "joy": {
        "calm":     {"min_valence": 0.5, "max_valence": 0.7, "min_energy": 0.1, "max_energy": 0.3},
        "focus":    {"min_valence": 0.5, "max_valence": 0.7, "min_energy": 0.4, "max_energy": 0.6},
        "energise": {"min_valence": 0.7, "max_valence": 1.0, "min_energy": 0.8, "max_energy": 1.0},
    },
    "surprise": {
        "calm":     {"min_valence": 0.4, "max_valence": 0.6, "min_energy": 0.1, "max_energy": 0.3},
        "focus":    {"min_valence": 0.5, "max_valence": 0.7, "min_energy": 0.3, "max_energy": 0.5},
        "energise": {"min_valence": 0.6, "max_valence": 0.9, "min_energy": 0.7, "max_energy": 1.0},
    },
    "neutral": {
        "calm":     {"min_valence": 0.3, "max_valence": 0.5, "min_energy": 0.1, "max_energy": 0.3},
        "focus":    {"min_valence": 0.5, "max_valence": 0.7, "min_energy": 0.4, "max_energy": 0.6},
        "energise": {"min_valence": 0.6, "max_valence": 0.9, "min_energy": 0.7, "max_energy": 1.0},
    },
}

def get_audio_features(detected_emotion, target_mood):
    """
    Returns the Spotify audio feature ranges for a given
    detected emotion and target mood combination.
    """
    emotion = detected_emotion.lower()
    target = target_mood.lower()

    if emotion not in MOOD_MAP:
        emotion = "neutral"

    return MOOD_MAP[emotion][target]
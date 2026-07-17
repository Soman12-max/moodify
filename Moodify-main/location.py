REGIONAL_GENRES = {
    # East Africa
    "Kenya": ["afrobeats", "gengetone", "benga", "bongo flava"],
    "Tanzania": ["bongo flava", "afrobeats", "taarab"],
    "Uganda": ["afrobeats", "afropop", "kadongo kamu"],
    "Ethiopia": ["ethiopian pop", "afrobeats"],
    "Rwanda": ["afrobeats", "afropop"],

    # West Africa
    "Nigeria": ["afrobeats", "afrofusion", "juju", "afropop"],
    "Ghana": ["highlife", "afrobeats", "hiplife", "afropop"],
    "Senegal": ["mbalax", "afrobeats", "afropop"],
    "Ivory Coast": ["afrobeats", "coupé-décalé", "afropop"],
    "Cameroon": ["afrobeats", "bikutsi", "makossa"],

    # Southern Africa
    "South Africa": ["amapiano", "kwaito", "afro house", "gqom"],
    "Zimbabwe": ["afrobeats", "zimdancehall", "afropop"],
    "Zambia": ["afrobeats", "zambian pop"],
    "Mozambique": ["afrobeats", "marrabenta"],

    # North Africa
    "Egypt": ["arabic pop", "shaabi", "mahraganat"],
    "Morocco": ["arabic pop", "gnawa", "chaabi"],
    "Tunisia": ["arabic pop", "maluf"],

    # UK & Europe
    "United Kingdom": ["uk drill", "grime", "uk garage", "brit pop"],
    "France": ["french pop", "chanson", "afrobeats"],
    "Germany": ["schlager", "german hip hop", "electronic"],
    "Spain": ["flamenco", "latin pop", "reggaeton"],
    "Italy": ["italian pop", "cantautore"],
    "Portugal": ["fado", "portuguese pop"],

    # Americas
    "United States": ["hip hop", "r&b", "country", "pop"],
    "Brazil": ["samba", "bossa nova", "funk carioca", "forró"],
    "Colombia": ["cumbia", "vallenato", "reggaeton", "latin pop"],
    "Jamaica": ["reggae", "dancehall", "ska"],
    "Mexico": ["banda", "norteño", "latin pop", "mariachi"],

    # Asia
    "India": ["bollywood", "indian classical", "indie pop"],
    "South Korea": ["k-pop", "k-indie", "k-r&b"],
    "Japan": ["j-pop", "city pop", "j-rock"],
    "Philippines": ["opm", "p-pop", "kundiman"],

    # Default
    "Global": []
}

# ── Target mood to genre style modifier ───────────────────────
MOOD_GENRE_STYLE = {
    "calm":       "acoustic chill",
    "focus":      "instrumental",
    "energise":   "dance",
    "happy":      "feel good",
    "sleep":      "ambient sleep",
    "confidence": "empowerment",
    "romance":    "romantic",
    "workout":    "gym motivation"
}

# ── Country list for UI dropdown ──────────────────────────────
COUNTRY_LIST = sorted(REGIONAL_GENRES.keys())


def get_local_genres(country):
    """Returns list of local genres for a given country."""
    return REGIONAL_GENRES.get(country, [])


def build_local_query(country, detected_emotion, target_mood):
    """
    Builds a localised Spotify search query by combining
    regional genres with mood and emotion context.
    """
    local_genres = get_local_genres(country)

    if not local_genres or country == "Global":
        return None

    # Pick the first two most representative local genres
    primary_genre = local_genres[0]
    secondary_genre = local_genres[1] if len(local_genres) > 1 else ""

    style = MOOD_GENRE_STYLE.get(target_mood, "")

    if secondary_genre:
        query = f"{primary_genre} {secondary_genre} {style}".strip()
    else:
        query = f"{primary_genre} {style}".strip()

    return query


def split_playlist(global_tracks, local_tracks, total=8):
    """
    Combines global and local tracks into a 50/50 playlist.
    Falls back to all global if no local tracks available.
    """
    if not local_tracks:
        return global_tracks[:total]

    half = total // 2
    combined = []

    # Add local tracks first (up to half)
    combined.extend(local_tracks[:half])

    # Fill remaining with global tracks not already in list
    local_uris = {t['uri'] for t in combined}
    for track in global_tracks:
        if track['uri'] not in local_uris and len(combined) < total:
            combined.append(track)

    return combined

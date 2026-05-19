import streamlit as st
from mood_detector import detect_mood
from spotify_client import get_recommendations

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Moodify",
    page_icon="🎵",
    layout="centered"
)

# ── Spotify-inspired dark theme ───────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0a;
    color: #ffffff;
}

.stApp {
    background: linear-gradient(180deg, #1a1a2e 0%, #0a0a0a 40%);
    min-height: 100vh;
}

#MainMenu, footer, header {visibility: hidden;}

.hero {
    text-align: center;
    padding: 3rem 0 2rem 0;
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #1DB954 0%, #1ed760 50%, #17a74a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}

.hero-sub {
    color: #a0a0a0;
    font-size: 1.05rem;
    font-weight: 300;
    letter-spacing: 0.3px;
}

.input-card {
    background: #181818;
    border-radius: 16px;
    padding: 2rem;
    border: 1px solid #282828;
    margin-bottom: 1.5rem;
}

.stTextArea textarea {
    background-color: #282828 !important;
    color: #ffffff !important;
    border: 1px solid #3e3e3e !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 14px !important;
}

.stTextArea textarea:focus {
    border: 1px solid #1DB954 !important;
    box-shadow: 0 0 0 2px rgba(29,185,84,0.15) !important;
}

.stTextArea textarea::placeholder {
    color: #6a6a6a !important;
}

.stSelectbox > div > div {
    background-color: #282828 !important;
    color: #ffffff !important;
    border: 1px solid #3e3e3e !important;
    border-radius: 10px !important;
}

.stTextArea label, .stSelectbox label {
    color: #b3b3b3 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}

.stButton > button {
    background: #1DB954 !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.75rem 2.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: #1ed760 !important;
    transform: scale(1.02) !important;
}

.transition-pill {
    background: linear-gradient(135deg, #1a2e1a, #1e3a1e);
    border: 1px solid #1DB954;
    border-radius: 50px;
    padding: 0.6rem 1.5rem;
    text-align: center;
    font-size: 0.9rem;
    color: #1DB954;
    margin: 1rem 0;
}

.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #ffffff;
    margin: 1.5rem 0 1rem 0;
}

.track-card {
    background: #181818;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    border: 1px solid #282828;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.track-card:hover {
    background: #282828;
    border-color: #3e3e3e;
}

.track-number {
    color: #6a6a6a;
    font-size: 0.85rem;
    min-width: 20px;
    text-align: center;
}

.track-name {
    font-size: 0.95rem;
    font-weight: 500;
    color: #ffffff;
    margin-bottom: 2px;
}

.track-artist {
    font-size: 0.82rem;
    color: #a0a0a0;
}

.track-link {
    color: #1DB954 !important;
    text-decoration: none !important;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.stMetric {
    background: #181818 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    border: 1px solid #282828 !important;
}

.stMetric label {
    color: #a0a0a0 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

.stMetric [data-testid="stMetricValue"] {
    color: #1DB954 !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
}

.divider {
    border: none;
    border-top: 1px solid #282828;
    margin: 1.5rem 0;
}

.stAlert {
    background: #181818 !important;
    border-radius: 10px !important;
    border-left: 3px solid #1DB954 !important;
    color: #b3b3b3 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Moodify</div>
    <div class="hero-sub">AI-powered music therapy for your emotions</div>
</div>
""", unsafe_allow_html=True)

# ── Input card ────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)

user_input = st.text_area(
    "How are you feeling right now?",
    placeholder="e.g. I feel anxious and overwhelmed today...",
    height=110
)

target_mood = st.selectbox(
    "Target mood",
    options=["calm", "focus", "energise"],
    format_func=lambda x: {
        "calm": "😌  Calm — wind down and relax",
        "focus": "🎯  Focus — sharpen your concentration",
        "energise": "⚡  Energise — boost your energy"
    }[x]
)

st.markdown('</div>', unsafe_allow_html=True)

if st.button("Generate My Playlist"):
    if not user_input.strip():
        st.warning("Please describe how you're feeling first.")
    elif len(user_input.strip()) < 5:
        st.warning("Please give a little more detail about how you're feeling.")
    elif len(user_input.strip()) > 500:
        st.warning("Please keep your description under 500 characters.")
    else:
        with st.spinner("Analysing your mood..."):
            detected_emotion, confidence = detect_mood(user_input)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Detected Emotion", detected_emotion.capitalize())
        with col2:
            st.metric("Confidence", f"{int(confidence * 100)}%")

        st.markdown(f"""
        <div class="transition-pill">
            Shifting you from <strong>{detected_emotion}</strong> → <strong>{target_mood}</strong>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Curating your playlist..."):
            tracks = get_recommendations(detected_emotion, target_mood)

        if isinstance(tracks, dict) and "error" in tracks:
            st.error(f"Spotify error: {tracks['error']}")
        else:
            st.markdown('<div class="section-header">Your Playlist</div>', unsafe_allow_html=True)
            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            for i, track in enumerate(tracks, 1):
                st.markdown(f"""
                <div class="track-card">
                    <div class="track-number">{i}</div>
                    <div style="flex:1">
                        <div class="track-name">{track['name']}</div>
                        <div class="track-artist">{track['artist']}</div>
                    </div>
                    <a class="track-link" href="{track['url']}" target="_blank">Open ↗</a>
                </div>
                """, unsafe_allow_html=True)

                track_id = track['uri'].split(":")[-1]
                embed_url = f"https://open.spotify.com/embed/track/{track_id}?utm_source=generator&theme=0"
                st.components.v1.iframe(embed_url, height=80)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown('<div style="text-align:center;color:#a0a0a0;font-size:0.85rem;padding:0.5rem 0;">Did this playlist shift your mood?</div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("😌  Yes, calmer"):
                    st.success("Glad it helped!")
            with col2:
                if st.button("⚡  Feeling energised"):
                    st.success("Let's go!")
            with col3:
                if st.button("😐  Not really"):
                    st.info("Try a different target mood.")
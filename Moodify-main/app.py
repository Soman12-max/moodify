import streamlit as st
import spotipy
import plotly.graph_objects as go
import plotly.express as px
from mood_detector import detect_mood
from spotify_client import get_recommendations, get_spotify_oauth, get_spotify_from_token
from auth import sign_up, sign_in, update_country
from database import save_session, get_user_history, get_mood_stats
from location import COUNTRY_LIST

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Moodify",
    page_icon="🎵",
    layout="centered"
)

# ── Global CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

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

.hero { text-align: center; padding: 2rem 0 1.5rem 0; }
.hero-title {
    font-size: 3rem; font-weight: 700; letter-spacing: -1px;
    background: linear-gradient(135deg, #1DB954 0%, #1ed760 50%, #17a74a 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 0.3rem;
}
.hero-sub { color: #a0a0a0; font-size: 1rem; font-weight: 300; }

.card {
    background: #181818; border-radius: 16px;
    padding: 1.5rem; border: 1px solid #282828; margin-bottom: 1rem;
}

.stTextArea textarea {
    background-color: #282828 !important; color: #ffffff !important;
    border: 1px solid #3e3e3e !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important;
}
.stTextArea textarea:focus {
    border: 1px solid #1DB954 !important;
    box-shadow: 0 0 0 2px rgba(29,185,84,0.15) !important;
}
.stTextArea textarea::placeholder { color: #6a6a6a !important; }
.stSelectbox > div > div {
    background-color: #282828 !important; color: #ffffff !important;
    border: 1px solid #3e3e3e !important; border-radius: 10px !important;
}
.stTextInput > div > div > input {
    background-color: #282828 !important; color: #ffffff !important;
    border: 1px solid #3e3e3e !important; border-radius: 10px !important;
}
.stTextArea label, .stSelectbox label, .stTextInput label {
    color: #b3b3b3 !important; font-size: 0.78rem !important;
    font-weight: 500 !important; letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
}

.stButton > button {
    background: #1DB954 !important; color: #000000 !important;
    border: none !important; border-radius: 50px !important;
    padding: 0.7rem 2rem !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important; font-weight: 700 !important;
    width: 100% !important; transition: all 0.2s ease !important;
}
.stButton > button:hover { background: #1ed760 !important; transform: scale(1.02) !important; }

.emotion-bar-container { margin: 0.4rem 0; }
.emotion-label { color: #b3b3b3; font-size: 0.82rem; margin-bottom: 3px; }
.emotion-bar-bg {
    background: #282828; border-radius: 50px;
    height: 8px; width: 100%; overflow: hidden;
}
.emotion-bar-fill {
    background: linear-gradient(90deg, #1DB954, #1ed760);
    height: 8px; border-radius: 50px;
}

.transition-pill {
    background: linear-gradient(135deg, #1a2e1a, #1e3a1e);
    border: 1px solid #1DB954; border-radius: 50px;
    padding: 0.6rem 1.5rem; text-align: center;
    font-size: 0.9rem; color: #1DB954; margin: 1rem 0;
}

.track-card {
    background: #181818; border-radius: 12px;
    padding: 0.9rem 1.2rem; margin-bottom: 0.5rem;
    border: 1px solid #282828;
}
.track-card:hover { background: #222222; border-color: #3e3e3e; }
.track-name { font-size: 0.92rem; font-weight: 500; color: #ffffff; }
.track-artist { font-size: 0.8rem; color: #a0a0a0; }
.track-badge-local {
    background: #1a2e1a; color: #1DB954; border: 1px solid #1DB954;
    border-radius: 50px; padding: 2px 10px; font-size: 0.7rem;
    font-weight: 600; display: inline-block; margin-left: 8px;
}
.track-badge-global {
    background: #1a1a2e; color: #7c7cff; border: 1px solid #7c7cff;
    border-radius: 50px; padding: 2px 10px; font-size: 0.7rem;
    font-weight: 600; display: inline-block; margin-left: 8px;
}
.track-link {
    color: #1DB954 !important; text-decoration: none !important;
    font-size: 0.78rem; font-weight: 600; text-transform: uppercase;
}

.stMetric {
    background: #181818 !important; border-radius: 12px !important;
    padding: 1rem !important; border: 1px solid #282828 !important;
}
.stMetric label { color: #a0a0a0 !important; font-size: 0.72rem !important; text-transform: uppercase !important; }
.stMetric [data-testid="stMetricValue"] { color: #1DB954 !important; font-size: 1.3rem !important; font-weight: 700 !important; }

.stTabs [data-baseweb="tab-list"] { background: #181818 !important; border-radius: 12px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: #a0a0a0 !important; border-radius: 8px !important; }
.stTabs [aria-selected="true"] { background: #1DB954 !important; color: #000000 !important; }

.section-header { font-size: 1.2rem; font-weight: 700; color: #ffffff; margin: 1rem 0 0.8rem 0; }
.divider { border: none; border-top: 1px solid #282828; margin: 1.2rem 0; }
.auth-title { font-size: 1.5rem; font-weight: 700; color: #ffffff; text-align: center; margin-bottom: 1.5rem; }
.keyword-tag {
    background: #1a2e1a; color: #1DB954; border: 1px solid #1DB954;
    border-radius: 50px; padding: 3px 12px; font-size: 0.75rem;
    display: inline-block; margin: 2px;
}
.spotify-login-btn {
    background: #1DB954; color: #000000 !important;
    padding: 0.8rem 2rem; border-radius: 50px;
    font-weight: 700; font-size: 0.95rem;
    text-decoration: none; display: inline-block;
    letter-spacing: 0.5px; text-align: center;
    width: 100%; box-sizing: border-box;
}
.spotify-login-btn:hover { background: #1ed760; }

.spotify-badge {
    background: #1a2e1a; border: 1px solid #1DB954;
    border-radius: 50px; padding: 4px 14px;
    color: #1DB954; font-size: 0.78rem; font-weight: 600;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# ── Session state initialisation ──────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "spotify_token" not in st.session_state:
    st.session_state.spotify_token = None
if "spotify_user" not in st.session_state:
    st.session_state.spotify_user = None
if "current_tracks" not in st.session_state:
    st.session_state.current_tracks = None
if "current_mood" not in st.session_state:
    st.session_state.current_mood = None
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"


# ── Helpers ───────────────────────────────────────────────────
def render_emotion_bar(label, score):
    st.markdown(f"""
    <div class="emotion-bar-container">
        <div class="emotion-label">{label.capitalize()} — {score}%</div>
        <div class="emotion-bar-bg">
            <div class="emotion-bar-fill" style="width:{min(score, 100)}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_track(i, track):
    badge = '<span class="track-badge-local">🌍 Local</span>' if track.get('is_local') else '<span class="track-badge-global">🌐 Global</span>'
    st.markdown(f"""
    <div class="track-card">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
                <span style="color:#6a6a6a;font-size:0.82rem;">{i}.</span>
                <span class="track-name"> {track['name']}</span>
                {badge}
                <div style="margin-top:3px;">
                    <span class="track-artist">{track['artist']}</span>
                </div>
            </div>
            <a class="track-link" href="{track['url']}" target="_blank">Open ↗</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    track_id = track['uri'].split(":")[-1]
    embed_url = f"https://open.spotify.com/embed/track/{track_id}?utm_source=generator&theme=0"
    st.components.v1.iframe(embed_url, height=80)


# ── AUTH PAGE ─────────────────────────────────────────────────
def render_auth():
    st.markdown("""
    <div class="hero">
        <div class="hero-title">Moodify</div>
        <div class="hero-sub">AI-powered music therapy for your emotions</div>
    </div>
    """, unsafe_allow_html=True)

    # Handle Spotify OAuth callback
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        try:
            oauth = get_spotify_oauth()
            token_info = oauth.get_access_token(code, as_dict=True)
            sp_user = spotipy.Spotify(auth=token_info['access_token'])
            spotify_profile = sp_user.current_user()
            st.session_state.spotify_token = token_info
            st.session_state.spotify_user = spotify_profile
            st.session_state.user = {
                "id": spotify_profile.get("id"),
                "username": spotify_profile.get("display_name", "Spotify User"),
                "email": spotify_profile.get("email", ""),
                "country": "Global"
            }
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Spotify login failed: {str(e)}")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Spotify login
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="auth-title">🎵 Connect with Spotify</div>', unsafe_allow_html=True)
        st.markdown("""
        <p style="color:#a0a0a0;text-align:center;font-size:0.88rem;margin-bottom:1.2rem;">
        Login with your Spotify account for full song playback and personalised recommendations.
        Premium users get full tracks. Free users get 30-second previews.
        </p>
        """, unsafe_allow_html=True)

        try:
            oauth = get_spotify_oauth()
            auth_url = oauth.get_authorize_url()
            st.markdown(f"""
            <div style="text-align:center;margin:0.5rem 0 1rem 0;">
                <a href="{auth_url}" target="_top" class="spotify-login-btn">
                    🎵 &nbsp; Login with Spotify
                </a>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Could not generate Spotify login URL: {str(e)}")

        st.markdown("""
        <div style="display:flex;align-items:center;gap:0.5rem;margin:1rem 0;">
            <hr style="flex:1;border-color:#282828;margin:0;">
            <span style="color:#6a6a6a;font-size:0.8rem;">or use email</span>
            <hr style="flex:1;border-color:#282828;margin:0;">
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Email login / signup
        mode = st.radio("", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        st.session_state.auth_mode = mode.lower().replace(" ", "_")

        st.markdown('<div class="card">', unsafe_allow_html=True)

        if st.session_state.auth_mode == "login":
            st.markdown('<div class="auth-title">Welcome Back</div>', unsafe_allow_html=True)
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            if st.button("Log In"):
                if not email or not password:
                    st.warning("Please fill in all fields.")
                else:
                    success, msg, user = sign_in(email, password)
                    if success:
                        st.session_state.user = user
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.markdown('<div class="auth-title">Create Account</div>', unsafe_allow_html=True)
            username = st.text_input("Username")
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            country = st.selectbox("Your country", options=COUNTRY_LIST)
            if st.button("Create Account"):
                if not all([username, email, password, confirm]):
                    st.warning("Please fill in all fields.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success, msg, user = sign_up(email, username, password, country)
                    if success:
                        st.session_state.user = user
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown('</div>', unsafe_allow_html=True)


# ── MAIN APP ──────────────────────────────────────────────────
def render_main():
    user = st.session_state.user
    country = user.get("country", "Global")
    spotify_connected = st.session_state.spotify_token is not None

    st.markdown(f"""
    <div class="hero">
        <div class="hero-title">Moodify</div>
        <div class="hero-sub">
            Welcome back, {user['username']} 👋
            {"&nbsp;&nbsp;<span class='spotify-badge'>🎵 Spotify Connected</span>" if spotify_connected else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎵  Discover", "📊  My Mood History", "⚙️  Settings"])

    # ── TAB 1: DISCOVER ───────────────────────────────────────
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        user_input = st.text_area(
            "How are you feeling right now?",
            placeholder="e.g. I feel anxious and overwhelmed today...",
            height=100
        )

        col1, col2 = st.columns(2)
        with col1:
            target_mood = st.selectbox(
                "Target mood",
                options=["calm", "focus", "energise", "happy", "sleep", "confidence", "romance", "workout"],
                format_func=lambda x: {
                    "calm": "😌  Calm",
                    "focus": "🎯  Focus",
                    "energise": "⚡  Energise",
                    "happy": "😊  Happy",
                    "sleep": "🌙  Sleep",
                    "confidence": "💪  Confidence",
                    "romance": "❤️  Romance",
                    "workout": "🏋️  Workout"
                }[x]
            )
        with col2:
            selected_country = st.selectbox(
                "Music region",
                options=COUNTRY_LIST,
                index=COUNTRY_LIST.index(country) if country in COUNTRY_LIST else 0
            )

        st.markdown('</div>', unsafe_allow_html=True)

        if not spotify_connected:
            st.markdown("""
            <div style="background:#1a1a2e;border:1px solid #3e3e3e;border-radius:10px;
                        padding:0.8rem 1rem;margin-bottom:1rem;color:#a0a0a0;font-size:0.85rem;">
                💡 <strong style="color:#1DB954;">Tip:</strong> Log in with Spotify for full song playback.
                Currently showing 30-second previews.
            </div>
            """, unsafe_allow_html=True)

        if st.button("Generate My Playlist"):
            if not user_input.strip():
                st.warning("Please describe how you're feeling first.")
            elif len(user_input.strip()) < 3:
                st.warning("Please give a little more detail.")
            elif len(user_input.strip()) > 500:
                st.warning("Please keep your description under 500 characters.")
            else:
                with st.spinner("Analysing your mood..."):
                    mood_result = detect_mood(user_input)
                st.session_state.current_mood = mood_result

                st.markdown('<div class="section-header">Your Emotion Analysis</div>', unsafe_allow_html=True)
                st.markdown('<div class="card">', unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Primary Emotion", mood_result["primary_emotion"].capitalize())
                with col2:
                    st.metric("Confidence", f"{int(mood_result['confidence'] * 100)}%")
                with col3:
                    st.metric("Intensity", mood_result["intensity"])

                st.markdown("<br>**Emotion Breakdown**", unsafe_allow_html=True)
                for emotion in mood_result["top_emotions"]:
                    render_emotion_bar(emotion["label"], emotion["score"])

                if mood_result["keywords"]:
                    kw_html = " ".join([f'<span class="keyword-tag">{k}</span>' for k in mood_result["keywords"]])
                    st.markdown(f"<br>**Key themes detected:** {kw_html}", unsafe_allow_html=True)

                sentiment_emoji = {"positive": "😊", "negative": "😔", "neutral": "😐"}
                st.markdown(f"<br>**Overall sentiment:** {sentiment_emoji.get(mood_result['sentiment'], '😐')} {mood_result['sentiment'].capitalize()}", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="transition-pill">
                    Shifting you from <strong>{mood_result['primary_emotion']}</strong> → <strong>{target_mood}</strong>
                    &nbsp;|&nbsp; 🌍 {selected_country} mix
                </div>
                """, unsafe_allow_html=True)

                with st.spinner("Curating your personalised playlist..."):
                    tracks = get_recommendations(
                        mood_result,
                        target_mood,
                        country=selected_country,
                        token_info=st.session_state.get("spotify_token")
                    )

                if isinstance(tracks, dict) and "error" in tracks:
                    st.error(f"Spotify error: {tracks['error']}")
                else:
                    st.session_state.current_tracks = tracks
                    local_count = sum(1 for t in tracks if t.get('is_local'))
                    global_count = len(tracks) - local_count

                    st.markdown('<div class="section-header">Your Playlist</div>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color:#a0a0a0;font-size:0.85rem;">🌍 {local_count} local tracks &nbsp;|&nbsp; 🌐 {global_count} global tracks</p>', unsafe_allow_html=True)
                    st.markdown('<hr class="divider">', unsafe_allow_html=True)

                    for i, track in enumerate(tracks, 1):
                        render_track(i, track)

                    st.markdown('<hr class="divider">', unsafe_allow_html=True)

                    # Save session
                    try:
                        save_session(
                            user_id=user["id"],
                            user_input=user_input,
                            mood_result=mood_result,
                            target_mood=target_mood,
                            country=selected_country,
                            tracks=tracks
                        )
                    except Exception:
                        pass

                    # Feedback
                    if not st.session_state.feedback_given:
                        st.markdown('<div style="text-align:center;color:#a0a0a0;font-size:0.85rem;padding:0.5rem 0;">Did this playlist shift your mood?</div>', unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("😌  Yes, calmer"):
                                st.session_state.feedback_given = True
                                st.success("Glad it helped!")
                        with col2:
                            if st.button("⚡  Feeling energised"):
                                st.session_state.feedback_given = True
                                st.success("Let's go!")
                        with col3:
                            if st.button("😐  Not really"):
                                st.session_state.feedback_given = True
                                st.info("Try a different target mood.")

    # ── TAB 2: MOOD HISTORY ───────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">Your Mood Journey</div>', unsafe_allow_html=True)

        try:
            stats = get_mood_stats(user["id"])
        except Exception:
            stats = None

        if not stats:
            st.info("No sessions yet. Generate your first playlist to start tracking your mood journey.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sessions", stats["total_sessions"])
            with col2:
                st.metric("Avg Confidence", f"{stats['avg_confidence']}%")
            with col3:
                positive_feedback = stats["feedback_counts"]["Yes, calmer"] + stats["feedback_counts"]["Feeling energised"]
                st.metric("Positive Feedback", positive_feedback)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if stats["emotion_counts"]:
                    emotions = list(stats["emotion_counts"].keys())
                    counts = list(stats["emotion_counts"].values())
                    fig = px.pie(values=counts, names=emotions, title="Emotion Distribution",
                                 color_discrete_sequence=px.colors.sequential.Greens_r, hole=0.4)
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                      font=dict(color="white"), title_font=dict(color="white"),
                                      legend=dict(font=dict(color="white")))
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                if stats["target_counts"]:
                    targets = list(stats["target_counts"].keys())
                    t_counts = list(stats["target_counts"].values())
                    fig2 = px.bar(x=targets, y=t_counts, title="Target Mood Frequency",
                                  color=t_counts, color_continuous_scale="Greens")
                    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                       font=dict(color="white"), title_font=dict(color="white"),
                                       showlegend=False, coloraxis_showscale=False)
                    st.plotly_chart(fig2, use_container_width=True)

            st.markdown('<div class="section-header">Sentiment Overview</div>', unsafe_allow_html=True)
            sentiments = stats["sentiments"]
            total = sum(sentiments.values()) or 1
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("😊 Positive", f"{round(sentiments['positive']/total*100)}%")
            with col2:
                st.metric("😐 Neutral", f"{round(sentiments['neutral']/total*100)}%")
            with col3:
                st.metric("😔 Negative", f"{round(sentiments['negative']/total*100)}%")

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">Recent Sessions</div>', unsafe_allow_html=True)

            try:
                history = get_user_history(user["id"], limit=5)
                for session in history:
                    with st.expander(f"🎵 {session['primary_emotion'].capitalize()} → {session['target_mood']} | {session['created_at'][:10]}"):
                        st.write(f"**You said:** {session['user_input']}")
                        st.write(f"**Confidence:** {int(float(session['confidence']) * 100)}%")
                        st.write(f"**Intensity:** {session['intensity']}")
                        st.write(f"**Sentiment:** {session['sentiment']}")
                        st.write(f"**Country:** {session['country']}")
                        if session.get('feedback'):
                            st.write(f"**Feedback:** {session['feedback']}")
            except Exception:
                st.info("Could not load session history.")

    # ── TAB 3: SETTINGS ───────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">Account Settings</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.write(f"**Username:** {user['username']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Current region:** {user.get('country', 'Global')}")

        if spotify_connected:
            spotify_profile = st.session_state.spotify_user
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#1a2e1a;border:1px solid #1DB954;border-radius:10px;padding:1rem;">
                <p style="color:#1DB954;font-weight:600;margin:0 0 4px 0;">🎵 Spotify Connected</p>
                <p style="color:#a0a0a0;font-size:0.85rem;margin:0;">
                    Logged in as <strong style="color:#ffffff;">{spotify_profile.get('display_name', 'Spotify User')}</strong>
                    &nbsp;|&nbsp; {spotify_profile.get('product', 'free').capitalize()} account
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        new_country = st.selectbox(
            "Update your music region",
            options=COUNTRY_LIST,
            index=COUNTRY_LIST.index(user.get("country", "Global")) if user.get("country") in COUNTRY_LIST else 0
        )

        if st.button("Save Region"):
            try:
                if update_country(user["id"], new_country):
                    st.session_state.user["country"] = new_country
                    st.success(f"Region updated to {new_country}!")
                else:
                    st.error("Failed to update region.")
            except Exception:
                st.session_state.user["country"] = new_country
                st.success(f"Region updated to {new_country}!")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)

        if st.button("Log Out"):
            st.session_state.user = None
            st.session_state.spotify_token = None
            st.session_state.spotify_user = None
            st.session_state.current_tracks = None
            st.session_state.current_mood = None
            st.session_state.feedback_given = False
            st.rerun()


# ── Router ────────────────────────────────────────────────────
if st.session_state.user is not None:
    render_main()
else:
    render_auth()

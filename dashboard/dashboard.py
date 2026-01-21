import streamlit as st
from service import Service

from database.db_env import DBEnv

env = DBEnv.PROD

recent_tracks = Service.fetch_recent_tracks(env=env)
recommended_tracks = Service.fetch_recommended_tracks(env=env)

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #121212;
    }
    [data-testid="stAppViewContainer"] {
        padding: 0rem !important;
    }
    .main-title {
        color: white;
        font-weight: 800;
        font-size: 2.4rem;
        margin-bottom: 8px;
    }
    .main-underline {
        width: 120px;
        height: 5px;
        background-color: #1DB954;
        border-radius: 3px;
    }
    .section-title {
        color: white;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 4px;
        margin-top: 40px !important;
    }
    .section-underline {
        width: 60px;
        height: 4px;
        background-color: #1DB954;
        border-radius: 2px;
        margin-bottom: 28px;
    }
    .track-card {
        padding: 12px;
        border-radius: 14px;
        background-color: #232323;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .track-card:hover {
        background-color: #2a2a2a;
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(29, 185, 84, 0.25);
    }
    .track-title {
        font-weight: 600;
        margin: 16px 0 8px 0;
        color: #ffffff;
        font-size: 1rem;
    }
    .track-title::after {
        content: "";
        display: block;
        width: 26px;
        height: 2px;
        background-color: #1DB954;
        margin: 6px auto 0 auto;
        border-radius: 1px;
    }
    .track-meta {
        color: #cfcfcf;
        font-size: 0.9em;
        margin: 6px 0;
    }
    img {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="main-title">Music Recommendation Dashboard</div>
<div class="main-underline"></div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="section-title">Recently listened</div>
<div class="section-underline"></div>
""",
    unsafe_allow_html=True,
)

cols = st.columns(len(recent_tracks))

for i, track in enumerate(recent_tracks):
    col = cols[i % len(recent_tracks)]

    with col:
        st.markdown(
            f"""
            <div class="track-card">
                <img src="{track.image_url}" width="100%" />
                <div class="track-title">{track.name}</div>
                <div
                    class="track-meta">{", ".join([a.name for a in track.artists])}
                </div>
                <div class="track-meta">{track.album.name}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
<div class="section-title">Recommended for you</div>
<div class="section-underline"></div>
""",
    unsafe_allow_html=True,
)

cols = st.columns(len(recommended_tracks))

for i, track in enumerate(recommended_tracks):
    col = cols[i % len(recommended_tracks)]

    with col:
        st.markdown(
            f"""
            <div class="track-card">
                <img src="{track.image_url}" width="100%" />
                <div class="track-title">{track.name}</div>
                <div
                    class="track-meta">{", ".join([a.name for a in track.artists])}
                </div>
                <div class="track-meta">{track.album.name}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

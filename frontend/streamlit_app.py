import os
import requests
import streamlit as st

# Allow overriding the backend URL via environment variable or Streamlit secrets.
# When deploying the frontend (Streamlit Community Cloud), set the secret/API value
# `API_URL` to the public URL of your deployed backend.
API_URL = os.getenv("API_URL") or st.secrets.get("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="IntelliCart", layout="wide", page_icon="🛒")


def badge_class(category: str) -> str:
    mapping = {
        "Electronics": "badge-electronics",
        "Home": "badge-home",
        "Wearables": "badge-wearables",
        "Accessories": "badge-accessories",
        "Sportswear": "badge-sportswear",
    }
    return mapping.get(category, "badge-default")


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&family=Dosis:wght@200..800&family=Josefin+Sans:ital,wght@0,100..700;1,100..700&family=Oswald:wght@200..700&display=swap');
    :root {font-family: 'Dosis', sans-serif;}
    .reportview-container, .main, .block-container {background: #eef2ff;}
    .css-18e3th9 {background-color: #eef2ff;}
    .css-1d391kg {background-color: #eef2ff;}
    .css-1v0mbdj {background-color: #eef2ff;}
    .stSidebar {background: #f8faff; border-radius: 24px; padding: 24px;}
    .stSidebar .stSelectbox, .stSidebar .stTextInput {background: #ffffff; border-radius: 14px;}
    .stSidebar .stButton>button {background-color: #4c51bf; color: white; border-radius: 14px;}
    .stSidebar .stButton>button:hover {background-color: #4338ca;}
    .stButton>button {background-color: #4c51bf; color: white; border-radius: 14px;}
    .stButton>button:hover {background-color: #4338ca;}
    .card {background: linear-gradient(180deg, #ffffff 0%, #eef4ff 100%); border: 1px solid #c7d2fe; border-radius: 24px; padding: 24px; box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08); margin-bottom: 22px;}
    .card-title {font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.18rem; font-weight: 700; color: #1e3a8a; margin-bottom: 10px;}
    .card-meta {font-family: 'Dosis', sans-serif; color: #475569; margin-bottom: 12px;}
    .card-badge {display: inline-block; padding: 6px 12px; border-radius: 999px; font-size: 0.85rem; margin-right: 8px; font-family: 'Dosis', sans-serif;}
    .badge-electronics {background: rgba(59, 130, 246, 0.14); color: #1d4ed8;}
    .badge-home {background: rgba(16, 185, 129, 0.14); color: #059669;}
    .badge-wearables {background: rgba(251, 191, 36, 0.14); color: #b45309;}
    .badge-accessories {background: rgba(139, 92, 246, 0.14); color: #7c3aed;}
    .badge-sportswear {background: rgba(239, 68, 68, 0.14); color: #b91c1c;}
    .badge-default {background: rgba(148, 163, 184, 0.14); color: #334155;}
    .small-text {font-family: 'Dosis', sans-serif; color: #64748b; line-height: 1.6;}
    .stMetric {border-radius: 20px; background: #eef2ff;}
    .stMetric .value {font-family: 'Bricolage Grotesque', sans-serif; color: #4338ca;}
    .stMetric .delta {font-family: 'Dosis', sans-serif; color: #1d4ed8;}
    .page-heading {font-family: 'Bricolage Grotesque', sans-serif; font-size: 2.5rem; font-weight: 800; color: #1e3a8a; margin-bottom: 0.2rem;}
    .page-subtitle {font-family: 'Josefin Sans', sans-serif; font-size: 1rem; color: #475569; margin-top: 0; margin-bottom: 1.5rem;}
    .section-header {font-family: 'Oswald', sans-serif; font-size: 1.3rem; color: #1e40af; margin-bottom: 0.7rem;}
    .section-header.style-2 {color: #0f766e;}
    .section-header.style-3 {color: #c2410c;}
    .section-label {font-family: 'Dosis', sans-serif; color: #475569; font-size: 0.95rem;}
    .stSidebar h2, .sidebar-header {font-family: 'Oswald', sans-serif; color: #1e3a8a;}
    .trending-chip {display: inline-block; background: rgba(59, 130, 246, 0.14); color: #1d4ed8; padding: 4px 10px; border-radius: 999px; font-size: 0.82rem; margin-top: 4px; font-family: 'Dosis', sans-serif;}
    .hero-panel {background: linear-gradient(135deg, #eef2ff 0%, #e0f2fe 100%); border-radius: 28px; padding: 24px; border: 1px solid #dbeafe; margin-bottom: 24px;}
    .hero-panel strong {color: #4338ca;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='page-heading'>🛍️ IntelliCart</div>", unsafe_allow_html=True)
st.markdown("<div class='page-subtitle'>A Hybrid Product Recommendation System with Explainable Recommendations for E-Commerce Platforms</div>", unsafe_allow_html=True)

user_id = st.sidebar.selectbox("Select User", [1, 2, 3, 4, 5])
search_query = st.sidebar.text_input("Search products")

if st.sidebar.button("Refresh"):
    st.experimental_rerun()

with st.spinner("Loading data..."):
    try:
        user_response = requests.get(f"{API_URL}/users/{user_id}").json()
        dashboard = requests.get(f"{API_URL}/dashboard/{user_id}").json()
        trending = requests.get(f"{API_URL}/trending").json()
        if search_query:
            search_results = requests.get(f"{API_URL}/products", params={"q": search_query}).json()
        else:
            search_results = []
    except requests.exceptions.RequestException as exception:
        st.error(f"Could not reach backend API: {exception}")
        st.stop()

st.sidebar.markdown("## User profile")
st.sidebar.write(f"**Name:** {user_response.get('name')}  ")
st.sidebar.write(f"**Preferences:** {user_response.get('preferences')}  ")
st.sidebar.markdown("---")
st.sidebar.markdown("## Trending products")
for item in trending[:5]:
    st.sidebar.markdown(f"**{item['name']}**  ")
    st.sidebar.markdown(f"<span class='small-text'>{item['category']} • ${item['price']}</span>", unsafe_allow_html=True)

st.markdown("---")
with st.container():
    st.markdown("<div class='hero-panel'>", unsafe_allow_html=True)
    hero_col1, hero_col2, hero_col3 = st.columns(3)
    hero_col1.metric("🧠 Recommendations", len(dashboard.get("recommendations", [])), delta="+12%")
    hero_col2.metric("🔥 Trending", len(trending), delta="+8%")
    hero_col3.metric("🕒 Activity", len(dashboard.get("recent_activity", [])), delta="+5%")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

main_col, side_col = st.columns([3, 1])
with main_col:
    st.markdown("<div class='section-header'>🛒 Recommendations</div>", unsafe_allow_html=True)
    for item in dashboard["recommendations"]:
        st.markdown(
            f"<div class='card'>"
            f"<div class='card-title'>{item['name']}</div>"
            f"<div class='card-badge {badge_class(item['category'])}'>{item['category']}</div>"
            f"<div class='card-meta'>Price: <strong>${item['price']}</strong> • Rating: <strong>{item['rating']} ⭐</strong></div>"
            f"<div class='small-text'>{item['explanation']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

with side_col:
    st.markdown("<div class='section-header'>📌 Recent activity</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if dashboard["recent_activity"]:
        for event in dashboard["recent_activity"]:
            st.markdown(f"<div class='small-text'>• {event}</div>", unsafe_allow_html=True)
    else:
        st.write("No recent activity yet.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("<div class='section-header'>🔍 Search product catalog</div>", unsafe_allow_html=True)
if search_query:
    if search_results:
        for item in search_results:
            st.markdown(
                f"<div class='card'>"
                f"<div class='card-title'>{item['name']}</div>"
                f"<div class='card-badge {badge_class(item['category'])}'>{item['category']}</div>"
                f"<div class='card-meta'>${item['price']} • {item['rating']} ⭐</div>"
                f"<div class='small-text'>{item['description']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("No products found for your search.")
else:
    st.info("Search for products by keyword from the sidebar.")

st.markdown("---")

st.markdown("<div class='section-header'>✨ Trending products</div>", unsafe_allow_html=True)
trending_cols = st.columns(4)
for idx, item in enumerate(trending[:8]):
    with trending_cols[idx % 4]:
        st.markdown(
            f"<div class='card'>"
            f"<div class='card-title'>{item['name']}</div>"
            f"<div class='trending-chip {badge_class(item['category'])}'>Top pick</div>"
            f"<div class='card-meta'>{item['category']} • ${item['price']}</div>"
            f"<div class='small-text'>Rating: {item['rating']} ⭐</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


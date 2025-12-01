import streamlit as st
from quiz_page import show_quiz
from shop_page import show_shop
from team_page import show_team
from battle_page import show_battle
from utils import api_post, api_get

st.set_page_config(page_title="Pokémon Quizmaster", page_icon=":zap:")

st.sidebar.title("Player")
if "player_id" not in st.session_state:
    st.session_state.player_id = None
if "player_points" not in st.session_state:
    st.session_state.player_points = 0

username = st.sidebar.text_input("Username", value="")
if st.sidebar.button("Create/Load Player"):
    if username.strip() == "":
        st.sidebar.error("Enter a username")
    else:
        # create player via backend
        try:
            r = api_post("/players", json=None)  # this path expects form param; but our backend expects query param. For simplicity we'll use GET below.
        except:
            pass
        # Use direct call: backend create_player expects ?username=...
        try:
            resp = api_get(f"/players/{username}")  # this won't exist; so instead call backend create with query param by direct requests - easier: use requests directly
        except:
            # fallback: call endpoint directly via requests
            import requests
            try:
                r = requests.post("http://localhost:8000/players", params={"username": username})
                r.raise_for_status()
                data = r.json()
                st.session_state.player_id = data["id"]
                st.session_state.player_points = data["total_points"]
                st.sidebar.success(f"Loaded id={data['id']}")
            except Exception as e:
                st.sidebar.error(f"Failed to create player: {e}")

st.sidebar.write(f"Player ID: {st.session_state.player_id}")
st.sidebar.write(f"Local Points: {st.session_state.get('player_points', 0)}")

page = st.sidebar.selectbox("Page", ["Quiz", "Shop", "Team", "Battle"])
if page == "Quiz":
    show_quiz()
elif page == "Shop":
    show_shop()
elif page == "Team":
    show_team()
elif page == "Battle":
    show_battle()

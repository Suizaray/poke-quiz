import streamlit as st
from utils import api_post, api_get

def show_shop():
    st.header("Shop")
    if "player_id" not in st.session_state:
        st.info("Create or load a player first on the sidebar.")
        return

    st.write("Buy a random Pokémon for 10 points.")
    if st.button("Buy Random Pokémon (10 pts)"):
        
        try:
            payload = {"player_id": st.session_state.player_id}
            if payload["player_id"] is None:
                st.error("Player ID not set!")
            else:
                res = api_post("/shop/buy", json=payload)
                st.success(f"You got {res['species_name']} (level {res['level']})")
                if res.get("sprite_url"):
                    st.image(res["sprite_url"], width=120)
                st.write("Moves:", res["moves"])
                st.write("Stats (EVs/IVs):", res["stats"])
                st.write(f"Your remaining points: {res['player_points']}")
                # reflect in session
                st.session_state.player_points = res["player_points"]
        except Exception as e:
            st.error(f"Purchase failed: {e}")

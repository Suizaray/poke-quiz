import streamlit as st
from utils import api_get, api_post

def calculate_hp(p):
    base = p.get("stats", {}).get("base_stats", {}).get("hp", 10)
    iv = p.get("stats", {}).get("ivs", {}).get("hp", 0)
    ev = p.get("stats", {}).get("evs", {}).get("hp", 0)
    level = p.get("level", 1)

    return ((2 * base + iv + (ev // 4)) * level) // 100 + level + 10

def hp_bar(p_id):
    info = st.session_state.pokemon_hp[p_id]
    pct = info["current"] / info["max"] * 100
    st.progress(pct / 100.0)
    st.caption(f"{info['current']} / {info['max']} HP")

def show_battle():
    st.header("Battle Arena")

    if "player_id" not in st.session_state:
        st.info("Create or load a player first on the sidebar.")
        return

    # Load all Pokémon from backend
    try:
        pokemon_list = api_get(f"/players/{st.session_state.player_id}/pokemon")
    except Exception as e:
        st.error(f"Failed to fetch Pokémon: {e}")
        return
    

    # Initialize session_state party (in-memory) from in_party info
    if "party" not in st.session_state:
        st.session_state.party = [p for p in pokemon_list if p.get("in_party", 0) > 0]
        st.session_state.party = sorted(st.session_state.party, key=lambda x: x["in_party"])
        # Ensure max 6 slots
        if len(st.session_state.party) > 6:
            st.session_state.party = st.session_state.party[:6]

    # ---------------- Party display ----------------
    st.subheader("Your Team")
    party_cols = st.columns(6)
    for i in range(6):
        if i < len(st.session_state.party):
            p = st.session_state.party[i]
            with party_cols[i]:
                st.image(p["sprite_url"], width=80)
                st.caption(f"{p['species_name']} (Lvl {p['level']})\nSlot {p['in_party']}")
        else:
            with party_cols[i]:
                st.image("https://via.placeholder.com/80x80?text=Empty", width=80)
                st.caption("Empty")

    # Battle

    if "battle" not in st.session_state or st.button("Next Battle"):
        try:
            st.session_state.battle = api_get("/battle/generate_opponent")
            st.session_state.move_selected = None
            st.session_state.active_player = None
            st.session_state.active_opponent = None
            st.session_state.battle_result = None
            st.session_state.battle_start = True
        except Exception as e:
            st.error(f"Failed to fetch battle: {e}")
            return
        
    battle = st.session_state.battle

    st.subheader("Opponents Team")
    opp_cols = st.columns(6)

    if "opponent_team" in battle:
        opponent_team = battle["opponent_team"]
        for i in range(6):
            with opp_cols[i]:
                if i < len(opponent_team):
                    p = opponent_team[i]
                    st.image(p["sprite_url"], width=80)
                    st.caption(f"{p['species_name']} (Lvl {p['level']})\nSlot {p['in_party']}")
                else:
                    st.image("https://via.placeholder.com/80x80?text=???", width=80)
                    st.caption("Unknown")
    else:
        st.warning("Opponent team not found")


    # HP display

    # Initialize stats only once per battle
    if st.session_state.battle_start:
        st.session_state.pokemon_hp = {}

        # For both player + opponent team: store max and current HP
        for p in st.session_state.party + battle["opponent_team"]:
            st.session_state.pokemon_hp[p["id"]] = {
                "current": calculate_hp(p),
                "max": calculate_hp(p),
                "fainted": False
            }

    if st.session_state.active_player is None: 
        st.subheader("Choose Your Pokémon")

        # Player selection buttons
        for i, p in enumerate(st.session_state.party):
            if st.button(f"Send {p['species_name']}"):
                st.session_state.active_player = p
                st.rerun()


    if st.session_state.active_opponent is None:
        # Send to backend for opponent selection
        party_alive =  [p for p in st.session_state.party 
                        if not st.session_state.pokemon_hp[p["id"]]["fainted"]]
        opp_alive = [p for p in battle["opponent_team"]
                     if not st.session_state.pokemon_hp[p["id"]]["fainted"]]
        
        if not opp_alive:
            st.success("You won the battle! 🎉")
            st.session_state.battle_result = "Won"

        payload = {
                    "player_team": party_alive,
                    "opponent_team": opp_alive,
                    "player_selected": st.session_state.active_player
                }

        try:
            resp = api_post("/battle/opponent_choose", json=payload)
            st.session_state.active_opponent = resp["opponent_selected"]
        except Exception as e:
            st.error(f"Opponent selection failed: {e}")


    if st.session_state.active_player and st.session_state.active_opponent:
        st.subheader("Battle Start!")

        col1, col2 = st.columns(2)

        with col1:
            p = st.session_state.active_player
            st.image(p["sprite_url"], width=120)
            st.caption(f"Your Pokémon: {p['species_name']} - Lvl {p['level']}")
            hp_bar(p["id"])

        with col2:
            o = st.session_state.active_opponent
            st.image(o["sprite_url"], width=120)
            st.caption(f"Opponent Pokémon: {o['species_name']} - Lvl {o['level']}")
            hp_bar(o["id"])


            player = st.session_state.active_player
            opp = st.session_state.active_opponent

            player_hp = st.session_state.pokemon_hp[player["id"]]
            opp_hp    = st.session_state.pokemon_hp[opp["id"]]

            # If fainted
            if player_hp["current"] <= 0 and not player_hp["fainted"]:
                player_hp["fainted"] = True
                st.error(f"{player['species_name']} fainted!")

                # Offer switching if others available
                alive = [p for p in st.session_state.party 
                        if not st.session_state.pokemon_hp[p["id"]]["fainted"]]
                if alive:
                    st.subheader("Choose next Pokémon!")
                    for p in alive:
                        if st.button(f"Switch to {p['species_name']}"):
                            st.session_state.active_player = p
                            st.rerun()
                else:
                    st.session_state.battle_result = "Lost"
                    st.error("You lost the battle!")
            
            # If opponent fainted
            if opp_hp["current"] <= 0 and not opp_hp["fainted"]:
                opp_hp["fainted"] = True
                st.success(f"{opp['species_name']} fainted!")
                st.session_state.active_opponent = None
                st.rerun()


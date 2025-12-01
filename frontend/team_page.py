import streamlit as st
from utils import api_get, api_post

def show_team():
    st.header("Your Pokémon Team")

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
    st.subheader("Current Party (6 slots)")
    party_cols = st.columns(6)
    for i in range(6):
        if i < len(st.session_state.party):
            p = st.session_state.party[i]
            with party_cols[i]:
                st.image(p["sprite_url"], width=80)
                st.caption(f"{p['species_name']} (Lvl {p['level']})\nSlot {p['in_party']}")

                # replace button
                btn_text = "Replace"
                if st.session_state.get("slot_to_replace") == i:
                    btn_text = f"⚡ {btn_text}"
                if st.button(btn_text, key=f"replace_btn_{p['id']}"):
                    st.session_state.slot_to_replace = i
                    st.session_state.show_replacement = True
        else:
            with party_cols[i]:
                st.image("https://via.placeholder.com/80x80?text=Empty", width=80)
                st.caption("Empty")


    st.markdown("---")  # divider between party and storage
    if st.button("Clear Party"):
        # Move all party Pokémon to slot 0 (PC)
        for p in st.session_state.party:
            try:
                api_post(f"/players/{st.session_state.player_id}/pokemon/{p['id']}/set_party_slot",
                        json={"slot": 0})
            except:
                st.warning(f"Failed to update {p['species_name']} slot to 0")
        # Clear session state party
        st.session_state.party = []
        st.session_state.pending_add = None
        st.session_state.show_replacement = False
        st.rerun()
    
    st.markdown("---")  # divider between party and storage

    st.subheader("Your Pokémon Storage")
    # Exclude all Pokémon currently in session_state.party from storage
    storage_list = [p for p in pokemon_list if p["id"] not in [x["id"] for x in st.session_state.party]]
    for p in storage_list:
        if p in st.session_state.party:
            continue  # skip party members

        cols = st.columns([1,2,2,1])
        with cols[0]:
            st.image(p["sprite_url"], width=60)
        with cols[1]:
            st.write(f"{p['species_name']} (Lvl {p['level']})")
        with cols[2]:
            st.write(f"Moves: {', '.join(p['moves'])}")
        with cols[3]:
            btn_text = "Add to Party"
            if st.session_state.get("pending_add") == p:
                btn_text = f"⚡ {btn_text}"  # highlight pending

            # Step 1: User clicks "Add to Party"
            if st.button(btn_text, key=f"add_{p['id']}"):
                if len(st.session_state.party) < 6:
                    # Not full, just add
                    available_slot = next(s for s in range(1,7) if s not in [x["in_party"] for x in st.session_state.party])
                    p["in_party"] = available_slot
                    st.session_state.party.append(p)
                    try:
                        api_post(f"/players/{st.session_state.player_id}/pokemon/{p['id']}/set_party_slot",
                                json={"slot": p["in_party"]})
                    except:
                        st.warning("Failed to update backend")
                    # done, refresh    
                    st.rerun()
                else:
                    # Party full → store Pokémon to add in session_state
                    st.session_state.pending_add = p

            # Step 2: Show replacement selectbox if needed
            if st.session_state.get("show_replacement") and st.session_state.get("pending_add"):
                # Replace the selected slot with pending_add Pokémon
                idx = st.session_state.slot_to_replace
                replaced = st.session_state.party[idx]
                pending = st.session_state.pending_add

                pending["in_party"] = replaced["in_party"]
                st.session_state.party[idx] = pending

                # Update backend
                try:
                    api_post(f"/players/{st.session_state.player_id}/pokemon/{pending['id']}/set_party_slot",
                            json={"slot": pending["in_party"]})
                except:
                    st.warning("Backend update failed.")

                # Clear flags
                st.session_state.pending_add = None
                st.session_state.show_replacement = False

                # Rerun page to refresh display
                st.rerun()

    st.write("Party updated!")

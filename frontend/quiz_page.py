import streamlit as st
from utils import api_get, api_post

def show_quiz():
    st.header("Quiz")
    if "player_id" not in st.session_state:
        st.info("Create or load a player first on the sidebar.")
        return

    if "quiz" not in st.session_state or st.button("New Question"):
        try:
            st.session_state.quiz = api_get("/quiz/quiz")
            st.session_state.answered = False
            st.session_state.selected = None
        except Exception as e:
            st.error(f"Failed to fetch quiz: {e}")
            return

    quiz = st.session_state.quiz
    st.subheader(quiz["question"])

    for option in quiz["options"]:
        if st.button(option):
            st.session_state.selected = option
            st.session_state.answered = True
            # award points immediately if correct
            if option == quiz["answer"]:
                # give 5 points for correct
                try:
                    # Call backend to award points
                    resp = api_post("/quiz/award_points", json={
                        "player_id": st.session_state.player_id,
                        "points": 5
                    })
                    st.session_state.player_points = resp["total_points"]
                except Exception as e:
                    st.error(f"Failed to award points: {e}")

    if st.session_state.get("answered"):
        if st.session_state.get("selected") == quiz["answer"]:
            st.success("Correct! +5 points")
        else:
            st.error(f"Wrong. Correct: {quiz['answer']}")

        st.write(f"Hint: {quiz.get('hint')}")

    st.write(f"Local points: {st.session_state.get('player_points', 0)}")

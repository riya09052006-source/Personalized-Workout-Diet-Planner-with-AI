import streamlit as st
from datetime import date
from database.db import get_plan, log_progress
from components.cards import workout_card
def show_workout_page():
    if not st.session_state.user_id:
        st.warning("Please log in to access this page.")
        return

    st.markdown('<h1 style="color: #ffffff; font-family: \'Outfit\', sans-serif;">💪 Your Weekly Workout Plan</h1>', unsafe_allow_html=True)
    
    plan_data = get_plan(st.session_state.user_id)
    if not plan_data:
        st.info("You haven't generated a plan yet. Please fill out your profile details first.")
        return
        
    workout_plan = plan_data["workout_plan"]
    
    st.markdown(f'<p style="color: #94A3B8;">Last updated: {plan_data["updated_at"]}</p>', unsafe_allow_html=True)
    st.write(" ")
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_tabs = st.tabs(days)
    
    for idx, day_name in enumerate(days):
        with day_tabs[idx]:
            day_data = workout_plan.get(day_name, {"focus": "Rest Day", "exercises": []})
            focus = day_data.get("focus", "Rest Day")
            exercises = day_data.get("exercises", [])
            
            st.markdown(f'<h3 style="color: #00F2FE; font-family: \'Outfit\', sans-serif; margin-bottom: 20px;">🎯 Today\'s Focus: {focus}</h3>', unsafe_allow_html=True)
            
            if focus == "Rest Day" or not exercises:
                st.info("🧘 Enjoy your recovery! Keep hydrated and take time to stretch.")
                continue
                
            st.markdown('<h4 style="color: #ffffff; font-family: \'Outfit\', sans-serif;">Exercises Checklist:</h4>', unsafe_allow_html=True)
            
            completed_count = 0
            total_exercises = len(exercises)
            
            for i, ex in enumerate(exercises):
                key = f"workout_{day_name}_{i}"
                if key not in st.session_state:
                    st.session_state[key] = False
                    
                col_check, col_card = st.columns([1, 15])
                with col_check:
                    st.write("")
                    st.write("")
                    is_completed = st.checkbox("", key=key, label_visibility="collapsed")
                    if is_completed:
                        completed_count += 1
                        
                with col_card:
                    card_html = workout_card(
                        exercise_name=ex["exercise"],
                        target=ex["target"],
                        equipment=ex["equipment"],
                        duration=ex["duration"]
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
                    
            st.write(" ")
            
            completion_rate = (completed_count / total_exercises) * 100
            st.progress(completion_rate / 100.0)
            st.write(f"**Completion**: {completed_count} of {total_exercises} exercises done ({completion_rate:.0f}%)")
            
            if completed_count == total_exercises:
                st.balloons()
                st.success("🎉 Outstanding! You completed all the exercises for today.")
                if st.button("Log Workout as Completed", key=f"btn_log_{day_name}"):
                    log_progress(
                        user_id=st.session_state.user_id,
                        log_date=date.today(),
                        weight=None,
                        calories_consumed=None,
                        water_intake_ml=None,
                        workout_completed=True
                    )
                    st.success("Workout completion logged in your dashboard!")

show_workout_page()
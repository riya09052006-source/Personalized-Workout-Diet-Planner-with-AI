import streamlit as st
from database.db import save_profile, get_profile, save_plan
from services.ai_service import generate_plans_with_ai
def show_profile_page():
    if not st.session_state.user_id:
        st.warning("Please log in to access this page.")
        return

    st.markdown('<h1 style="color: #ffffff; font-family: \'Outfit\', sans-serif;">👤 Setup Your Fitness Profile</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94A3B8;">Tell us about yourself so our AI can curate the perfect diet and workout split for your goals.</p>', unsafe_allow_html=True)
    
    existing_profile = get_profile(st.session_state.user_id)
    if existing_profile is None:
        existing_profile = {}
        
    st.write(" ")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h3 style="color: #00F2FE; font-family: \'Outfit\', sans-serif; font-size: 1.25rem;">Demographics</h3>', unsafe_allow_html=True)
            age = st.slider("Age (years)", min_value=12, max_value=100, value=existing_profile.get("age", 25))
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(existing_profile.get("gender", "Male")))
            height = st.slider("Height (cm)", min_value=100.0, max_value=250.0, value=existing_profile.get("height", 170.0), step=0.5)
            weight = st.slider("Weight (kg)", min_value=30.0, max_value=200.0, value=existing_profile.get("weight", 70.0), step=0.5)
            
            st.markdown('<h3 style="color: #00F2FE; font-family: \'Outfit\', sans-serif; font-size: 1.25rem; margin-top: 25px;">Preferences</h3>', unsafe_allow_html=True)
            pref_options = ["Veg", "Non-Veg", "Vegan"]
            food_preference = st.selectbox("Dietary Preference", pref_options, index=pref_options.index(existing_profile.get("food_preference", "Veg")))
            budget = st.number_input("Monthly Food Budget (₹)", min_value=1000.0, max_value=100000.0, value=existing_profile.get("budget", 5000.0), step=500.0)
            
        with col2:
            st.markdown('<h3 style="color: #4FACFE; font-family: \'Outfit\', sans-serif; font-size: 1.25rem;">Fitness Goals</h3>', unsafe_allow_html=True)
            goal_options = ["Weight Loss", "Muscle Gain", "Endurance", "General Fitness"]
            goal = st.selectbox("Primary Goal", goal_options, index=goal_options.index(existing_profile.get("goal", "General Fitness")))
            
            level_options = ["Beginner", "Intermediate", "Advanced"]
            fitness_level = st.selectbox("Current Fitness Experience", level_options, index=level_options.index(existing_profile.get("fitness_level", "Beginner")))
            
            st.markdown('<h3 style="color: #4FACFE; font-family: \'Outfit\', sans-serif; font-size: 1.25rem; margin-top: 48px;">Workout Setup</h3>', unsafe_allow_html=True)
            workout_time = st.slider("Workout Duration Limit (minutes/day)", min_value=15, max_value=120, value=existing_profile.get("workout_time", 45), step=5)
            equip_options = ["Bodyweight", "Dumbbells", "Full Gym"]
            equipment = st.selectbox("Equipment Available", equip_options, index=equip_options.index(existing_profile.get("equipment", "Bodyweight")))
            
        st.write(" ")
        save_btn = st.form_submit_button("🔥 Save Profile & Generate My Plans", use_container_width=True)
        
        if save_btn:
            with st.spinner("Processing profile and generating personalized schedules..."):
                save_profile(
                    user_id=st.session_state.user_id,
                    age=age,
                    height=height,
                    weight=weight,
                    gender=gender,
                    goal=goal,
                    budget=budget,
                    food_preference=food_preference,
                    workout_time=workout_time,
                    fitness_level=fitness_level,
                    equipment=equipment
                )
                
                profile_dict = {
                    "age": age,
                    "height": height,
                    "weight": weight,
                    "gender": gender,
                    "goal": goal,
                    "budget": budget,
                    "food_preference": food_preference,
                    "workout_time": workout_time,
                    "fitness_level": fitness_level,
                    "equipment": equipment
                }
                
                workout_plan, diet_plan, targets, is_ai = generate_plans_with_ai(profile_dict)
                save_plan(st.session_state.user_id, workout_plan, diet_plan)
                
                st.success("Profile saved and weekly plans successfully generated!")
                st.rerun()

if __name__ == "__main__":
    show_profile_page()
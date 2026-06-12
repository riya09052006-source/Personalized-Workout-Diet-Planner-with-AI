
import streamlit as st
from datetime import date
from database.db import get_plan, log_progress, get_profile
from services.recommendation import calculate_daily_targets
from components.cards import meal_card, custom_progress_bar
def show_diet_page():
    if not st.session_state.user_id:
        st.warning("Please log in to access this page.")
        return

    st.markdown('<h1 style="color: #ffffff; font-family: \'Outfit\', sans-serif;">🥗 Your Weekly Diet Plan</h1>', unsafe_allow_html=True)
    
    plan_data = get_plan(st.session_state.user_id)
    profile_data = get_profile(st.session_state.user_id)
    
    if not plan_data or not profile_data:
        st.info("You haven't generated a plan yet. Please fill out your profile details first.")
        return
        
    diet_plan = plan_data["diet_plan"]
    targets = calculate_daily_targets(profile_data)
    
    st.markdown(f'<p style="color: #94A3B8;">Last updated: {plan_data["updated_at"]}</p>', unsafe_allow_html=True)
    st.write(" ")
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_tabs = st.tabs(days)
    
    for idx, day_name in enumerate(days):
        with day_tabs[idx]:
            day_data = diet_plan.get(day_name, {})
            
            breakfast = day_data.get("Breakfast", {})
            lunch = day_data.get("Lunch", {})
            dinner = day_data.get("Dinner", {})
            snack = day_data.get("Snack", {})
            totals = day_data.get("totals", {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0})
            
            col_meals, col_stats = st.columns([3, 2])
            
            with col_meals:
                st.markdown('<h4 style="color: #ffffff; font-family: \'Outfit\', sans-serif; margin-bottom: 15px;">Meal Schedule</h4>', unsafe_allow_html=True)
                
                st.markdown(meal_card("Breakfast", breakfast.get("meal", "N/A"), breakfast.get("calories", 0), 
                                      breakfast.get("protein", 0), breakfast.get("carbs", 0), breakfast.get("fat", 0), 
                                      breakfast.get("cost", 0.0)), unsafe_allow_html=True)
                st.markdown(meal_card("Lunch", lunch.get("meal", "N/A"), lunch.get("calories", 0), 
                                      lunch.get("protein", 0), lunch.get("carbs", 0), lunch.get("fat", 0), 
                                      lunch.get("cost", 0.0)), unsafe_allow_html=True)
                st.markdown(meal_card("Dinner", dinner.get("meal", "N/A"), dinner.get("calories", 0), 
                                      dinner.get("protein", 0), dinner.get("carbs", 0), dinner.get("fat", 0), 
                                      dinner.get("cost", 0.0)), unsafe_allow_html=True)
                st.markdown(meal_card("Snack/Pre-Workout", snack.get("meal", "N/A"), snack.get("calories", 0), 
                                      snack.get("protein", 0), snack.get("carbs", 0), snack.get("fat", 0), 
                                      snack.get("cost", 0.0)), unsafe_allow_html=True)
                
            with col_stats:
                st.markdown('<h4 style="color: #ffffff; font-family: \'Outfit\', sans-serif; margin-bottom: 15px;">Daily Totals vs Targets</h4>', unsafe_allow_html=True)
                
                st.markdown(custom_progress_bar("Calories", totals.get("calories", 0), targets["target_calories"], "#4FACFE"), unsafe_allow_html=True)
                st.markdown(custom_progress_bar("Protein (g)", totals.get("protein", 0), targets["protein_g"], "#38ef7d"), unsafe_allow_html=True)
                st.markdown(custom_progress_bar("Carbs (g)", totals.get("carbs", 0), targets["carbs_g"], "#ff9966"), unsafe_allow_html=True)
                st.markdown(custom_progress_bar("Fat (g)", totals.get("fat", 0), targets["fat_g"], "#ff5e62"), unsafe_allow_html=True)
                
                day_cost = totals.get("cost", 0)
                daily_budget = targets["daily_budget"]
                budget_status_color = "#38ef7d" if day_cost <= daily_budget else "#ff5e62"
                budget_status_text = "Within Budget" if day_cost <= daily_budget else "Over Budget"
                
                st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 12px;
                    padding: 16px;
                    margin-top: 25px;
                ">
                    <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 5px;">Daily Meal Cost</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #ffffff; margin-bottom: 8px;">₹{day_cost:.1f} <span style="font-size: 1rem; font-weight: 400; color: #94A3B8;">/ ₹{daily_budget:.1f} limit</span></div>
                    <span style="background: {budget_status_color}22; color: {budget_status_color}; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 6px; text-transform: uppercase;">
                        {budget_status_text}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                st.write(" ")
                if st.button("Log Today's Calories", key=f"btn_log_diet_{day_name}"):
                    log_progress(
                        user_id=st.session_state.user_id,
                        log_date=date.today(),
                        weight=None,
                        calories_consumed=round(totals.get("calories", 0)),
                        water_intake_ml=None,
                        workout_completed=None
                    )
                    st.success("Today's food intake logged successfully in your dashboard!")

if __name__ == "__main__":
    show_diet_page()
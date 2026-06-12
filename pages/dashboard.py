import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
from database.db import get_progress_history, log_progress, get_profile
from services.recommendation import calculate_daily_targets
from components.cards import glass_card, stat_metric_grid
def show_dashboard_page():
    if not st.session_state.user_id:
        st.warning("Please log in to access this page.")
        return

    st.markdown('<h1 style="color: #ffffff; font-family: \'Outfit\', sans-serif;">📊 Fitness Progress Dashboard</h1>', unsafe_allow_html=True)
    st.write(" ")
    
    profile_data = get_profile(st.session_state.user_id)
    if profile_data:
        targets = calculate_daily_targets(profile_data)
        target_calories = targets["target_calories"]
    else:
        targets = None
        target_calories = 2000
        
    history = get_progress_history(st.session_state.user_id)
    df = pd.DataFrame(history)
    
    today_str = date.today().strftime("%Y-%m-%d")
    today_weight = "-"
    today_calories = 0
    today_water = 0
    today_workout = "No"
    
    if not df.empty:
        today_entry = df[df["date"] == today_str]
        if not today_entry.empty:
            row = today_entry.iloc[0]
            if row["weight"] is not None and not pd.isna(row["weight"]):
                today_weight = f"{row['weight']} kg"
            today_calories = int(row["calories_consumed"]) if not pd.isna(row["calories_consumed"]) else 0
            today_water = int(row["water_intake_ml"]) if not pd.isna(row["water_intake_ml"]) else 0
            today_workout = "Yes" if row["workout_completed"] else "No"
            
        if today_weight == "-":
            valid_weights = df[df["weight"].notna()]
            if not valid_weights.empty:
                today_weight = f"{valid_weights.iloc[-1]['weight']} kg (last logged)"
    
    st.markdown('<h3 style="color: #00F2FE; font-family: \'Outfit\', sans-serif; font-size: 1.35rem;">Today\'s Stats</h3>', unsafe_allow_html=True)
    metrics = [
        {"label": "Current Weight", "value": today_weight, "sub": "Target: Steady Progress"},
        {"label": "Water Consumed", "value": f"{today_water} ml", "sub": "Goal: 3000 ml"},
        {"label": "Calories Consumed", "value": f"{today_calories} kcal", "sub": f"Target: {target_calories} kcal"},
        {"label": "Workout Done", "value": today_workout, "sub": "Keep it up!"}
    ]
    st.markdown(stat_metric_grid(metrics), unsafe_allow_html=True)
    st.write(" ")
    st.write(" ")
    
    col_charts, col_logger = st.columns([2, 1])
    
    with col_logger:
        st.markdown('<h3 style="color: #00F2FE; font-family: \'Outfit\', sans-serif; font-size: 1.35rem;">Log Daily Activity</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #94A3B8; font-size: 0.85rem;">Record your daily vitals to track adjustments over time.</p>', unsafe_allow_html=True)
        
        with st.form("log_form", clear_on_submit=True):
            log_date = st.date_input("Select Date", date.today())
            
            default_w = 70.0
            if profile_data:
                default_w = profile_data["weight"]
            if not df.empty:
                selected_entry = df[df["date"] == log_date.strftime("%Y-%m-%d")]
                if not selected_entry.empty:
                    val = selected_entry.iloc[0]["weight"]
                    if val is not None and not pd.isna(val):
                        default_w = float(val)
            
            log_weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=default_w, step=0.1)
            log_cals = st.number_input("Calories Consumed (kcal)", min_value=0, max_value=10000, value=today_calories if log_date == date.today() else 0, step=50)
            log_water = st.slider("Water Intake (ml)", min_value=0, max_value=6000, value=today_water if log_date == date.today() else 2000, step=250)
            log_done = st.checkbox("Workout Completed", value=(today_workout == "Yes") if log_date == date.today() else False)
            
            submit_log = st.form_submit_button("📝 Save Entry", use_container_width=True)
            if submit_log:
                log_progress(
                    user_id=st.session_state.user_id,
                    log_date=log_date,
                    weight=log_weight,
                    calories_consumed=log_cals,
                    water_intake_ml=log_water,
                    workout_completed=log_done
                )
                st.success(f"Successfully saved stats for {log_date}!")
                st.rerun()
                
    with col_charts:
        st.markdown('<h3 style="color: #4FACFE; font-family: \'Outfit\', sans-serif; font-size: 1.35rem;">Progress Timelines</h3>', unsafe_allow_html=True)
        
        if df.empty:
            st.info("You haven't logged any entries yet. Use the logger on the right to start tracking your weight and calories!")
        else:
            df["parsed_date"] = pd.to_datetime(df["date"])
            df = df.sort_values("parsed_date")
            
            if df["weight"].notna().any():
                fig_weight = px.line(
                    df[df["weight"].notna()], 
                    x="date", 
                    y="weight", 
                    title="Weight Tracker Timeline (kg)",
                    markers=True,
                    color_discrete_sequence=["#00F2FE"]
                )
                fig_weight.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#ffffff",
                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
                )
                st.plotly_chart(fig_weight, use_container_width=True)
            
            st.write(" ")
            
            if df["calories_consumed"].notna().any():
                fig_calories = go.Figure()
                fig_calories.add_trace(go.Bar(
                    x=df["date"],
                    y=df["calories_consumed"],
                    name="Consumed",
                    marker_color="rgba(79, 172, 254, 0.75)",
                    marker_line=dict(color="#4FACFE", width=1.5)
                ))
                fig_calories.add_trace(go.Scatter(
                    x=df["date"],
                    y=[target_calories] * len(df),
                    mode="lines",
                    name="Target Goal",
                    line=dict(color="#ff5e62", width=2, dash="dash")
                ))
                fig_calories.update_layout(
                    title="Daily Calorie Intake vs Target",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#ffffff",
                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
                )
                st.plotly_chart(fig_calories, use_container_width=True)

if __name__ == "__main__":
    show_dashboard_page()
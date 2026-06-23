import os
import pandas as pd
import numpy as np
import random
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEALS_CSV = os.path.join(BASE_DIR, "database", "data", "meals.csv")
WORKOUTS_CSV = os.path.join(BASE_DIR, "database", "data", "workouts.csv")

def calculate_daily_targets(profile: dict) -> dict:
    age = profile.get("age", 25)
    height = profile.get("height", 170.0)
    weight = profile.get("weight", 70.0)
    gender = profile.get("gender", "Male")
    goal = profile.get("goal", "General Fitness")
    fitness_level = profile.get("fitness_level", "Beginner")
    
    if gender.lower() == "male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
    multipliers = {"Beginner": 1.2, "Intermediate": 1.375, "Advanced": 1.55}
    multiplier = multipliers.get(fitness_level, 1.2)
    tdee = bmr * multiplier
    
    if goal == "Weight Loss":
        target_calories = tdee - 500
        protein_pct, carbs_pct, fat_pct = 0.35, 0.35, 0.30
    elif goal == "Muscle Gain":
        target_calories = tdee + 350
        protein_pct, carbs_pct, fat_pct = 0.30, 0.50, 0.20
    else:
        target_calories = tdee
        protein_pct, carbs_pct, fat_pct = 0.25, 0.50, 0.25
        
    target_calories = max(target_calories, 1200)
    protein_g = (target_calories * protein_pct) / 4
    carbs_g = (target_calories * carbs_pct) / 4
    fat_g = (target_calories * fat_pct) / 9
    
    monthly_budget = profile.get("budget", 5000.0)
    daily_budget = monthly_budget / 30.0
    
    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_calories": round(target_calories),
        "protein_g": round(protein_g),
        "carbs_g": round(carbs_g),
        "fat_g": round(fat_g),
        "daily_budget": round(daily_budget, 2)
    }

def get_diet_recommendation(profile: dict, targets: dict) -> dict:
    try:
        meals_df = pd.read_csv(MEALS_CSV)
    except Exception:
        meals_df = pd.DataFrame(columns=["meal", "protein", "carbs", "fat", "calories", "cost", "region", "type", "category"])
        
    pref = profile.get("food_preference", "Veg")
    
    if pref == "Vegan":
        filtered_df = meals_df[meals_df["type"].str.lower() == "vegan"]
    elif pref == "Veg":
        filtered_df = meals_df[meals_df["type"].str.lower().isin(["veg", "vegan"])]
    else:
        filtered_df = meals_df
        
    breakfast_options = filtered_df[filtered_df["category"].str.lower() == "breakfast"].to_dict("records")
    lunch_options = filtered_df[filtered_df["category"].str.lower() == "lunch"].to_dict("records")
    dinner_options = filtered_df[filtered_df["category"].str.lower() == "dinner"].to_dict("records")
    snack_options = filtered_df[filtered_df["category"].str.lower() == "snack"].to_dict("records")
    
    default_meal = {"meal": "Healthy Bowl", "protein": 15, "carbs": 40, "fat": 10, "calories": 300, "cost": 40}
    if not breakfast_options: breakfast_options = [default_meal]
    if not lunch_options: lunch_options = [default_meal]
    if not dinner_options: dinner_options = [default_meal]
    if not snack_options: snack_options = [default_meal]
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    diet_plan = {}
    daily_budget = targets["daily_budget"]
    
    for day in days:
        best_combo = None
        best_diff = float("inf")
        for _ in range(15):
            b = random.choice(breakfast_options)
            l = random.choice(lunch_options)
            d = random.choice(dinner_options)
            s = random.choice(snack_options)
            
            total_calories = b["calories"] + l["calories"] + d["calories"] + s["calories"]
            total_cost = b["cost"] + l["cost"] + d["cost"] + s["cost"]
            
            cost_penalty = 0
            if total_cost > daily_budget:
                cost_penalty = (total_cost - daily_budget) * 10
                
            cal_diff = abs(total_calories - targets["target_calories"]) + cost_penalty
            if cal_diff < best_diff:
                best_diff = cal_diff
                best_combo = (b, l, d, s)
                
        if not best_combo:
            best_combo = (breakfast_options[0], lunch_options[0], dinner_options[0], snack_options[0])
            
        b, l, d, s = best_combo
        diet_plan[day] = {
            "Breakfast": b,
            "Lunch": l,
            "Dinner": d,
            "Snack": s,
            "totals": {
                "calories": b["calories"] + l["calories"] + d["calories"] + s["calories"],
                "protein": b["protein"] + l["protein"] + d["protein"] + s["protein"],
                "carbs": b["carbs"] + l["carbs"] + d["carbs"] + s["carbs"],
                "fat": b["fat"] + l["fat"] + d["fat"] + s["fat"],
                "cost": b["cost"] + l["cost"] + d["cost"] + s["cost"]
            }
        }
    return diet_plan

def get_workout_recommendation(profile: dict) -> dict:
    try:
        workouts_df = pd.read_csv(WORKOUTS_CSV)
    except Exception:
        workouts_df = pd.DataFrame(columns=["exercise", "target", "equipment", "difficulty", "duration"])
        
    equip = profile.get("equipment", "Bodyweight")
    diff = profile.get("fitness_level", "Beginner")
    goal = profile.get("goal", "General Fitness")
    avail_time = profile.get("workout_time", 30)
    
    if equip == "Bodyweight":
        eq_filter = ["bodyweight"]
    elif equip == "Dumbbells":
        eq_filter = ["bodyweight", "dumbbells"]
    else:
        eq_filter = ["bodyweight", "dumbbells", "full gym"]
    filtered_df = workouts_df[workouts_df["equipment"].str.lower().isin(eq_filter)]
    
    if diff == "Beginner":
        diff_filter = ["beginner"]
    elif diff == "Intermediate":
        diff_filter = ["beginner", "intermediate"]
    else:
        diff_filter = ["beginner", "intermediate", "advanced"]
    filtered_df = filtered_df[filtered_df["difficulty"].str.lower().isin(diff_filter)]
    
    if filtered_df.empty:
        filtered_df = workouts_df
        
    cardio_ex = filtered_df[filtered_df["target"].str.lower().str.contains("cardio|calves")].to_dict("records")
    chest_ex = filtered_df[filtered_df["target"].str.lower().str.contains("chest")].to_dict("records")
    back_ex = filtered_df[filtered_df["target"].str.lower().str.contains("back")].to_dict("records")
    legs_ex = filtered_df[filtered_df["target"].str.lower().str.contains("quads|hamstrings|legs|glutes")].to_dict("records")
    shoulders_ex = filtered_df[filtered_df["target"].str.lower().str.contains("shoulder")].to_dict("records")
    arms_ex = filtered_df[filtered_df["target"].str.lower().str.contains("bicep|tricep")].to_dict("records")
    core_ex = filtered_df[filtered_df["target"].str.lower().str.contains("core|abs|oblique")].to_dict("records")
    
    default_ex = {"exercise": "Stretch & Walk", "target": "Cardio", "equipment": "Bodyweight", "duration": 15}
    if not cardio_ex: cardio_ex = [default_ex]
    if not chest_ex: chest_ex = [default_ex]
    if not back_ex: back_ex = [default_ex]
    if not legs_ex: legs_ex = [default_ex]
    if not shoulders_ex: shoulders_ex = [default_ex]
    if not arms_ex: arms_ex = [default_ex]
    if not core_ex: core_ex = [default_ex]
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    workout_plan = {}
    
    if goal == "Weight Loss":
        splits = {
            "Monday": ("HIIT & Core", cardio_ex + core_ex),
            "Tuesday": ("Full Body Strength", chest_ex + back_ex + legs_ex),
            "Wednesday": ("Active Recovery (Core)", core_ex),
            "Thursday": ("HIIT Cardio", cardio_ex),
            "Friday": ("Upper Body Strength", chest_ex + back_ex + shoulders_ex + arms_ex),
            "Saturday": ("Fat Burn Cardio", cardio_ex + core_ex),
            "Sunday": ("Rest Day", [])
        }
    elif goal == "Muscle Gain":
        splits = {
            "Monday": ("Push Day (Chest, Shoulders, Triceps)", chest_ex + shoulders_ex + arms_ex),
            "Tuesday": ("Pull Day (Back, Biceps)", back_ex + arms_ex),
            "Wednesday": ("Leg Day (Quads, Hamstrings, Glutes)", legs_ex),
            "Thursday": ("Rest Day", []),
            "Friday": ("Upper Body Focus", chest_ex + back_ex + shoulders_ex),
            "Saturday": ("Lower Body & Core", legs_ex + core_ex),
            "Sunday": ("Rest Day", [])
        }
    else:
        splits = {
            "Monday": ("Full Body Conditioning", chest_ex + back_ex + legs_ex + core_ex),
            "Tuesday": ("Cardio & Core Endurance", cardio_ex + core_ex),
            "Wednesday": ("Rest Day", []),
            "Thursday": ("Full Body Strength", chest_ex + back_ex + shoulders_ex + legs_ex),
            "Friday": ("Cardio Endurance", cardio_ex),
            "Saturday": ("Core & Mobility", core_ex),
            "Sunday": ("Rest Day", [])
        }
        
    for day in days:
        focus, exercise_pool = splits[day]
        if focus == "Rest Day" or not exercise_pool:
            workout_plan[day] = {"focus": "Rest Day", "exercises": []}
            continue
            
        selected_exercises = []
        current_time = 0
        pool_copy = exercise_pool.copy()
        random.shuffle(pool_copy)
        
        for ex in pool_copy:
            if current_time + ex["duration"] <= avail_time:
                selected_exercises.append({
                    "exercise": ex["exercise"],
                    "target": ex["target"],
                    "equipment": ex["equipment"],
                    "duration": ex["duration"]
                })
                current_time += ex["duration"]
                
        if len(selected_exercises) < 2 and pool_copy:
            for ex in pool_copy[:3]:
                if ex["exercise"] not in [se["exercise"] for se in selected_exercises]:
                    selected_exercises.append({
                        "exercise": ex["exercise"],
                        "target": ex["target"],
                        "equipment": ex["equipment"],
                        "duration": ex["duration"]
                    })
                    
        workout_plan[day] = {"focus": focus, "exercises": selected_exercises}
    return workout_plan

def get_recommendation_plan(profile: dict) -> tuple:
    targets = calculate_daily_targets(profile)
    diet_plan = get_diet_recommendation(profile, targets)
    workout_plan = get_workout_recommendation(profile)
    return workout_plan, diet_plan, targets
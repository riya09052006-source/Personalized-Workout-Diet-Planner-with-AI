import os
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI
from services.recommendation import get_recommendation_plan, calculate_daily_targets

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_plans_with_ai(profile: dict) -> tuple:
    api_key = os.getenv("OPENAI_API_KEY")
    targets = calculate_daily_targets(profile)
    
    if not api_key:
        logger.info("OpenAI API Key not found. Falling back to local rules-based planner.")
        workout_plan, diet_plan, _ = get_recommendation_plan(profile)
        return workout_plan, diet_plan, targets, False
        
    try:
        client = OpenAI(api_key=api_key)
        
        system_prompt = (
            "You are an expert AI Fitness & Nutrition coach. Your task is to generate a personalized "
            "7-day workout schedule and 7-day diet plan in strict JSON format. "
            "Ensure the diet plan fits within the user's budget and food preference."
        )
        
        user_prompt = f"""
        User Profile:
        - Age: {profile['age']}
        - Gender: {profile['gender']}
        - Height: {profile['height']} cm
        - Weight: {profile['weight']} kg
        - Goal: {profile['goal']}
        - Monthly Budget: ₹{profile['budget']} (Daily limit: ₹{targets['daily_budget']})
        - Food Preference: {profile['food_preference']}
        - Daily Workout Time: {profile['workout_time']} minutes
        - Fitness Level: {profile['fitness_level']}
        - Available Equipment: {profile['equipment']}
        
        Target Daily Metrics:
        - Target Calories: {targets['target_calories']} kcal
        - Protein: {targets['protein_g']}g
        - Carbs: {targets['carbs_g']}g
        - Fat: {targets['fat_g']}g
        
        Expected JSON Schema:
        {{
          "workout_plan": {{
            "Monday": {{
              "focus": "Focus Description",
              "exercises": [
                {{"exercise": "Exercise Name", "target": "Target Muscle", "equipment": "Equipment Used", "duration": 15}}
              ]
            }}
          }},
          "diet_plan": {{
            "Monday": {{
              "Breakfast": {{"meal": "Meal name", "protein": 12, "carbs": 50, "fat": 8, "calories": 320, "cost": 45}},
              "Lunch": {{"meal": "Meal name", "protein": 30, "carbs": 60, "fat": 10, "calories": 450, "cost": 75}},
              "Dinner": {{"meal": "Meal name", "protein": 25, "carbs": 40, "fat": 12, "calories": 370, "cost": 60}},
              "Snack": {{"meal": "Meal name", "protein": 8, "carbs": 20, "fat": 4, "calories": 150, "cost": 20}},
              "totals": {{"calories": 1290, "protein": 75, "carbs": 170, "fat": 34, "cost": 200}}
            }}
          }}
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2500
        )
        
        result_text = response.choices[0].message.content
        result_json = json.loads(result_text)
        
        workout_plan = result_json.get("workout_plan")
        diet_plan = result_json.get("diet_plan")
        
        if workout_plan and diet_plan:
            logger.info("Successfully generated plans with OpenAI.")
            return workout_plan, diet_plan, targets, True
        else:
            raise ValueError("Parsed JSON is missing plan structures.")
            
    except Exception as e:
        logger.error(f"Error during OpenAI generation: {e}. Falling back to local rules-based planner.")
        workout_plan, diet_plan, _ = get_recommendation_plan(profile)
        return workout_plan, diet_plan, targets, False
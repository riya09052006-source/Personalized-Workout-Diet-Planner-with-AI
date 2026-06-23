import os
import json
import hashlib
from datetime import date, datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///fitness.db")

# Convert postgres:// to postgresql:// as required by SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Only use check_same_thread connection arguments for SQLite databases
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)  # Hashed
    
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    plans = relationship("Plan", back_populates="user", uselist=False, cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = "profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    age = Column(Integer, nullable=False)
    height = Column(Float, nullable=False)  # in cm
    weight = Column(Float, nullable=False)  # in kg
    gender = Column(String, nullable=False)
    goal = Column(String, nullable=False)  # Weight Loss, Muscle Gain, Endurance, General Fitness
    budget = Column(Float, nullable=False)  # Monthly budget in local currency (e.g., INR)
    food_preference = Column(String, nullable=False)  # Veg, Non-Veg, Vegan
    workout_time = Column(Integer, nullable=False)  # Minutes per day
    fitness_level = Column(String, nullable=False)  # Beginner, Intermediate, Advanced
    equipment = Column(String, nullable=False)  # Bodyweight, Dumbbells, Full Gym
    
    user = relationship("User", back_populates="profile")

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    weight = Column(Float, nullable=True)
    calories_consumed = Column(Integer, nullable=True)
    water_intake_ml = Column(Integer, nullable=True)
    workout_completed = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="progress")

class Plan(Base):
    __tablename__ = "plans"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    workout_plan = Column(Text, nullable=False)  # JSON String
    diet_plan = Column(Text, nullable=False)  # JSON String
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="plans")

# Helper functions
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name: str, email: str, password: str):
    db = get_db()
    try:
        existing_user = db.query(User).filter(User.email == email.lower()).first()
        if existing_user:
            return None
        
        hashed = hash_password(password)
        new_user = User(name=name, email=email.lower(), password=hashed)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    finally:
        db.close()

def authenticate_user(email: str, password: str):
    db = get_db()
    try:
        hashed = hash_password(password)
        user = db.query(User).filter(User.email == email.lower(), User.password == hashed).first()
        return user
    finally:
        db.close()

def save_profile(user_id: int, age: int, height: float, weight: float, gender: str, goal: str, 
                 budget: float, food_preference: str, workout_time: int, fitness_level: str, equipment: str):
    db = get_db()
    try:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if profile:
            profile.age = age
            profile.height = height
            profile.weight = weight
            profile.gender = gender
            profile.goal = goal
            profile.budget = budget
            profile.food_preference = food_preference
            profile.workout_time = workout_time
            profile.fitness_level = fitness_level
            profile.equipment = equipment
        else:
            profile = Profile(
                user_id=user_id, age=age, height=height, weight=weight, gender=gender, goal=goal,
                budget=budget, food_preference=food_preference, workout_time=workout_time,
                fitness_level=fitness_level, equipment=equipment
            )
            db.add(profile)
        db.commit()
        return profile
    finally:
        db.close()

def get_profile(user_id: int):
    db = get_db()
    try:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if profile:
            return {
                "age": profile.age,
                "height": profile.height,
                "weight": profile.weight,
                "gender": profile.gender,
                "goal": profile.goal,
                "budget": profile.budget,
                "food_preference": profile.food_preference,
                "workout_time": profile.workout_time,
                "fitness_level": profile.fitness_level,
                "equipment": profile.equipment
            }
        return None
    finally:
        db.close()

def save_plan(user_id: int, workout_plan_dict: dict, diet_plan_dict: dict):
    db = get_db()
    try:
        plan = db.query(Plan).filter(Plan.user_id == user_id).first()
        workout_str = json.dumps(workout_plan_dict)
        diet_str = json.dumps(diet_plan_dict)
        
        if plan:
            plan.workout_plan = workout_str
            plan.diet_plan = diet_str
            plan.updated_at = datetime.utcnow()
        else:
            plan = Plan(user_id=user_id, workout_plan=workout_str, diet_plan=diet_str)
            db.add(plan)
        db.commit()
        return plan
    finally:
        db.close()

def get_plan(user_id: int):
    db = get_db()
    try:
        plan = db.query(Plan).filter(Plan.user_id == user_id).first()
        if plan:
            return {
                "workout_plan": json.loads(plan.workout_plan),
                "diet_plan": json.loads(plan.diet_plan),
                "updated_at": plan.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        return None
    finally:
        db.close()

def log_progress(user_id: int, log_date: date, weight: float, calories_consumed: int, water_intake_ml: int, workout_completed: bool):
    db = get_db()
    try:
        entry = db.query(Progress).filter(Progress.user_id == user_id, Progress.date == log_date).first()
        if entry:
            if weight is not None:
                entry.weight = weight
            if calories_consumed is not None:
                entry.calories_consumed = calories_consumed
            if water_intake_ml is not None:
                entry.water_intake_ml = water_intake_ml
            if workout_completed is not None:
                entry.workout_completed = workout_completed
        else:
            entry = Progress(
                user_id=user_id,
                date=log_date,
                weight=weight,
                calories_consumed=calories_consumed,
                water_intake_ml=water_intake_ml,
                workout_completed=workout_completed
            )
            db.add(entry)
        db.commit()
        return entry
    finally:
        db.close()

def get_progress_history(user_id: int):
    db = get_db()
    try:
        entries = db.query(Progress).filter(Progress.user_id == user_id).order_by(Progress.date.asc()).all()
        history = []
        for entry in entries:
            history.append({
                "date": entry.date.strftime("%Y-%m-%d"),
                "weight": entry.weight,
                "calories_consumed": entry.calories_consumed,
                "water_intake_ml": entry.water_intake_ml,
                "workout_completed": entry.workout_completed
            })
        return history
    finally:
        db.close()
def clean_html(html: str) -> str:
    """Helper to clean leading whitespace and newlines from HTML strings to prevent Streamlit's markdown parser from rendering them as code blocks."""
    return "".join(line.strip() for line in html.splitlines())

def glass_card(title: str, content: str, subtitle: str = "", gradient_border: bool = False) -> str:
    border_style = "border: 1px solid rgba(255, 255, 255, 0.15);"
    if gradient_border:
        border_style = "border: 1px solid transparent; border-image: linear-gradient(135deg, #00F2FE, #4FACFE) 1;"
        
    html = f"""
    <div style="
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        {border_style}
    ">
        <h4 style="margin: 0 0 10px 0; color: #00F2FE; font-family: 'Outfit', sans-serif; font-size: 1.15rem;">{title}</h4>
        <div style="font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-bottom: 5px;">{content}</div>
        {f'<div style="color: #94A3B8; font-size: 0.85rem;">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    return clean_html(html)

def stat_metric_grid(metrics: list) -> str:
    cols_html = ""
    for m in metrics:
        cols_html += f"""
        <div style="
            flex: 1;
            min-width: 140px;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(8px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 16px;
            margin: 8px;
            text-align: center;
        ">
            <div style="color: #94A3B8; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 8px;">{m.get('label', '')}</div>
            <div style="color: #ffffff; font-size: 1.6rem; font-weight: 700; margin-bottom: 4px;">{m.get('value', '')}</div>
            <div style="color: #00F2FE; font-size: 0.75rem; font-weight: 500;">{m.get('sub', '')}</div>
        </div>
        """
    return clean_html(f'<div style="display: flex; flex-wrap: wrap; margin: -8px; justify-content: space-between; width: 100%;">{cols_html}</div>')

def meal_card(meal_type: str, meal_name: str, calories: int, protein: int, carbs: int, fat: int, cost: float) -> str:
    html = f"""
    <div style="
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 15px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="
                background: linear-gradient(135deg, #00F2FE, #4FACFE);
                color: #0B0F19;
                font-size: 0.75rem;
                font-weight: 700;
                padding: 4px 12px;
                border-radius: 20px;
                text-transform: uppercase;
            ">{meal_type}</span>
            <span style="color: #4FACFE; font-weight: 700; font-size: 1.1rem;">₹{cost:.1f}</span>
        </div>
        <div style="color: #ffffff; font-size: 1.15rem; font-weight: 600; margin-bottom: 15px;">{meal_name}</div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            <div style="background: rgba(255, 255, 255, 0.05); color: #fff; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem;">
                🔥 <strong style="color: #4FACFE;">{calories}</strong> kcal
            </div>
            <div style="background: rgba(255, 255, 255, 0.05); color: #fff; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem;">
                🥩 <strong style="color: #38ef7d;">{protein}g</strong> Protein
            </div>
            <div style="background: rgba(255, 255, 255, 0.05); color: #fff; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem;">
                🌾 <strong style="color: #ff9966;">{carbs}g</strong> Carbs
            </div>
            <div style="background: rgba(255, 255, 255, 0.05); color: #fff; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem;">
                🥑 <strong style="color: #ff5e62;">{fat}g</strong> Fat
            </div>
        </div>
    </div>
    """
    return clean_html(html)

def workout_card(exercise_name: str, target: str, equipment: str, duration: int) -> str:
    html = f"""
    <div style="
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div>
            <div style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin-bottom: 6px;">{exercise_name}</div>
            <div style="display: flex; gap: 8px;">
                <span style="background: rgba(0, 242, 254, 0.1); color: #00F2FE; font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">{target}</span>
                <span style="background: rgba(255, 255, 255, 0.08); color: #94A3B8; font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">{equipment}</span>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="color: #4FACFE; font-size: 1.3rem; font-weight: 700;">{duration}</div>
            <div style="color: #94A3B8; font-size: 0.7rem; text-transform: uppercase;">mins</div>
        </div>
    </div>
    """
    return clean_html(html)

def custom_progress_bar(label: str, val: float, max_val: float, color: str = "#00F2FE") -> str:
    pct = min((val / max_val) * 100 if max_val > 0 else 0, 100)
    html = f"""
    <div style="margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="color: #94A3B8; font-size: 0.85rem;">{label}</span>
            <span style="color: #ffffff; font-size: 0.85rem; font-weight: 600;">{val:.0f} / {max_val:.0f}</span>
        </div>
        <div style="width: 100%; background: rgba(255, 255, 255, 0.08); height: 8px; border-radius: 4px; overflow: hidden;">
            <div style="width: {pct:.1f}%; background: {color}; height: 100%; border-radius: 4px;"></div>
        </div>
    </div>
    """
    return clean_html(html)
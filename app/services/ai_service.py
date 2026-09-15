import json
from openai import OpenAI
from fastapi import HTTPException
from pydantic import ValidationError
from app.core.config import settings
from app.schemas.watch import AIWatchData

# Initialize the AI Client (Groq/Owen)
client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def analyze_watch_with_ai(brand: str, model_name: str) -> AIWatchData:
    prompt = f"""
    Analyze this watch: Brand: {brand}, Model: {model_name}.
    Return ONLY a raw JSON object with no markdown formatting.
    Required keys:
    - "is_automatic": boolean
    - "movement_type": string (e.g., "Automatic", "Quartz", "Manual")
    - "case_size_mm": float (e.g., 40.5)
    - "crystal_type": string (e.g., "Sapphire", "Mineral", "Hardlex")
    - "water_resistance_m": integer (e.g., 200, 50)
    - "strap_type": string
    - "power_reserve_hours": integer or null
    - "ai_confidence": float between 0.0 and 1.0 (lower if you are guessing)
    """

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI service is currently unavailable."
        )

    ai_output = response.choices[0].message.content.strip()

    if ai_output.startswith("```json"):
        ai_output = ai_output.replace("```json", "").replace("```", "").strip()
    elif ai_output.startswith("```"):
        ai_output = ai_output.replace("```", "").strip()

    try:
        raw_data = json.loads(ai_output)
        ai_data = AIWatchData(**raw_data)
        return ai_data
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI returned invalid data structure: {str(e)}"
        )


def extract_watch_info_from_text(description: str) -> dict:
    """
    Extracts watch details from a natural language description.
    """
    prompt = f"""
    Extract watch details from the following text and return ONLY a raw JSON object with no markdown formatting.
    Keys required: brand, model_name, is_automatic (boolean), movement_type, case_size_mm, crystal_type, water_resistance_m, strap_type. 
    Text: '{description}'
    """

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        ai_output = response.choices[0].message.content.strip()

        if ai_output.startswith("```json"):
            ai_output = ai_output.replace("```json", "").replace("```", "").strip()
        elif ai_output.startswith("```"):
            ai_output = ai_output.replace("```", "").strip()

        return json.loads(ai_output)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI extraction failed: {str(e)}"
        )


def parse_recommendation_query(user_query: str) -> dict:
    """
    Converts natural language into structured SQL filters for watch recommendations.
    """
    prompt = f"""
    You are a watch expert API. Extract search filters from the user's natural language query.
    Return ONLY a raw JSON object (no markdown). Do not guess fields if not mentioned.
    Possible JSON keys to output (only include if the user implies them):
    - "max_price": float
    - "min_price": float
    - "movement_type": string (e.g., "Automatic", "Quartz")
    - "brand": string
    - "max_case_size": float
    - "min_case_size": float

    User Query: "{user_query}"
    """

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        ai_output = response.choices[0].message.content.strip()

        if ai_output.startswith("```json"):
            ai_output = ai_output.replace("```json", "").replace("```", "").strip()
        elif ai_output.startswith("```"):
            ai_output = ai_output.replace("```", "").strip()

        return json.loads(ai_output)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI failed to parse recommendation query: {str(e)}"
        )
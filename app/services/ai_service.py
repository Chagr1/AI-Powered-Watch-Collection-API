import json
from openai import OpenAI
from fastapi import HTTPException
from pydantic import ValidationError
from app.core.config import settings
from app.schemas.watch import AIWatchData


client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def analyze_watch_with_ai(brand: str, model_name: str) -> AIWatchData:
    """
    Marka ve model bilgisini alıp, Groq LLM üzerinden teknik detayları çeker
    ve Pydantic şeması (AIWatchData) ile doğrulanmış olarak geri döndürür.
    """
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
    Kullanıcının girdiği doğal metni analiz edip yapılandırılmış JSON verisi döner.
    """

    # GERÇEK OPENAI KODU (API Key'in olduğunda bunu kullanırsın):
    """
    prompt = f"Extract watch details from the following text and return ONLY a valid JSON object with keys: brand, model_name, is_automatic (boolean), movement_type, case_size_mm, crystal_type, water_resistance_m, strap_type. Text: '{description}'"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return json.loads(response.choices[0].message.content)
    """

    # ŞİMDİLİK TEST İÇİN MOCK (SAHTE) YANIT:
    # Metin içinde Tissot geçerse onu döndürelim, geçmezse standart bir şey dönsün.
    if "tissot" in description.lower():
        return {
            "brand": "Tissot",
            "model_name": "PRX Powermatic 80",
            "is_automatic": True,
            "movement_type": "Automatic",
            "case_size_mm": 40.0,
            "crystal_type": "Sapphire",
            "water_resistance_m": 100,
            "strap_type": "Stainless Steel",
            "ai_confidence": 0.95
        }

    return {
        "brand": "Unknown",
        "model_name": "Unknown Model",
        "is_automatic": False,
        "movement_type": "Unknown",
        "case_size_mm": 0.0,
        "crystal_type": "Unknown",
        "water_resistance_m": 0,
        "strap_type": "Unknown",
        "ai_confidence": 0.30
    }
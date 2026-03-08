import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from core.config import settings
from pydantic import BaseModel
import json
import datetime

router = APIRouter()

class VoiceInput(BaseModel):
    text: str

@router.post("/process-voice")
async def process_voice_text(input_data: VoiceInput):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")

    genai.configure(api_key=settings.GEMINI_API_KEY)
    # Cambiamos a -latest que suele ser más compatible
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    Eres un asistente contable experto. Tu tarea es extraer datos de un gasto o ingreso a partir de un texto en español.

    TEXTO: "{input_data.text}"
    FECHA ACTUAL: {datetime.date.today().isoformat()}

    Reglas:
    1. Devuelve EXCLUSIVAMENTE un JSON válido. No incluyas explicaciones ni formato markdown.
    2. Si el texto no especifica fecha, usa la FECHA ACTUAL.
    3. 'movement_type' debe ser "expense" o "income".
    4. 'amount' debe ser un número (float o int).
    5. 'description' debe ser breve y descriptiva (máximo 50 caracteres).

    FORMATO JSON ESPERADO:
    {{
      "amount": number,
      "description": "string",
      "date": "YYYY-MM-DD",
      "movement_type": "expense" | "income"
    }}
    """

    try:
        # Usamos el modelo 2.0 Flash que está disponible en tu cuenta y es súper rápido
        model_name = 'gemini-2.0-flash'
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        text_response = response.text

        # Limpieza de JSON
        json_start = text_response.find('{')
        json_end = text_response.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            return json.loads(text_response[json_start:json_end])
        else:
            raise ValueError(f"No JSON found in response: {text_response}")

    except Exception as e:
        print(f"Gemini Error (Attempt 1 with {model_name}): {e}")
        
        # Fallback dinámico basado en tu lista real de modelos
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Buscamos cualquier otro modelo 'flash' disponible
            flash_models = [m for m in available_models if 'flash' in m]
            if flash_models:
                fallback_name = flash_models[0]
                print(f"Intentando fallback con: {fallback_name}")
                model = genai.GenerativeModel(fallback_name)
                response = model.generate_content(prompt)
                json_start = response.text.find('{')
                json_end = response.text.rfind('}') + 1
                return json.loads(response.text[json_start:json_end])
        except Exception as diag_err:
            print(f"Error en el fallback: {diag_err}")
            
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

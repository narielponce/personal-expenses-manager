import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.config import settings
from pydantic import BaseModel
import json
import datetime
import crud
from database import get_db
from core.security import get_current_user
from schemas import ExpenseCreate

router = APIRouter()

class VoiceInput(BaseModel):
    text: str

async def _extract_voice_data(text: str):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")

    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    prompt = f"""
    Eres un asistente contable experto. Tu tarea es extraer datos de un gasto o ingreso a partir de un texto en español.

    TEXTO: "{text}"
    FECHA ACTUAL: {datetime.date.today().isoformat()}

    Reglas:
    1. Devuelve EXCLUSIVAMENTE un JSON válido. No incluyas explicaciones ni formato markdown.
    2. Si el texto no especifica fecha, usa la FECHA ACTUAL.
    3. 'movement_type' debe ser "expense" o "income".
    4. 'amount' debe ser un número (float o int).
    5. 'description' debe ser breve y descriptiva (máximo 50 caracteres).
    6. Intenta inferir el 'account_hint' (ej. Visa, Mastercard, Efectivo, Banco). Si no se menciona, devuelve null.
    7. Si se menciona pago en cuotas, devuelve el número en 'installments' (ej. 6). De lo contrario, null.
    8. Intenta inferir el 'recipient_hint' (la persona, tienda o entidad a la que se paga o de quien se recibe). Si no, null.
    9. Intenta inferir una 'category_hint' (ej. Supermercado, Ropa, Combustible, etc.). Si no, null.

    FORMATO JSON ESPERADO:
    {{
      "amount": number,
      "description": "string",
      "date": "YYYY-MM-DD",
      "movement_type": "expense" | "income",
      "account_hint": "string" | null,
      "installments": number | null,
      "recipient_hint": "string" | null,
      "category_hint": "string" | null
    }}
    """

    try:
        model_name = 'gemini-2.0-flash'
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        text_response = response.text

        json_start = text_response.find('{')
        json_end = text_response.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            return json.loads(text_response[json_start:json_end])
        else:
            raise ValueError(f"No JSON found in response: {text_response}")

    except Exception as e:
        print(f"Gemini Error (Attempt 1 with {model_name}): {e}")
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            flash_models = [m for m in available_models if 'flash' in m]
            if flash_models:
                fallback_name = flash_models[0]
                model = genai.GenerativeModel(fallback_name)
                response = model.generate_content(prompt)
                json_start = response.text.find('{')
                json_end = response.text.rfind('}') + 1
                return json.loads(response.text[json_start:json_end])
        except Exception as diag_err:
            print(f"Error en el fallback: {diag_err}")
            
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@router.post("/process-voice")
async def process_voice_text(input_data: VoiceInput):
    return await _extract_voice_data(input_data.text)

@router.post("/process-voice-and-save")
async def process_voice_and_save(
    input_data: VoiceInput, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    extracted_data = await _extract_voice_data(input_data.text)
    
    # Try to find IDs based on hints
    account_id = None
    if extracted_data.get("account_hint"):
        accounts = crud.get_accounts_by_tenant(db, current_user.tenant_id)
        for acc in accounts:
            if extracted_data["account_hint"].lower() in acc.name.lower():
                account_id = acc.id
                break
    
    category_id = None
    if extracted_data.get("category_hint"):
        categories = crud.get_categories_by_tenant(db, current_user.tenant_id)
        for cat in categories:
            if extracted_data["category_hint"].lower() in cat.name.lower():
                category_id = cat.id
                break

    recipient_id = None
    if extracted_data.get("recipient_hint"):
        recipients = crud.get_recipients_by_tenant(db, current_user.tenant_id)
        for rec in recipients:
            if extracted_data["recipient_hint"].lower() in rec.name.lower():
                recipient_id = rec.id
                break

    expense_create = ExpenseCreate(
        description=extracted_data["description"],
        amount=extracted_data["amount"],
        date=datetime.datetime.strptime(extracted_data["date"], "%Y-%m-%d").date(),
        application_date=datetime.datetime.strptime(extracted_data["date"], "%Y-%m-%d").date(),
        movement_type=extracted_data["movement_type"],
        category_id=category_id,
        account_id=account_id,
        recipient_id=recipient_id,
        is_installment=extracted_data.get("installments") is not None,
        num_installments=extracted_data.get("installments"),
        status="pending"
    )
    
    db_expense = crud.create_expense(db, expense_create, current_user.id, current_user.tenant_id)
    return db_expense

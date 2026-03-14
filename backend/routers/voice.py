import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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

def _get_available_models():
    """Devuelve la lista de modelos disponibles priorizando los de cuota estable (1.5)."""
    try:
        if not settings.GEMINI_API_KEY:
            return []
            
        genai.configure(api_key=settings.GEMINI_API_KEY)
        models = genai.list_models()
        available = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        # Ajustamos el orden de preferencia basado en los logs reales
        # Priorizamos 'flash-latest' que es el 1.5 estable
        pref_order = ['flash-latest', '1.5-flash', 'pro-latest', '1.5-pro', '2.0-flash']
        sorted_models = []
        
        for pref in pref_order:
            for m in available:
                if pref in m and m not in sorted_models:
                    sorted_models.append(m)
        
        for m in available:
            if m not in sorted_models:
                sorted_models.append(m)
                
        print(f"DEBUG - Modelos ordenados por prioridad: {sorted_models}")
        return sorted_models
    except Exception as e:
        print(f"Error listando modelos: {e}")
        return ['models/gemini-1.5-flash', 'models/gemini-flash-latest']

async def _extract_with_fallback(prompt, contents=None):
    """Intenta extraer datos usando los modelos disponibles uno por uno."""
    models_to_try = _get_available_models()
    
    last_error = None
    for model_name in models_to_try:
        # Saltamos modelos que sabemos que fallan por cuota 0 en free tier (2.5, 3.0, 3.1)
        if any(x in model_name for x in ['2.5', '3.0', '3.1']):
            continue
            
        try:
            print(f"DEBUG - Intentando con: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            if contents:
                response = model.generate_content(contents)
            else:
                response = model.generate_content(prompt)
                
            text_response = response.text
            json_start = text_response.find('{')
            json_end = text_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                return json.loads(text_response[json_start:json_end])
            else:
                raise ValueError("Respuesta sin JSON")
                
        except Exception as e:
            last_error = e
            print(f"WARN - Falló {model_name}: {str(e)}")
            if "429" not in str(e) and "404" not in str(e):
                break
            continue
            
    if "429" in str(last_error):
        raise HTTPException(status_code=429, detail="Cuotas de IA agotadas. Intenta usar gemini-1.5-flash manualmente.")
    raise HTTPException(status_code=500, detail=f"Error IA: {str(last_error)}")

async def _extract_voice_data(text: str):
    prompt = f"Extrae datos de este gasto en JSON: '{text}'. Fecha actual: {datetime.date.today().isoformat()}. JSON: {{amount, description, date, movement_type, account_hint, installments, recipient_hint, category_hint}}"
    return await _extract_with_fallback(prompt)

async def _extract_image_data(file_bytes: bytes, mime_type: str):
    prompt = f"Analiza este ticket. Extrae datos en JSON. Fecha actual: {datetime.date.today().isoformat()}. JSON: {{amount, description, date, movement_type: 'expense', account_hint, installments, recipient_hint, category_hint}}"
    contents = [prompt, {"mime_type": mime_type, "data": file_bytes}]
    return await _extract_with_fallback(prompt, contents)

async def _save_extracted_expense(extracted_data: dict, db: Session, current_user):
    account_id = None
    if extracted_data.get("account_hint"):
        accounts = crud.get_accounts_by_tenant(db, current_user.tenant_id)
        hint = extracted_data["account_hint"].lower()
        for acc in accounts:
            if hint in acc.name.lower() or acc.name.lower() in hint:
                account_id = acc.id
                break
    
    category_id = None
    if extracted_data.get("category_hint"):
        categories = crud.get_categories_by_tenant(db, current_user.tenant_id)
        hint = extracted_data["category_hint"].lower()
        for cat in categories:
            if hint in cat.name.lower() or cat.name.lower() in hint:
                category_id = cat.id
                break

    recipient_id = None
    if extracted_data.get("recipient_hint"):
        recipients = crud.get_recipients_by_tenant(db, current_user.tenant_id)
        hint = extracted_data["recipient_hint"].lower()
        for rec in recipients:
            if hint in rec.name.lower() or rec.name.lower() in hint:
                recipient_id = rec.id
                break

    expense_create = ExpenseCreate(
        description=extracted_data.get("description") or "Gasto por IA",
        amount=extracted_data.get("amount") or 0,
        date=datetime.datetime.strptime(extracted_data.get("date") or datetime.date.today().isoformat(), "%Y-%m-%d").date(),
        application_date=datetime.datetime.strptime(extracted_data.get("date") or datetime.date.today().isoformat(), "%Y-%m-%d").date(),
        movement_type=extracted_data.get("movement_type", "expense"),
        category_id=category_id,
        account_id=account_id,
        recipient_id=recipient_id,
        is_installment=extracted_data.get("installments") is not None,
        num_installments=extracted_data.get("installments"),
        status="pending"
    )
    
    return crud.create_expense(db, expense_create, current_user.id, current_user.tenant_id)

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
    return await _save_extracted_expense(extracted_data, db, current_user)

@router.post("/process-image-and-save")
async def process_image_and_save(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        file_bytes = await file.read()
        extracted_data = await _extract_image_data(file_bytes, file.content_type)
        return await _save_extracted_expense(extracted_data, db, current_user)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error en process_image_and_save: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

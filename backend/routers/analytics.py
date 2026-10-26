import time
from datetime import date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from core.security import get_current_user
from models.user import User
from schemas import BudgetCreate, BudgetUpdate, Budget as BudgetSchema, BudgetResponse
import crud
from services.analytics import (
    get_monthly_projection,
    detect_recurrent_candidates,
    get_category_burn_rate
)
from services.ai_advisor import (
    generate_financial_diagnosis,
    simulate_purchase_impact
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Cache simple en memoria para el diagnóstico de IA (TTL: 15 minutos)
# clave: f"{tenant_id}_{year}_{month}", valor: {"timestamp": float, "data": dict}
_advisor_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 900  # 15 minutos


class SimulationRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Monto total de la compra")
    installments: int = Field(1, ge=1, le=60, description="Cantidad de cuotas")
    description: str = Field("Compra planeada", description="Descripción del artículo")
    category_id: Optional[int] = None
    category_name: Optional[str] = "General"


@router.get("/summary")
def get_analytics_summary(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve la proyección de cierre de mes, tasa de gasto diario,
    seguimiento de presupuesto por categoría y candidatos a gastos recurrentes.
    """
    now = date.today()
    target_month = month or now.month
    target_year = year or now.year
    target_date = date(target_year, target_month, min(now.day, 28) if (target_month == now.month and target_year == now.year) else 1)

    projection = get_monthly_projection(db, current_user.tenant_id, target_date)
    burn_rate = get_category_burn_rate(db, current_user.tenant_id, target_month, target_year)
    recurrents = detect_recurrent_candidates(db, current_user.tenant_id)

    return {
        "projection": projection,
        "burn_rate": burn_rate,
        "recurrent_candidates": recurrents
    }


@router.get("/advisor")
def get_ai_advisor(
    force: bool = Query(False, description="Forzar regeneración ignorando caché"),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve el diagnóstico financiero estructurado generado por IA.
    Utiliza caché en memoria para optimizar llamadas al SDK de Gemini.
    """
    now = date.today()
    target_month = month or now.month
    target_year = year or now.year
    target_date = date(target_year, target_month, min(now.day, 28) if (target_month == now.month and target_year == now.year) else 1)

    cache_key = f"{current_user.tenant_id}_{target_year}_{target_month}"
    current_time = time.time()

    if not force and cache_key in _advisor_cache:
        cached = _advisor_cache[cache_key]
        if current_time - cached["timestamp"] < CACHE_TTL_SECONDS:
            return {
                **cached["data"],
                "cached": True,
                "cached_at": cached["timestamp"]
            }

    # Calcular métricas para el diagnóstico
    projection = get_monthly_projection(db, current_user.tenant_id, target_date)
    burn_rate = get_category_burn_rate(db, current_user.tenant_id, target_month, target_year)
    recurrents = detect_recurrent_candidates(db, current_user.tenant_id)

    diagnosis = generate_financial_diagnosis(projection, burn_rate, recurrents)

    _advisor_cache[cache_key] = {
        "timestamp": current_time,
        "data": diagnosis
    }

    return {
        **diagnosis,
        "cached": False
    }


@router.post("/simulate")
def simulate_purchase(
    request: SimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Simula una compra planeada en cuotas y evalúa su impacto en el flujo de caja
    con análisis semafórico de IA (Verde, Amarillo, Rojo).
    """
    now = date.today()
    projection = get_monthly_projection(db, current_user.tenant_id, now)

    category_name = request.category_name
    if request.category_id:
        cat = crud.get_category(db, request.category_id, current_user.tenant_id)
        if cat:
            category_name = cat.name

    purchase_data = {
        "amount": request.amount,
        "installments": request.installments,
        "description": request.description,
        "category_name": category_name
    }

    simulation = simulate_purchase_impact(projection, purchase_data)
    return simulation


# Endpoints de Presupuestos (Budgets)
@router.get("/budgets", response_model=List[BudgetResponse])
def list_budgets(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista presupuestos mensuales asignados por categoría con el gasto real."""
    now = date.today()
    target_month = month or now.month
    target_year = year or now.year

    burn_rate = get_category_burn_rate(db, current_user.tenant_id, target_month, target_year)
    budgets_map = {b["category_id"]: b for b in burn_rate["budgets"]}

    raw_budgets = crud.get_budgets(db, current_user.tenant_id, target_month, target_year)
    res = []
    for b in raw_budgets:
        info = budgets_map.get(b.category_id, {})
        res.append(BudgetResponse(
            id=b.id,
            user_id=b.user_id,
            tenant_id=b.tenant_id,
            category_id=b.category_id,
            category_name=info.get("category_name", "Categoría"),
            month=b.month,
            year=b.year,
            allocated_amount=b.allocated_amount,
            spent_amount=info.get("spent_amount", 0.0),
            percentage_spent=info.get("percentage_spent", 0.0),
            created_at=b.created_at
        ))
    return res


@router.post("/budgets", response_model=BudgetSchema)
def set_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea o actualiza un presupuesto para una categoría en el mes indicado."""
    return crud.create_or_update_budget(db, budget_in, current_user.id, current_user.tenant_id)


@router.delete("/budgets/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina un presupuesto."""
    success = crud.delete_budget(db, budget_id, current_user.tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return {"message": "Presupuesto eliminado con éxito"}

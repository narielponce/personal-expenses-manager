import calendar
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import extract, func, and_
from models.expense import Expense
from models.budget import Budget
from models.category import Category


def get_monthly_projection(db: Session, tenant_id: int, target_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Calcula la proyección de cierre de mes distinguiendo gastos fijos/recurrentes
    de gastos variables y determinando el run-rate diario.
    """
    now = date.today()
    target = target_date or now
    year = target.year
    month = target.month

    _, days_in_month = calendar.monthrange(year, month)

    # Determinamos días transcurridos respecto al mes objetivo
    if (year, month) < (now.year, now.month):
        days_elapsed = days_in_month
        is_current_month = False
    elif (year, month) > (now.year, now.month):
        days_elapsed = 0
        is_current_month = False
    else:
        days_elapsed = max(1, now.day)
        is_current_month = True

    days_remaining = max(0, days_in_month - days_elapsed)

    # Obtenemos todos los movimientos completados del mes
    expenses = db.query(Expense).filter(
        Expense.tenant_id == tenant_id,
        Expense.status == "completed",
        extract('month', Expense.application_date) == month,
        extract('year', Expense.application_date) == year
    ).all()

    income_list = [e for e in expenses if e.movement_type == "income"]
    expense_list = [e for e in expenses if e.movement_type == "expense"]

    total_income = sum(e.amount for e in income_list)
    total_spent_so_far = sum(e.amount for e in expense_list)

    # Separar fijos/recurrentes de variables
    recurring_expenses = [e for e in expense_list if getattr(e, "is_recurring", False) is True]
    variable_expenses = [e for e in expense_list if getattr(e, "is_recurring", False) is not True]

    fixed_spent = sum(e.amount for e in recurring_expenses)
    variable_spent = sum(e.amount for e in variable_expenses)

    # Tasa de gasto diario variable
    if days_elapsed > 0:
        daily_variable_rate = variable_spent / days_elapsed
    else:
        daily_variable_rate = 0.0

    # Proyección a fin de mes:
    # Si ya terminó el mes, la proyección es el total real
    if not is_current_month and (year, month) < (now.year, now.month):
        projected_month_end = total_spent_so_far
        projected_variable = variable_spent
    elif days_elapsed > 0:
        projected_variable = daily_variable_rate * days_in_month
        projected_month_end = fixed_spent + projected_variable
    else:
        projected_month_end = 0.0
        projected_variable = 0.0

    projected_balance = (total_income - projected_month_end) if total_income > 0 else None

    # Porcentaje del mes transcurrido vs porcentaje de presupuesto/proyección
    time_progress_pct = round((days_elapsed / days_in_month) * 100, 1) if days_in_month > 0 else 0

    return {
        "month": month,
        "year": year,
        "days_in_month": days_in_month,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "is_current_month": is_current_month,
        "time_progress_pct": time_progress_pct,
        "total_spent_so_far": round(total_spent_so_far, 2),
        "fixed_recurring_spent": round(fixed_spent, 2),
        "variable_spent_so_far": round(variable_spent, 2),
        "daily_variable_rate": round(daily_variable_rate, 2),
        "projected_month_end": round(projected_month_end, 2),
        "projected_variable": round(projected_variable, 2),
        "total_income": round(total_income, 2),
        "projected_balance": round(projected_balance, 2) if projected_balance is not None else None,
        "actual_balance_so_far": round(total_income - total_spent_so_far, 2)
    }


def detect_recurrent_candidates(db: Session, tenant_id: int) -> List[Dict[str, Any]]:
    """
    Analiza gastos repetidos en los últimos meses con descripciones y montos similares
    que aún no estén marcados como `is_recurring=True`.
    """
    today = date.today()
    three_months_ago = today - timedelta(days=120)

    # Buscamos gastos de los últimos 4 meses
    expenses = db.query(Expense).filter(
        Expense.tenant_id == tenant_id,
        Expense.movement_type == "expense",
        Expense.status == "completed",
        Expense.date >= three_months_ago,
        (Expense.is_recurring == False) | (Expense.is_recurring.is_(None))
    ).all()

    # Mapeo por descripción normalizada
    patterns: Dict[str, List[Expense]] = {}
    for exp in expenses:
        if not exp.description or len(exp.description.strip()) < 3:
            continue
        key = exp.description.strip().lower()
        patterns.setdefault(key, []).append(exp)

    candidates = []
    for key, items in patterns.items():
        if len(items) < 2:
            continue

        # Verificar si ocurren en meses distintos
        months_set = {(e.date.year, e.date.month) for e in items}
        if len(months_set) >= 2:
            amounts = [e.amount for e in items]
            avg_amount = sum(amounts) / len(amounts)
            # Verificamos si la variación de montos es baja (menos del 20%)
            max_dev = max(abs(a - avg_amount) for a in amounts)
            if avg_amount > 0 and (max_dev / avg_amount) < 0.25:
                latest_item = max(items, key=lambda x: x.date)
                category_name = latest_item.category.name if latest_item.category else "Sin Categoría"
                candidates.append({
                    "description": latest_item.description,
                    "average_amount": round(avg_amount, 2),
                    "occurrences": len(items),
                    "months_detected": len(months_set),
                    "category_id": latest_item.category_id,
                    "category_name": category_name,
                    "last_date": latest_item.date.isoformat()
                })

    return sorted(candidates, key=lambda x: x["occurrences"], reverse=True)


def get_category_burn_rate(db: Session, tenant_id: int, month: int, year: int) -> Dict[str, Any]:
    """
    Compara gasto real por categoría contra el presupuesto asignado en `Budget`.
    Determina si al ritmo actual se agotará el presupuesto antes de fin de mes.
    """
    now = date.today()
    _, days_in_month = calendar.monthrange(year, month)

    if (year, month) < (now.year, now.month):
        days_elapsed = days_in_month
    elif (year, month) > (now.year, now.month):
        days_elapsed = 0
    else:
        days_elapsed = max(1, now.day)

    pace_pct = (days_elapsed / days_in_month) * 100 if days_in_month > 0 else 0

    # Presupuestos definidos para el mes
    budgets = db.query(Budget).filter(
        Budget.tenant_id == tenant_id,
        Budget.month == month,
        Budget.year == year
    ).all()

    # Gastos reales del mes
    expenses = db.query(Expense).filter(
        Expense.tenant_id == tenant_id,
        Expense.movement_type == "expense",
        Expense.status == "completed",
        extract('month', Expense.application_date) == month,
        extract('year', Expense.application_date) == year
    ).all()

    # Gastos agrupados por category_id
    cat_spent: Dict[Optional[int], float] = {}
    for exp in expenses:
        cat_spent[exp.category_id] = cat_spent.get(exp.category_id, 0.0) + exp.amount

    # Traer nombres de categorías
    categories = db.query(Category).filter(Category.tenant_id == tenant_id).all()
    cat_name_map = {c.id: c.name for c in categories}

    budget_results = []
    total_allocated = 0.0
    total_spent_budgeted = 0.0

    # Procesar categorías presupuestadas
    for b in budgets:
        total_allocated += b.allocated_amount
        spent = round(cat_spent.get(b.category_id, 0.0), 2)
        total_spent_budgeted += spent

        pct_spent = round((spent / b.allocated_amount) * 100, 1) if b.allocated_amount > 0 else 0.0
        remaining = round(b.allocated_amount - spent, 2)

        # Ritmo de gasto
        daily_cat_rate = spent / days_elapsed if days_elapsed > 0 else 0.0
        projected_finish = round(daily_cat_rate * days_in_month, 2)

        # Semáforo de alerta
        if spent > b.allocated_amount:
            status = "exceeded" # Rojo
            message = f"Excedido por ${round(spent - b.allocated_amount, 2)}"
        elif pct_spent > (pace_pct + 15):
            status = "warning" # Amarillo
            message = "Ritmo acelerado, riesgo de agotar antes de fin de mes"
        else:
            status = "good" # Verde
            message = "En presupuesto"

        budget_results.append({
            "budget_id": b.id,
            "category_id": b.category_id,
            "category_name": cat_name_map.get(b.category_id, "Desconocida"),
            "allocated_amount": round(b.allocated_amount, 2),
            "spent_amount": spent,
            "remaining_amount": remaining,
            "percentage_spent": pct_spent,
            "projected_finish": projected_finish,
            "status": status,
            "message": message
        })

    # Top 5 categorías con más gasto en el mes (incluso sin presupuesto)
    all_cat_ranked = []
    for cid, amt in cat_spent.items():
        all_cat_ranked.append({
            "category_id": cid,
            "category_name": cat_name_map.get(cid, "Sin Categoría") if cid else "Sin Categoría",
            "total": round(amt, 2)
        })
    all_cat_ranked.sort(key=lambda x: x["total"], reverse=True)

    return {
        "month": month,
        "year": year,
        "days_in_month": days_in_month,
        "days_elapsed": days_elapsed,
        "month_progress_pct": round(pace_pct, 1),
        "total_allocated": round(total_allocated, 2),
        "total_spent_budgeted": round(total_spent_budgeted, 2),
        "overall_budget_percentage": round((total_spent_budgeted / total_allocated) * 100, 1) if total_allocated > 0 else 0.0,
        "budgets": budget_results,
        "top_categories": all_cat_ranked[:5]
    }

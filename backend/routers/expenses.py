from datetime import date # Import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import ExpenseCreate, Expense, ExpenseUpdate, PaginatedExpenses # Import PaginatedExpenses
from models.user import User
import crud
from database import get_db
from core.security import get_current_user
from typing import List # Keep List for type hinting if needed elsewhere, though no longer directly used for response_model here

router = APIRouter()

@router.post("/expenses/", response_model=Expense)
def create_expense_for_user(
    expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return crud.create_expense(db=db, expense=expense, user_id=current_user.id, tenant_id=current_user.tenant_id)

@router.get("/expenses/", response_model=PaginatedExpenses) # Change response_model
def read_expenses(
    skip: int = 0,
    limit: int = 100,
    description: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    account_id: int | None = None,
    category_id: int | None = None,
    recipient_id: int | None = None,
    month: int | None = None,
    year: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expenses, total_count = crud.get_expenses_by_tenant(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        description=description,
        start_date=start_date,
        end_date=end_date,
        account_id=account_id,
        category_id=category_id,
        recipient_id=recipient_id,
        month=month,
        year=year,
        status=status
    ) # Unpack tuple
    return {"expenses": expenses, "total_count": total_count} # Return PaginatedExpenses object

@router.get("/expenses/{expense_id}", response_model=Expense)
def read_expense(expense_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_expense = crud.get_expense(db, expense_id=expense_id, tenant_id=current_user.tenant_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.put("/expenses/{expense_id}", response_model=Expense)
def update_expense(
    expense_id: int, expense: ExpenseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    db_expense = crud.update_expense(db, expense_id=expense_id, expense=expense, tenant_id=current_user.tenant_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_expense = crud.delete_expense(db, expense_id=expense_id, tenant_id=current_user.tenant_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"ok": True}

@router.get("/expenses/reports/by-category")
def read_expenses_by_category(
    month: int,
    year: int,
    parent_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_expenses_by_category(db, tenant_id=current_user.tenant_id, month=month, year=year, parent_id=parent_id)

@router.get("/expenses/reports/by-category/export")
def export_expenses_by_category(
    month: int,
    year: int,
    parent_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    # Obtener los mismos datos que el reporte visual
    data = crud.get_expenses_by_category(db, tenant_id=current_user.tenant_id, month=month, year=year, parent_id=parent_id)
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["category_name", "total", "variance_percent"])
    
    # Encabezados amigables
    writer.writerow({"category_name": "Categoria", "total": "Monto Total", "variance_percent": "Variacion %"})
    
    for item in data:
        writer.writerow({
            "category_name": item["category_name"],
            "total": item["total"],
            "variance_percent": f"{item['variance_percent']}%"
        })
    
    output.seek(0)
    filename = f"reporte_categorias_{year}_{month}.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")), # utf-8-sig para que Excel reconozca tildes
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/expenses/reports/income-vs-expenses")
def read_income_expense_balance(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_income_expense_balance(db, tenant_id=current_user.tenant_id, month=month, year=year)

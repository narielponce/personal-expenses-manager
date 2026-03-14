import csv
import io
import zipfile
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from core.security import get_current_user
from models.expense import Expense
from models.category import Category
from models.account import Account
from models.recipient import Recipient
from crud import seed_tenant_categories
from datetime import datetime

router = APIRouter()

def generate_csv(data, fieldnames):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return output.getvalue()

@router.get("/export")
async def export_data(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    tenant_id = current_user.tenant_id
    
    # 1. Obtener datos de todas las tablas filtrados por tenant
    expenses = db.query(Expense).filter(Expense.tenant_id == tenant_id).all()
    categories = db.query(Category).filter(Category.tenant_id == tenant_id).all()
    accounts = db.query(Account).filter(Account.tenant_id == tenant_id).all()
    recipients = db.query(Recipient).filter(Recipient.tenant_id == tenant_id).all()

    # 2. Preparar los archivos CSV en memoria
    
    # Gastos
    expenses_data = [
        {
            "id": e.id,
            "descripcion": e.description,
            "monto": e.amount,
            "fecha_compra": e.date,
            "fecha_aplicacion": e.application_date,
            "tipo": e.movement_type,
            "categoria_id": e.category_id,
            "cuenta_id": e.account_id,
            "destinatario_id": e.recipient_id,
            "es_cuota": e.is_installment,
            "num_cuotas": e.num_installments,
            "monto_cuota": e.installment_amount,
            "estado": e.status
        } for e in expenses
    ]
    expenses_csv = generate_csv(expenses_data, expenses_data[0].keys() if expenses_data else ["id", "descripcion", "monto"])

    # Categorías
    categories_data = [{"id": c.id, "nombre": c.name, "padre_id": c.parent_id} for c in categories]
    categories_csv = generate_csv(categories_data, categories_data[0].keys() if categories_data else ["id", "nombre"])

    # Cuentas
    accounts_data = [{"id": a.id, "nombre": a.name, "es_tarjeta_credito": a.is_credit_card} for a in accounts]
    accounts_csv = generate_csv(accounts_data, accounts_data[0].keys() if accounts_data else ["id", "nombre"])

    # Destinatarios
    recipients_data = [{"id": r.id, "nombre": r.name} for r in recipients]
    recipients_csv = generate_csv(recipients_data, recipients_data[0].keys() if recipients_data else ["id", "nombre"])

    # 3. Crear el archivo ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr("movimientos.csv", expenses_csv)
        zip_file.writestr("categorias.csv", categories_csv)
        zip_file.writestr("cuentas.csv", accounts_csv)
        zip_file.writestr("destinatarios.csv", recipients_csv)

    zip_buffer.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"respaldo_gastos_{timestamp}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/reset")
async def reset_account(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    tenant_id = current_user.tenant_id
    
    try:
        # 1. Borrar en orden para respetar claves foráneas
        db.query(Expense).filter(Expense.tenant_id == tenant_id).delete()
        db.query(Category).filter(Category.tenant_id == tenant_id).delete()
        db.query(Account).filter(Account.tenant_id == tenant_id).delete()
        db.query(Recipient).filter(Recipient.tenant_id == tenant_id).delete()
        
        # 2. Confirmar borrado
        db.commit()
        
        # 3. Volver a sembrar categorías iniciales para que no quede vacía
        seed_tenant_categories(db, tenant_id)
        
        return {"message": "Cuenta reiniciada con éxito"}
    except Exception as e:
        db.rollback()
        print(f"Error resetting account: {e}")
        raise HTTPException(status_code=500, detail="Error al reiniciar la cuenta")

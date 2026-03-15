from sqlalchemy.orm import Session
from models.user import User
from models.tenant import Tenant
from models.expense import Expense
from models.category import Category
from models.account import Account
from models.recipient import Recipient
from schemas import UserCreate, TenantCreate, ExpenseCreate, CategoryCreate, AccountCreate, RecipientCreate, AccountUpdate, CategoryUpdate, RecipientUpdate, ExpenseUpdate
from core.security import get_password_hash
from datetime import date, timedelta
from sqlalchemy import extract, and_

# Lista exhaustiva de categorías predefinidas para nuevos usuarios
DEFAULT_CATEGORIES = [
    {
        "name": "Hogar",
        "sub": ["Alquiler / Hipoteca", "Expensas", "Luz", "Gas", "Agua", "Internet", "Cable / TV", "Reparaciones", "Muebles / Equipamiento"]
    },
    {
        "name": "Alimentación",
        "sub": ["Supermercado", "Verdulería", "Carnicería", "Restaurante", "Delivery", "Café / snacks"]
    },
    {
        "name": "Transporte",
        "sub": ["Combustible", "Transporte público", "Uber / Taxi", "Peajes", "Estacionamiento", "Mantenimiento auto", "Seguro auto"]
    },
    {
        "name": "Salud",
        "sub": ["Farmacia", "Médico", "Estudios", "Odontología", "Obra social / prepaga"]
    },
    {
        "name": "Compras personales",
        "sub": ["Ropa", "Tecnología", "Electrónica", "Regalos", "Belleza / peluquería"]
    },
    {
        "name": "Entretenimiento",
        "sub": ["Salidas", "Cine / teatro", "Streaming", "Videojuegos", "Eventos"]
    },
    {
        "name": "Educación",
        "sub": ["Colegio", "Universidad", "Cursos", "Libros", "Material escolar"]
    },
    {
        "name": "Servicios y suscripciones",
        "sub": ["Netflix", "Spotify", "Apps", "Software", "Cloud / almacenamiento"]
    },
    {
        "name": "Finanzas",
        "sub": ["Impuestos", "Comisiones bancarias", "Intereses", "Seguros", "Gastos administrativos"]
    },
    {
        "name": "Ahorro / Inversión",
        "sub": ["Transferencia a ahorro", "Compra de dólares", "Inversiones", "Criptomonedas", "Plazo fijo"]
    },
    {
        "name": "Ingresos",
        "sub": ["Sueldo", "Freelance", "Ventas", "Intereses", "Otros ingresos"]
    }
]

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_tenant_by_name(db: Session, name: str):
    return db.query(Tenant).filter(Tenant.name == name).first()

def seed_tenant_categories(db: Session, tenant_id: int):
    for cat_data in DEFAULT_CATEGORIES:
        db_parent = Category(name=cat_data["name"], tenant_id=tenant_id, parent_id=None)
        db.add(db_parent)
        db.flush() 
        for sub_name in cat_data["sub"]:
            db_child = Category(name=sub_name, tenant_id=tenant_id, parent_id=db_parent.id)
            db.add(db_child)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding categories: {e}")

def create_tenant(db: Session, tenant: TenantCreate):
    db_tenant = Tenant(name=tenant.name, schema_name=tenant.name.lower().replace(" ", "_"))
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    seed_tenant_categories(db, db_tenant.id)
    return db_tenant

def create_user(db: Session, user: UserCreate):
    db_tenant = get_tenant_by_name(db, name=user.tenant_name)
    if not db_tenant:
        db_tenant = create_tenant(db, TenantCreate(name=user.tenant_name))
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, tenant_id=db_tenant.id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_category(db: Session, category: CategoryCreate, tenant_id: int):
    db_category = Category(name=category.name, tenant_id=tenant_id, parent_id=category.parent_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories_by_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    return db.query(Category).filter(Category.tenant_id == tenant_id).all()

def get_category(db: Session, category_id: int, tenant_id: int):
    return db.query(Category).filter(Category.id == category_id, Category.tenant_id == tenant_id).first()

def update_category(db: Session, category_id: int, category: CategoryUpdate, tenant_id: int):
    db_category = db.query(Category).filter(Category.id == category_id, Category.tenant_id == tenant_id).first()
    if db_category:
        for key, value in category.model_dump(exclude_unset=True).items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int, tenant_id: int):
    db_category = db.query(Category).filter(Category.id == category_id, Category.tenant_id == tenant_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

def create_account(db: Session, account: AccountCreate, tenant_id: int):
    db_account = Account(**account.model_dump(), tenant_id=tenant_id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts_by_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    return db.query(Account).filter(Account.tenant_id == tenant_id).offset(skip).limit(limit).all()

def get_account(db: Session, account_id: int, tenant_id: int):
    return db.query(Account).filter(Account.id == account_id, Account.tenant_id == tenant_id).first()

def update_account(db: Session, account_id: int, account: AccountCreate, tenant_id: int):
    db_account = db.query(Account).filter(Account.id == account_id, Account.tenant_id == tenant_id).first()
    if db_account:
        for key, value in account.model_dump(exclude_unset=True).items():
            setattr(db_account, key, value)
        db.commit()
        db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: int, tenant_id: int):
    db_account = db.query(Account).filter(Account.id == account_id, Account.tenant_id == tenant_id).first()
    if db_account:
        db.delete(db_account)
        db.commit()
    return db_account

def create_recipient(db: Session, recipient: RecipientCreate, tenant_id: int):
    db_recipient = Recipient(**recipient.model_dump(), tenant_id=tenant_id)
    db.add(db_recipient)
    db.commit()
    db.refresh(db_recipient)
    return db_recipient

def get_recipients_by_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    return db.query(Recipient).filter(Recipient.tenant_id == tenant_id).offset(skip).limit(limit).all()

def get_recipient(db: Session, recipient_id: int, tenant_id: int):
    return db.query(Recipient).filter(Recipient.id == recipient_id, Recipient.tenant_id == tenant_id).first()

def update_recipient(db: Session, recipient_id: int, recipient: RecipientCreate, tenant_id: int):
    db_recipient = db.query(Recipient).filter(Recipient.id == recipient_id, Recipient.tenant_id == tenant_id).first()
    if db_recipient:
        for key, value in recipient.model_dump(exclude_unset=True).items():
            setattr(db_recipient, key, value)
        db.commit()
        db.refresh(db_recipient)
    return db_recipient

def delete_recipient(db: Session, recipient_id: int, tenant_id: int):
    db_recipient = db.query(Recipient).filter(Recipient.id == recipient_id, Recipient.tenant_id == tenant_id).first()
    if db_recipient:
        db.delete(db_recipient)
        db.commit()
    return db_recipient

def create_expense(db: Session, expense: ExpenseCreate, user_id: int, tenant_id: int):
    expenses_to_create = []
    initial_application_date = expense.date
    if expense.account_id:
        account = db.query(Account).filter(Account.id == expense.account_id, Account.tenant_id == tenant_id).first()
        if account and account.is_credit_card:
            purchase_date = expense.date
            year = purchase_date.year
            month = purchase_date.month + 1
            if month > 12:
                month = 1
                year += 1
            initial_application_date = date(year, month, 10)

    if expense.is_installment and expense.num_installments and expense.num_installments > 0:
        installment_amount_per_month = round(expense.amount / expense.num_installments, 2)
        for i in range(expense.num_installments):
            current_application_date = initial_application_date
            if i > 0:
                year = initial_application_date.year + (initial_application_date.month + i - 1) // 12
                month = (initial_application_date.month + i - 1) % 12 + 1
                day = initial_application_date.day
                try:
                    current_application_date = date(year, month, day)
                except ValueError:
                    temp_date = date(year, month + 1 if month < 12 else 1, 1) - timedelta(days=1)
                    current_application_date = date(year, month, temp_date.day)
            expenses_to_create.append(
                Expense(
                    description=f"{expense.description} (Cuota {i+1}/{expense.num_installments})",
                    amount=installment_amount_per_month,
                    date=expense.date,
                    application_date=current_application_date,
                    movement_type=expense.movement_type,
                    category_id=expense.category_id,
                    account_id=expense.account_id,
                    recipient_id=expense.recipient_id,
                    is_installment=True,
                    num_installments=expense.num_installments,
                    installment_amount=installment_amount_per_month,
                    status=expense.status or "completed",
                    user_id=user_id,
                    tenant_id=tenant_id
                )
            )
    else:
        expenses_to_create.append(
            Expense(
                description=expense.description,
                amount=expense.amount,
                date=expense.date,
                application_date=initial_application_date,
                movement_type=expense.movement_type,
                category_id=expense.category_id,
                account_id=expense.account_id,
                recipient_id=expense.recipient_id,
                is_installment=False,
                num_installments=None,
                installment_amount=None,
                status=expense.status or "completed",
                user_id=user_id,
                tenant_id=tenant_id
            )
        )
    db.add_all(expenses_to_create)
    db.commit()
    for exp in expenses_to_create:
        db.refresh(exp)
    return expenses_to_create[0]

def get_expenses_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    query = db.query(Expense).filter(Expense.user_id == user_id)
    total_count = query.count()
    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).offset(skip).limit(limit).all()
    return expenses, total_count

def get_income_expense_balance(db: Session, tenant_id: int, month: int, year: int):
    # Obtenemos todos los movimientos completados del mes
    expenses = db.query(Expense).filter(
        Expense.tenant_id == tenant_id,
        Expense.status == "completed",
        extract('month', Expense.application_date) == month,
        extract('year', Expense.application_date) == year
    ).all()

    total_income = sum(e.amount for e in expenses if e.movement_type == "income")
    total_expense = sum(e.amount for e in expenses if e.movement_type == "expense")

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(total_income - total_expense, 2)
    }

def get_expense(db: Session, expense_id: int, tenant_id: int):
    return db.query(Expense).filter(Expense.id == expense_id, Expense.tenant_id == tenant_id).first()

def update_expense(db: Session, expense_id: int, expense: ExpenseUpdate, tenant_id: int):
    db_expense = db.query(Expense).filter(Expense.id == expense_id, Expense.tenant_id == tenant_id).first()
    if not db_expense:
        return None

    # Guardamos el estado anterior para detectar cambios críticos
    was_installment = db_expense.is_installment
    
    # Actualizamos los campos básicos
    for key, value in expense.model_dump(exclude_unset=True).items():
        if key in ["installment_amount"]: continue
        setattr(db_expense, key, value)
    
    # Lógica de Cuotas
    if db_expense.is_installment and db_expense.num_installments and db_expense.num_installments > 1:
        # Recalcular monto de cuota
        db_expense.installment_amount = round(db_expense.amount / db_expense.num_installments, 2)
        
        # CASO ESPECIAL: Si antes NO era cuota y ahora SÍ es (Conversión desde Inbox)
        if not was_installment:
            # 1. Ajustar el registro actual como la "Cuota 1"
            db_expense.description = f"{db_expense.description} (Cuota 1/{db_expense.num_installments})"
            db_expense.amount = db_expense.installment_amount
            
            # 2. Calcular la fecha de aplicación inicial (reutilizando lógica de create_expense)
            initial_app_date = db_expense.application_date
            # Si el usuario cambió la cuenta a una de crédito en esta misma edición
            if db_expense.account_id:
                account = db.query(Account).filter(Account.id == db_expense.account_id, Account.tenant_id == tenant_id).first()
                if account and account.is_credit_card:
                    # Forzamos la lógica de tarjeta si no se había aplicado
                    purchase_date = db_expense.date
                    year = purchase_date.year
                    month = purchase_date.month + 1
                    if month > 12:
                        month = 1
                        year += 1
                    initial_app_date = date(year, month, 10)
                    db_expense.application_date = initial_app_date

            # 3. Crear las cuotas restantes (2 a N)
            for i in range(1, db_expense.num_installments):
                year = initial_app_date.year + (initial_app_date.month + i - 1) // 12
                month = (initial_app_date.month + i - 1) % 12 + 1
                day = initial_app_date.day
                try:
                    current_app_date = date(year, month, day)
                except ValueError:
                    temp_date = date(year, month + 1 if month < 12 else 1, 1) - timedelta(days=1)
                    current_app_date = date(year, month, temp_date.day)

                new_installment = Expense(
                    description=f"{expense.description or db_expense.description.split(' (Cuota')[0]} (Cuota {i+1}/{db_expense.num_installments})",
                    amount=db_expense.installment_amount,
                    date=db_expense.date,
                    application_date=current_app_date,
                    movement_type=db_expense.movement_type,
                    category_id=db_expense.category_id,
                    account_id=db_expense.account_id,
                    recipient_id=db_expense.recipient_id,
                    is_installment=True,
                    num_installments=db_expense.num_installments,
                    installment_amount=db_expense.installment_amount,
                    status=db_expense.status, # Hereda el estado (probablemente 'completed' si viene del form)
                    user_id=db_expense.user_id,
                    tenant_id=tenant_id
                )
                db.add(new_installment)
    else:
        db_expense.installment_amount = None

    db.commit()
    db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int, tenant_id: int):
    db_expense = db.query(Expense).filter(Expense.id == expense_id, Expense.tenant_id == tenant_id).first()
    if db_expense:
        db.delete(db_expense)
        db.commit()
    return db_expense

def get_expenses_by_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 100, **filters):
    query = db.query(Expense).filter(Expense.tenant_id == tenant_id)
    if filters.get("description"): query = query.filter(Expense.description.ilike(f"%{filters['description']}%"))
    if filters.get("status"): query = query.filter(Expense.status == filters["status"])
    if filters.get("month"): query = query.filter(extract('month', Expense.application_date) == filters["month"])
    if filters.get("year"): query = query.filter(extract('year', Expense.application_date) == filters["year"])
    total_count = query.count()
    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).offset(skip).limit(limit).all()
    return expenses, total_count

def get_expenses_by_category(db: Session, tenant_id: int, month: int, year: int, parent_id: int | None = None):
    # 1. Calcular mes anterior para comparativa
    prev_month, prev_year = (12, year - 1) if month == 1 else (month - 1, year)

    # 2. Obtener TODAS las categorías del tenant para manejar jerarquía
    all_cats = db.query(Category).filter(Category.tenant_id == tenant_id).all()
    
    # Mapa de hijos para navegación rápida
    children_map = {}
    for c in all_cats:
        children_map.setdefault(c.parent_id, []).append(c)

    # 3. Función para obtener todos los descendientes de una categoría (incluyéndose a sí misma)
    def get_descendant_ids(cat_id):
        ids = {cat_id}
        for child in children_map.get(cat_id, []):
            ids.update(get_descendant_ids(child.id))
        return ids

    # 4. Obtener todos los gastos de ambos meses (completados y de tipo gasto)
    def get_month_expenses(m, y):
        return db.query(Expense).filter(
            Expense.tenant_id == tenant_id,
            Expense.movement_type == "expense",
            Expense.status == "completed",
            extract('month', Expense.application_date) == m,
            extract('year', Expense.application_date) == y
        ).all()

    current_expenses = get_month_expenses(month, year)
    prev_expenses = get_month_expenses(prev_month, prev_year)

    # 5. Definir qué categorías mostrar en este nivel
    target_cats = children_map.get(parent_id, [])
    
    report_data = []
    for cat in target_cats:
        # Sumamos recursivamente los gastos de esta categoría y todas sus subcategorías
        relevant_ids = get_descendant_ids(cat.id)
        
        curr_total = sum(e.amount for e in current_expenses if e.category_id in relevant_ids)
        prev_total = sum(e.amount for e in prev_expenses if e.category_id in relevant_ids)
        
        diff_percent = 0
        if prev_total > 0:
            diff_percent = ((curr_total - prev_total) / prev_total) * 100
        elif curr_total > 0:
            diff_percent = 100

        if curr_total > 0 or prev_total > 0:
            report_data.append({
                "category_id": cat.id,
                "category_name": cat.name,
                "total": round(curr_total, 2),
                "variance_percent": round(diff_percent, 1),
                "has_children": len(children_map.get(cat.id, [])) > 0
            })

    # Caso especial: Sin Categoría (solo se muestra en el nivel raíz)
    if parent_id is None:
        curr_none = sum(e.amount for e in current_expenses if e.category_id is None)
        prev_none = sum(e.amount for e in prev_expenses if e.category_id is None)
        if curr_none > 0 or prev_none > 0:
            diff_none = ((curr_none - prev_none) / prev_none * 100) if prev_none > 0 else (100 if curr_none > 0 else 0)
            report_data.append({
                "category_id": 0,
                "category_name": "Sin Categoría",
                "total": round(curr_none, 2),
                "variance_percent": round(diff_none, 1),
                "has_children": False
            })

    return sorted(report_data, key=lambda x: x["total"], reverse=True)

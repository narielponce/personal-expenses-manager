from sqlalchemy.orm import Session
from models.user import User
from models.tenant import Tenant
from models.expense import Expense
from models.category import Category
from models.account import Account
from models.recipient import Recipient
from schemas import UserCreate, TenantCreate, ExpenseCreate, CategoryCreate, AccountCreate, RecipientCreate, AccountUpdate, CategoryUpdate, RecipientUpdate, ExpenseUpdate
from core.security import get_password_hash
from datetime import date, timedelta # Import timedelta
from sqlalchemy import extract, and_ # Import extract, and_

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_tenant_by_name(db: Session, name: str):
    return db.query(Tenant).filter(Tenant.name == name).first()

def create_tenant(db: Session, tenant: TenantCreate):
    db_tenant = Tenant(name=tenant.name, schema_name=tenant.name.lower().replace(" ", "_"))
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

def create_user(db: Session, user: UserCreate):
    # Check if tenant exists, if not create it
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
    # Modified to include parent_id
    db_category = Category(
        name=category.name,
        tenant_id=tenant_id,
        parent_id=category.parent_id # Include parent_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories_by_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    return db.query(Category).filter(Category.tenant_id == tenant_id).offset(skip).limit(limit).all()

def get_category(db: Session, category_id: int, tenant_id: int):
    return db.query(Category).filter(Category.id == category_id, Category.tenant_id == tenant_id).first()

def update_category(db: Session, category_id: int, category: CategoryUpdate, tenant_id: int): # Changed schema to CategoryUpdate
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

    # Determine initial application date based on account type
    initial_application_date = expense.date
    if expense.account_id:
        account = db.query(Account).filter(Account.id == expense.account_id, Account.tenant_id == tenant_id).first()
        if account and account.is_credit_card:
            # If it's a credit card, the first application date is the 10th of the next month
            purchase_date = expense.date
            # Calculate next month
            year = purchase_date.year
            month = purchase_date.month + 1
            if month > 12:
                month = 1
                year += 1
            
            # Set the day to 10
            initial_application_date = date(year, month, 10)

    # Calculate installment amount if it's an installment
    if expense.is_installment and expense.num_installments and expense.num_installments > 0:
        installment_amount_per_month = round(expense.amount / expense.num_installments, 2)
        
        for i in range(expense.num_installments):
            # Calculate application_date for each installment
            current_application_date = initial_application_date
            # For subsequent installments, add months to the initial_application_date
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
                    date=expense.date, # Original purchase date remains the same for all installments
                    application_date=current_application_date,
                    movement_type=expense.movement_type,
                    category_id=expense.category_id,
                    account_id=expense.account_id,
                    recipient_id=expense.recipient_id,
                    is_installment=True,
                    num_installments=expense.num_installments,
                    installment_amount=installment_amount_per_month,
                    user_id=user_id,
                    tenant_id=tenant_id
                )
            )
    else:
        # Not an installment or num_installments is 0/None
        expenses_to_create.append(
            Expense(
                description=expense.description,
                amount=expense.amount,
                date=expense.date,
                application_date=initial_application_date, # Use initial_application_date here
                movement_type=expense.movement_type,
                category_id=expense.category_id,
                account_id=expense.account_id,
                recipient_id=expense.recipient_id,
                is_installment=False,
                num_installments=None,
                installment_amount=None,
                user_id=user_id,
                tenant_id=tenant_id
            )
        )
    
    db.add_all(expenses_to_create)
    db.commit()
    for exp in expenses_to_create:
        db.refresh(exp)
    return expenses_to_create[0] # Return the first created expense

def get_expenses_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    query = db.query(Expense).filter(Expense.user_id == user_id)
    total_count = query.count()
    expenses = query.offset(skip).limit(limit).all()
    return expenses, total_count

def get_expense(db: Session, expense_id: int, tenant_id: int):
    return db.query(Expense).filter(Expense.id == expense_id, Expense.tenant_id == tenant_id).first()

def update_expense(db: Session, expense_id: int, expense: ExpenseUpdate, tenant_id: int):
    db_expense = db.query(Expense).filter(Expense.id == expense_id, Expense.tenant_id == tenant_id).first()
    if db_expense:
        # Update fields that are provided
        for key, value in expense.model_dump(exclude_unset=True).items():
            if key in ["installment_amount"]: # installment_amount is a derived field, not directly updated
                continue
            setattr(db_expense, key, value)
        
        # Recalculate installment_amount if num_installments or amount changed and it's an installment
        if db_expense.is_installment and db_expense.num_installments and db_expense.num_installments > 0:
            if expense.amount is not None or expense.num_installments is not None:
                db_expense.installment_amount = round(db_expense.amount / db_expense.num_installments, 2)
        else:
            db_expense.installment_amount = None # Not an installment

        db.commit()
        db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int, tenant_id: int):
    db_expense = db.query(Expense).filter(Expense.id == expense_id, Expense.tenant_id == tenant_id).first()
    if db_expense:
        db.delete(db_expense)
        db.commit()
    return db_expense

def get_expenses_by_tenant(
    db: Session,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    description: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    account_id: int | None = None,
    category_id: int | None = None,
    recipient_id: int | None = None,
    month: int | None = None,
    year: int | None = None
):
    query = db.query(Expense).filter(Expense.tenant_id == tenant_id)

    if description:
        query = query.filter(Expense.description.ilike(f"%{description}%"))

    if start_date:
        query = query.filter(Expense.application_date >= start_date)
    if end_date:
        query = query.filter(Expense.application_date <= end_date)

    if account_id:
        query = query.filter(Expense.account_id == account_id)
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    if recipient_id:
        query = query.filter(Expense.recipient_id == recipient_id)

    if not (start_date or end_date):
        if month:
            query = query.filter(extract('month', Expense.application_date) == month)
        if year:
            query = query.filter(extract('year', Expense.application_date) == year)

    total_count = query.count()
    expenses = query.offset(skip).limit(limit).all()
    return expenses, total_count

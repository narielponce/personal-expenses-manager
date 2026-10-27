from pydantic import BaseModel
from typing import Optional, List # Import List
import datetime

# Tenant Schemas
class TenantBase(BaseModel):
    name: str

class TenantCreate(TenantBase):
    pass

class Tenant(TenantBase):
    id: int
    schema_name: str

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    tenant_name: str # When creating a new user, we can also create a new tenant

class User(UserBase):
    id: int
    is_active: bool
    tenant_id: int

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    email: Optional[str] = None

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None
    parent_id: Optional[int] = None

# Account Schemas
class AccountBase(BaseModel):
    name: str
    is_credit_card: Optional[bool] = False
    initial_balance: Optional[float] = 0.0

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    is_credit_card: Optional[bool] = None
    initial_balance: Optional[float] = None

class AccountWithBalance(Account):
    current_balance: float = 0.0
    total_incomes: float = 0.0
    total_expenses: float = 0.0
    total_transfers_in: float = 0.0
    total_transfers_out: float = 0.0
    is_overdrawn: bool = False

class AccountBalanceSummary(BaseModel):
    accounts: List[AccountWithBalance]
    total_available_liquidity: float = 0.0
    total_credit_debt: float = 0.0


# Recipient Schemas
class RecipientBase(BaseModel):
    name: str

class RecipientCreate(RecipientBase):
    pass

class Recipient(RecipientBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True

class RecipientUpdate(RecipientBase):
    name: Optional[str] = None

# Expense Schemas
class ExpenseBase(BaseModel):
    description: str
    amount: float
    date: datetime.date
    application_date: datetime.date
    movement_type: str
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    recipient_id: Optional[int] = None
    is_installment: Optional[bool] = False
    num_installments: Optional[int] = None
    status: Optional[str] = "completed"
    is_recurring: Optional[bool] = False
    payment_method: Optional[str] = None
    installments: Optional[int] = 1
    destination_account_id: Optional[int] = None


class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    user_id: int
    tenant_id: int
    installment_amount: Optional[float] = None

    class Config:
        from_attributes = True

class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    date: datetime.date | None = None
    application_date: datetime.date | None = None
    movement_type: Optional[str] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    destination_account_id: Optional[int] = None
    recipient_id: Optional[int] = None
    is_installment: Optional[bool] = None
    num_installments: Optional[int] = None
    status: Optional[str] = None
    is_recurring: Optional[bool] = None
    payment_method: Optional[str] = None
    installments: Optional[int] = None

# Paginated Expense Schemas
class PaginatedExpenses(BaseModel):
    expenses: List[Expense]
    total_count: int

# Budget Schemas
class BudgetBase(BaseModel):
    category_id: int
    month: int
    year: int
    allocated_amount: float

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    allocated_amount: Optional[float] = None
    month: Optional[int] = None
    year: Optional[int] = None
    category_id: Optional[int] = None

class Budget(BudgetBase):
    id: int
    user_id: int
    tenant_id: int
    created_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class BudgetResponse(Budget):
    category_name: Optional[str] = None
    spent_amount: Optional[float] = 0.0
    percentage_spent: Optional[float] = 0.0


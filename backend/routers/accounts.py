from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas import AccountCreate, Account as AccountSchema, AccountUpdate
from models.user import User
from models.account import Account # Import SQLAlchemy model
import crud
from database import get_db
from core.security import get_current_user

router = APIRouter()

@router.post("/accounts/", response_model=AccountSchema)
def create_account_for_user(
    account: AccountCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # Check if account with the same name already exists for this tenant
    db_account = db.query(Account).filter(
        Account.tenant_id == current_user.tenant_id,
        Account.name == account.name
    ).first()
    if db_account:
        raise HTTPException(status_code=400, detail="Account with this name already exists for your tenant")

    return crud.create_account(db=db, account=account, tenant_id=current_user.tenant_id)

@router.get("/accounts/", response_model=List[AccountSchema])
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    accounts = crud.get_accounts_by_tenant(db, tenant_id=current_user.tenant_id, skip=skip, limit=limit)
    return accounts

@router.get("/accounts/{account_id}", response_model=AccountSchema)
def read_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_account = crud.get_account(db, account_id=account_id, tenant_id=current_user.tenant_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.put("/accounts/{account_id}", response_model=AccountSchema)
def update_account(
    account_id: int, account: AccountCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    db_account = crud.update_account(db, account_id=account_id, account=account, tenant_id=current_user.tenant_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_account = crud.delete_account(db, account_id=account_id, tenant_id=current_user.tenant_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"ok": True}

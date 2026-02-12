from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas import RecipientCreate, Recipient as RecipientSchema, RecipientUpdate
from models.user import User
from models.recipient import Recipient # Import SQLAlchemy model
import crud
from database import get_db
from core.security import get_current_user

router = APIRouter()

@router.post("/recipients/", response_model=RecipientSchema)
def create_recipient_for_user(
    recipient: RecipientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # Check if recipient with the same name already exists for this tenant
    db_recipient = db.query(Recipient).filter(
        Recipient.tenant_id == current_user.tenant_id,
        Recipient.name == recipient.name
    ).first()
    if db_recipient:
        raise HTTPException(status_code=400, detail="Recipient with this name already exists for your tenant")

    return crud.create_recipient(db=db, recipient=recipient, tenant_id=current_user.tenant_id)

@router.get("/recipients/", response_model=List[RecipientSchema])
def read_recipients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipients = crud.get_recipients_by_tenant(db, tenant_id=current_user.tenant_id, skip=skip, limit=limit)
    return recipients

@router.get("/recipients/{recipient_id}", response_model=RecipientSchema)
def read_recipient(recipient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_recipient = crud.get_recipient(db, recipient_id=recipient_id, tenant_id=current_user.tenant_id)
    if db_recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return db_recipient

@router.put("/recipients/{recipient_id}", response_model=RecipientSchema)
def update_recipient(
    recipient_id: int, recipient: RecipientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    db_recipient = crud.update_recipient(db, recipient_id=recipient_id, recipient=recipient, tenant_id=current_user.tenant_id)
    if db_recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return db_recipient

@router.delete("/recipients/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipient(recipient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_recipient = crud.delete_recipient(db, recipient_id=recipient_id, tenant_id=current_user.tenant_id)
    if db_recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return {"ok": True}

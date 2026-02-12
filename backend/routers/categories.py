from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas import CategoryCreate, Category as CategorySchema, CategoryUpdate
from models.user import User
from models.category import Category
import crud
from database import get_db
from core.security import get_current_user

router = APIRouter()

@router.post("/categories/", response_model=CategorySchema)
def create_category_for_user(
    category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # Check if category with the same name already exists for this tenant
    db_category = db.query(Category).filter(
        Category.tenant_id == current_user.tenant_id,
        Category.name == category.name
    ).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category with this name already exists for your tenant")

    return crud.create_category(db=db, category=category, tenant_id=current_user.tenant_id)

@router.get("/categories/", response_model=List[CategorySchema])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = crud.get_categories_by_tenant(db, tenant_id=current_user.tenant_id, skip=skip, limit=limit)
    return categories

@router.get("/categories/{category_id}", response_model=CategorySchema)
def read_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_category = crud.get_category(db, category_id=category_id, tenant_id=current_user.tenant_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.put("/categories/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: int, category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    db_category = crud.update_category(db, category_id=category_id, category=category, tenant_id=current_user.tenant_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_category = crud.delete_category(db, category_id=category_id, tenant_id=current_user.tenant_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"ok": True}

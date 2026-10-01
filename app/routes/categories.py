from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from app import models,schemas
from app.database import get_db
from app.dependencies import get_current_admin


router = APIRouter(prefix="/categories",tags=["categories"])


@router.get("/",response_model=List[schemas.CategoryResponse])
def get_all_category(db:Session=Depends(get_db)):
    categories = db.query(models.Category).order_by(models.Category.name).all()
    return categories


@router.post("/",response_model=schemas.CategoryResponse,status_code=status.HTTP_201_CREATED)
def create_post(category:schemas.CategoryCreate,db:Session=Depends(get_db),admin:models.User=Depends(get_current_admin)):
    name = category.name.strip()

    existing_name = db.query(models.Category).filter(models.Category.name == name).first()

    if existing_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Category already exist.")


    new_category = models.Category(name=name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category



@router.put("/{category_id}",response_model=schemas.CategoryResponse)
def update_category(category_id:int,category:schemas.CategoryCreate,db:Session=Depends(get_db),admin:models.User=Depends(get_current_admin)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()

    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found.")

    name = category.name.strip()

    duplicate = db.query(models.Category).filter(
        models.Category.name == name,
        models.Category.id != category_id
    ).first()

    if duplicate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Category already exist.")

    db_category.name = name
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id:int,db:Session=Depends(get_db),admin:models.User=Depends(get_current_admin)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()

    if not category_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Catgory not found.")

    if category.products:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Cannot delete a category that still has products")

    db.delete(category)
    db.commit()
    return None
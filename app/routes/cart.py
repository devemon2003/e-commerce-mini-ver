from fastapi import APIRouter,HTTPException,status,Depends
from sqlalchemy.orm import Session,joinedload
from typing import List

from app import models,schemas
from app.database import get_db
from app.dependencies import get_current_user
from app.routes.product import get_active_product_or_404


router = APIRouter(prefix="/cart",tags=["carts"])


@router.get("/",response_model=schemas.CartSummaryResponse)
def get_cart_items(db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    items = db.query(models.CartItem).options(joinedload(models.CartItem.product).joinedload(models.Product.category)).filter(models.CartItem.user_id == current_user.id).all()

    total_price = sum(item.product.price * item.quantity for item in items)
    return schemas.CartSummaryResponse(items=items,total_price=total_price)


@router.post("/",response_model=schemas.CartItemResponse)
def add_to_cart(item:schemas.CartItemCreate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    product = get_active_product_or_404(db,item.product_id)

    if item.quantity < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Quantity must be at least 1")

    if item.quantity > product.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Not enough stock available")


    existing = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id,models.CartItem.product_id == product.id).first()

    if existing:
        new_quantity = existing.quantity + item.quantity
        if new_quantity > product.stock:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Not enough stock available")
        existing.quantity = new_quantity
        db.commit()
        db.refresh(existing)
        return existing

    new_item = models.CartItem(user_id=current_user.id,product_id=item.product_id,quantity=item.quantity)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.patch("/{cart_item_id}",response_model=schemas.CartItemResponse)
def update_cart_item(cart_item_id:int,update:schemas.CartItemUpdate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id,models.User.id == current_user.id).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Cart not found.")

    if update.quantity < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Quantity must be at least 1")

    if update.quantity > item.product.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Not enough stock available")

    item.quantity = update.quantity
    db.commit()
    db.refresh(item)
    return(item)


@router.delete("/{cart_item_id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(cart_item_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id,models.CartItem.user_id == current_user.id).first()

    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    return None
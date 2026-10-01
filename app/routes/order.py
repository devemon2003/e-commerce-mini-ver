from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session,joinedload
from typing import List

from app import models,schemas,stripe_config
from app.dependencies import get_current_user
from app.database import get_db

import stripe


router = APIRouter(prefix="/orders",tags=["orders"])


@router.post("/",response_model=schemas.OrderResponse,status_code=status.HTTP_201_CREATED)
def checkout(db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    cart_item = db.query(models.CartItem).options(joinedload(models.CartItem.product)).filter(models.CartItem.user_id == current_user.id).all()

    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Cart is empty.")

    for item in cart_item:
        if not item.product.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{item.product.name} is no longer available.")

        if item.quantity > item.product.stock:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Not enough stock for '{item.product.name}'")

    try:
        total_price = sum(item.product.price * item.quantity for item in cart_item)

        new_order = models.Order(user_id=current_user.id,total_price=total_price)
        db.add(new_order)
        db.flush()

        for item in cart_item:
            new_order_item = models.OrderItem(
                order_id = new_order.id,
                product_id = item.product_id,
                quantity = item.quantity,
                price_at_purchase = item.product.price
            )

            db.add(new_order_item)

            item.product.stock -= item.quantity

            db.delete(item)

        db.commit()
        db.refresh(new_order)
        return new_order

    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Checkout failed, nothing was charged")


@router.get("/",response_model=List[schemas.OrderResponse])
def get_my_orders(db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    orders = db.query(models.Order).options(joinedload(models.Order.items).joinedload(models.OrderItem.product)).filter(models.Order.user_id == current_user.id).order_by(models.Order.created_at.desc()).all()
    return orders


@router.get("/{order_id}",response_model=schemas.OrderResponse)
def get_single_order(order_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    order = db.query(models.Order).options(joinedload(models.Order.items).joinedload(models.OrderItem.product)).filter(models.Order.id == order_id,models.Order.user_id == current_user.id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found.")

    return order


@router.post("/{order_id}/pay",response_model=schemas.PaymentIntentResponse)
def create_payment(order_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id,models.Order.user_id == current_user.id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="order not found.")

    if order.status != schemas.OrderStatus.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="This order is not payable.")

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_price * 100),
            currency="usd",
            metadata={"order_id":str(order.id),"user_id":str(current_user.id)}
        )

    except stripe.error.StripeError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,detail="Payment service unavailable")

    order.stripe_payment_intent = intent.id
    db.commit()

    return schemas.PaymentIntentResponse(
        client_secret=intent.client_secret,
        order_id=order.id,
        amount=order.total_price
    )
        
@router.post("/{order_id}/confirm-payment", response_model=schemas.OrderResponse)
def confirm_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id,
    ).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if not order.stripe_payment_intent:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No payment started for this order")

    try:
        intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent)
    except stripe.error.StripeError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Payment service unavailable")

    if intent.status != "succeeded":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Payment not completed (status: {intent.status})")

    order.status = models.OrderStatus.paid
    db.commit()
    db.refresh(order)
    return order
    
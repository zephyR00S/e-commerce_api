from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, crud
from auth import get_current_user
from schemas import OrderSchema

router = APIRouter(prefix="/orders", tags=["Orders"])


# Create order from cart
@router.post("/", response_model=OrderSchema)
def create_order(db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = crud.create_order_from_cart(db, user["id"])
    if not order:
        raise HTTPException(400, "Cart is empty")
    return order


# List user orders
@router.get("/", response_model=list[OrderSchema])
def list_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == user["id"]).all()


# Get single order
@router.get("/{order_id}", response_model=OrderSchema)
def get_order(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user["id"]
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    return order

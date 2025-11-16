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
    order = crud.create_order_from_cart(db, user.id)
    if not order:
        raise HTTPException(400, "Cart is empty")
    return order


# List user orders
@router.get("/", response_model=list[OrderSchema])
def list_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == user.id).all()


# Get single order
@router.get("/{order_id}", response_model=OrderSchema)
def get_order(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    return order

# -------------------------
# ADMIN: Update Order Status
# -------------------------
@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    allowed_status = ["Pending", "Paid", "Shipped", "Delivered", "Cancelled"]

    if status not in allowed_status:
        raise HTTPException(400, f"Invalid status. Allowed: {allowed_status}")

    # only admin
    if not getattr(user, "is_admin", False):
        raise HTTPException(403, "Only admin can update order status.")

    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    order.status = status
    db.commit()
    db.refresh(order)

    return {"message": "Order status updated", "order": order}


# -------------------------
# PAY FOR ORDER (simulate)
# -------------------------
@router.post("/{order_id}/pay")
def pay_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user.id

    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.status != "Pending":
        raise HTTPException(400, f"Order already {order.status}, cannot pay.")

    # simulate payment success
    order.status = "Paid"
    db.commit()
    db.refresh(order)

    return {
        "message": "Payment successful",
        "order_id": order.id,
        "status": order.status,
        "amount_charged": order.total_amount
    }

# orders.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import crud
from auth import get_current_user
from schemas import OrderSchema
from database import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])

# -----------------------------------------------------
#  Create order from cart
# -----------------------------------------------------
@router.post("/", response_model=OrderSchema)
def create_order(db: Session = Depends(get_db), user=Depends(get_current_user)):
    
    order = crud.create_order_from_cart(db, user.id)
    if not order:
        raise HTTPException(400, "Cart is empty")
    return order


# -----------------------------------------------------
#  List user's orders
# -----------------------------------------------------
@router.get("/", response_model=list[OrderSchema])
def list_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == user.id).all()


# -----------------------------------------------------
#  Get single order
# -----------------------------------------------------
@router.get("/{order_id}", response_model=OrderSchema)
def get_order(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    return order


# -----------------------------------------------------
#  Admin: Update order status
# -----------------------------------------------------
@router.put("/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db), user=Depends(get_current_user)):

    allowed_status = ["Pending", "Paid", "Packed", "Shipped", "Out for Delivery", "Delivered", "Cancelled", "Returned"]

    if status not in allowed_status:
        raise HTTPException(400, f"Invalid status. Allowed: {allowed_status}")

    if not getattr(user, "is_admin", False):
        raise HTTPException(403, "Admins only")

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    order.status = status
    db.commit()

    # Save to history
    crud.log_status(db, order_id, status)

    db.refresh(order)
    return {"message": "Status updated", "new_status": order.status}

@router.get("/{order_id}/timeline")
def order_timeline(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    timeline = db.query(models.OrderStatusHistory).filter(
        models.OrderStatusHistory.order_id == order_id
    ).order_by(models.OrderStatusHistory.timestamp.asc()).all()

    return [
        {
            "status": entry.status,
            "timestamp": entry.timestamp
        }
        for entry in timeline
    ]



# -----------------------------------------------------
#  MOCK PAYMENT (no real gateway)
# -----------------------------------------------------
@router.post("/{order_id}/pay")
def mock_pay_order(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Simulate a successful payment without any real gateway.
    """

    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.status != "Pending":
        raise HTTPException(400, f"Order is already {order.status}")

    # Simulate successful payment
    order.status = "Paid"
    order.paid_at = datetime.now()

    db.commit()
    crud.log_status(db, order.id, "Paid")
    db.refresh(order)

    return {
        "message": "Mock payment successful",
        "order_id": order.id,
        "amount_charged": order.total_amount,
        "status": order.status,
        "paid_at": order.paid_at
    }


# -----------------------------------------------------
#  MOCK REFUND API
# -----------------------------------------------------
@router.post("/{order_id}/refund")
def mock_refund(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):

    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.status != "Paid":
        raise HTTPException(400, "Only paid orders can be refunded")

    # Simulate refund
    order.status = "Refunded"
    order.refunded_at = datetime.now()

    db.commit()
    db.refresh(order)

    return {
        "message": "Mock refund successful",
        "order_id": order.id,
        "status": order.status,
        "refunded_at": order.refunded_at
    }

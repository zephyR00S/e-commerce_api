from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import auth
from database import get_db
import models
from auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin Tools"])

@router.post("/make-admin/{user_id}")
def make_admin(user_id: int, db: Session = Depends(get_db),
               current_user: models.User = Depends(auth.get_current_user)
               ):
    # Only admins can promote others
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can promote users")
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_admin = True
    db.commit()
    db.refresh(user)

    return {"message": f"User {user.email} is now an admin"}

# 1️⃣ Get all users
@router.get("/users")
def get_all_users(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(models.User).all()


# 2️⃣ Get all orders
@router.get("/orders")
def get_all_orders(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(models.Order).all()


# 3️⃣ Get revenue
@router.get("/revenue")
def get_revenue(db: Session = Depends(get_db), admin=Depends(require_admin)):
    revenue = db.query(models.Order).all()
    total = sum(order.total_amount for order in revenue)
    return {"total_revenue": total}


# 4️⃣ Low stock products
@router.get("/low-stock")
def low_stock(db: Session = Depends(get_db), admin=Depends(require_admin)):
    products = db.query(models.Product).filter(models.Product.stock < 5).all()
    return products


# 5️⃣ Basic sales stats
@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db), admin=Depends(require_admin)):
    total_users = db.query(models.User).count()
    total_orders = db.query(models.Order).count()
    total_products = db.query(models.Product).count()

    revenue = db.query(models.Order).all()
    total_revenue = sum(o.total_amount for o in revenue)

    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_products": total_products,
        "total_revenue": total_revenue,
    }

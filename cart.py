from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
import crud
import models
from schemas import CartItemCreate, CartItemOut

router = APIRouter(prefix="/cart", tags=["Cart"])


# Add to Cart
@router.post("/", response_model=CartItemOut)
def add_item_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    cart_item = crud.add_to_cart(db, user.id, item.product_id, item.quantity)
    return cart_item


# View Cart (with total price)
@router.get("/")
def view_cart(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    items = crud.get_cart_items(db, user.id)

    total = sum(i.product.price * i.quantity for i in items)

    return {
        "items": items,
        "total_price": total
    }

# Update Quantity
@router.put("/{product_id}", response_model=CartItemOut)
def update_cart(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    updated = crud.update_cart_quantity(db, user.id, product_id, quantity)
    if not updated:
        raise HTTPException(404, "Item not found in cart")

    return updated


# Remove from Cart
@router.delete("/{product_id}")
def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    deleted = crud.remove_from_cart(db, user.id, product_id)
    if not deleted:
        raise HTTPException(404, "Item not found")

    return {"message": "Item removed from cart"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import ProductCreate, Product
import crud
from auth import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

# Admin-only creation
@router.post("/", response_model=Product)
def create_product_api(
    product: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.create_product(db, product)

# Public - list
@router.get("/", response_model=list[Product])
def get_products_api(db: Session = Depends(get_db)):
    return crud.get_products(db)

# Public - single product
@router.get("/{product_id}", response_model=Product)
def get_product_api(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product

# Admin-only update
@router.put("/{product_id}", response_model=Product)
def update_product_api(
    product_id: int,
    updated_data: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    product = crud.update_product(db, product_id, updated_data)
    if not product:
        raise HTTPException(404, "Product not found")
    return product

# Admin-only delete
@router.delete("/{product_id}")
def delete_product_api(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    deleted = crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted"}

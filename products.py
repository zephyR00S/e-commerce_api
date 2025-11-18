import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas import ProductCreate, Product
import crud
from auth import get_current_user
import schemas


router = APIRouter(prefix="/products", tags=["Products"])
UPLOAD_DIR = "uploads/products"


# Admin-only creation
@router.post("/", response_model=Product)
def create_product_api(
    product: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.create_product(db, product)


#-----------------------------------------------------------------------------------



# Public - single product
@router.get("/{product_id}", response_model=Product)
def get_product_api(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product

# Filters + Search Route
@router.get("/", response_model=list[schemas.Product])
def list_products(
    skip: int = 0,
    limit: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
    search: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Product)

    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)

    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))

    if is_active is not None:
        query = query.filter(models.Product.is_active == is_active)

    products = query.offset(skip).limit(limit).all()
    return products

#-----------------------------------------------------------------------------------



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

# Active/Inactive Toggle Route
@router.put("/{product_id}/toggle", response_model=schemas.Product)
def toggle_product(product_id: int, db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = not product.is_active
    db.commit()
    db.refresh(product)
    return product






#------------------------------------------------------------------------------------------------



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

#------------------------------------------------------------------------------------------------


@router.post("/{product_id}/upload-image")
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Only admin can upload images
    if not getattr(user, "is_admin", False):
        raise HTTPException(403, "Only admin can upload images")

    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    # Validate file type
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(400, "Invalid file type")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"{product_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Save file
    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())

    # Update product image URL
    product.image_url = f"/static/products/{filename}"
    db.commit()
    db.refresh(product)

    return {"message": "Image uploaded successfully", "url": product.image_url}
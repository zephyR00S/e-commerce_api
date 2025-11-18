import os
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas import ProductCreate, Product
import crud
from auth import get_current_user
import schemas

UPLOAD_FOLDER = "uploads/products"
router = APIRouter(prefix="/products", tags=["Products"])



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

@router.post("/{product_id}/images")
async def upload_images(
    product_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Only admin can upload
    if not user.is_admin:
        raise HTTPException(403, "Only admin can upload product images")

    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        raise HTTPException(404, "Product not found")

    saved_images = []
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    for file in files:
        ext = file.filename.split(".")[-1]
        unique_name = f"{uuid4()}.{ext}"

        file_path = os.path.join(UPLOAD_FOLDER, unique_name)

        # Save file to disk
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Save entry in DB
        image = models.ProductImage(product_id=product_id, 
                        file_path=f"/uploads/products/{unique_name}")
        db.add(image)
        saved_images.append(image)

    db.commit()

    return {
        "message": "Images uploaded successfully",
        "images": [img.file_path for img in saved_images]
    }

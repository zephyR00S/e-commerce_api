# These define request/response models.
from typing import List
from pydantic import BaseModel, EmailStr

# ---------- USER ----------
# UserCreate validates signup payload.
class UserCreate(BaseModel):
    email: str
    password: str
    is_admin: bool = False

# UserOut is what the API returns for user info.
class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: int

    class Config:
        from_attributes = True


# ---------- TOKEN ---------- 
# Token and TokenData are for JWT flows.
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None


# ---------- PRODUCT ----------
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int = 0
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True


# ---------- CART ----------
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    class Config:
        from_attributes = True


# ---------- ORDER ----------

class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderSchema(BaseModel):
    id: int
    total_amount: float
    status: str
    items: List[OrderItemSchema]

    class Config:
        from_attributes = True

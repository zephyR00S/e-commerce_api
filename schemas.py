# These define request/response models.
from pydantic import BaseModel, EmailStr

# ---------- USER ----------
# UserCreate validates signup payload.
class UserCreate(BaseModel):
    email: str
    password: str

# UserOut is what the API returns for user info.
class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: int

    class Config:
        orm_mode = True


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
    price: float
    stock: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        orm_mode = True


# ---------- CART ----------
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItem(BaseModel):
    id: int
    product_id: int
    quantity: int
    class Config:
        orm_mode = True


# ---------- ORDER ----------
class Order(BaseModel):
    id: int
    total_price: float
    class Config:
        orm_mode = True

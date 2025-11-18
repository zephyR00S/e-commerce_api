# These define request/response models.
from typing import List, Optional
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

class ProductImage(BaseModel):
    id: int
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


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
    images: list[ProductImage] = []
    
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

    # Shipping fields ⬇⬇
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    shipping_city: str
    shipping_state: str
    shipping_pincode: str


    items: List[OrderItemSchema]

    class Config:
        from_attributes = True


# ---------- ADDRESS ----------

class AddressBase(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    landmark: str | None = None
    country: str | None = "India"
    is_primary: bool = False

class AddressCreate(AddressBase):
    pass

class AddressOut(AddressBase):
    id: int
    is_primary: bool

    class Config:
        from_attributes = True

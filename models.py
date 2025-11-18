
"""
This defines DB tables: User, Product, CartItem, Order, OrderItem.

"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    is_admin = Column(Boolean, default=False)


    orders = relationship("Order", back_populates="user")
    cart_items = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")



class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    images = relationship("ProductImage", back_populates="product")

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")




class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    total_amount = Column(Float, default=0)
    status = Column(String, default="Pending")  # Pending, Paid, Shipped, Delivered, Cancelled, Refunded

    payment_id = Column(String, nullable=True)   # For future gateways, mock keeps it None
    paid_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now()) 

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))

    quantity = Column(Integer, default=1)
    price = Column(Float)  # price at time of order

    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    file_path = Column(String)  # stored file name / path
    alt_text = Column(String, nullable=True)
    is_primary = Column(Boolean, default=False)

    product = relationship("Product", back_populates="images")
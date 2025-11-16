# crud.py
from sqlalchemy.orm import Session
import models, schemas, auth

# ---------- USER ----------
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not auth.verify_password(password, user.hashed_password):
        return None
    return user


# ---------------- PRODUCT CRUD ---------------- #

def create_product(db: Session, product_data):
    product = models.Product(**product_data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_products(db: Session):
    return db.query(models.Product).all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_product(db: Session, product_id: int, product_data):
    product = get_product(db, product_id)
    if not product:
        return None

    for key, value in product_data.dict().items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    if not product:
        return None

    db.delete(product)
    db.commit()
    return True



# ---------------- CART CRUD ---------------- #

def get_cart_items(db: Session, user_id: int):
    return db.query(models.Cart).filter(models.Cart.user_id == user_id).all()


def get_cart_item(db: Session, user_id: int, product_id: int):
    return db.query(models.Cart).filter(
        models.Cart.user_id == user_id,
        models.Cart.product_id == product_id
    ).first()


def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int):
    item = get_cart_item(db, user_id, product_id)

    if item:
        item.quantity += quantity
    else:
        item = models.Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(item)

    db.commit()
    db.refresh(item)
    return item


def update_cart_quantity(db: Session, user_id: int, product_id: int, quantity: int):
    item = get_cart_item(db, user_id, product_id)
    if not item:
        return None

    item.quantity = quantity
    db.commit()
    return item


def remove_from_cart(db: Session, user_id: int, product_id: int):
    item = get_cart_item(db, user_id, product_id)
    if not item:
        return False

    db.delete(item)
    db.commit()
    return True

#---------------- ORDER CRUD ---------------- #

def create_order_from_cart(db, user_id):
    # fetch user cart
    cart_items = db.query(models.Cart).filter(models.Cart.user_id == user_id).all()

    if not cart_items:
        return None

    # create order
    order = models.Order(user_id=user_id, status="Pending")
    db.add(order)
    db.commit()
    db.refresh(order)

    total = 0

    # create order items
    for item in cart_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()

        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )

        total += product.price * item.quantity
        db.add(order_item)

    # update total
    order.total_amount = total
    db.commit()

    # clear user's cart
    db.query(models.Cart).filter(models.Cart.user_id == user_id).delete()
    db.commit()

    return order

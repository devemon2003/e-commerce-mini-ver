from sqlalchemy import String,Integer,Column,Text,DateTime,ForeignKey,Enum as SQLEnum,Boolean,Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum



class UserRole(str,enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):

    __tablename__="users"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True,index=True,nullable=False)
    hashed_password = Column(String,nullable=False)
    role = Column(SQLEnum(UserRole),default=UserRole.user,nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    cart_items = relationship("CartItem",back_populates="user",cascade="all, delete")
    orders = relationship("Order",back_populates="user",cascade="all, delete")


class Category(Base):

    __tablename__="categories"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,unique=True,index=True,nullable=False)

    products = relationship("Product",back_populates="category")


class Product(Base):

    __tablename__="products"

    id = Column(Integer,primary_key=True,nullable=False)
    name = Column(String,nullable=False,index=True)
    description = Column(Text,nullable=True)
    price = Column(Float,nullable=False)
    stock = Column(Integer,default=0,nullable=False)
    image_url = Column(String,nullable=True)
    image_public_id = Column(String,nullable=True)
    is_active = Column(Boolean,default=True,nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    category_id = Column(Integer,ForeignKey("categories.id"))
    category = relationship("Category",back_populates="products")



class CartItem(Base):

    __tablename__="cart_items"

    id = Column(Integer,primary_key=True,index=True)
    quantity = Column(Integer,default=1,nullable=False)

    user_id = Column(Integer,ForeignKey("users.id"))
    user = relationship("User",back_populates="cart_items")

    product_id = Column(Integer,ForeignKey("products.id"))
    product = relationship("Product")


class OrderStatus(str,enum.Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base):

    __tablename__="orders"

    id = Column(Integer,primary_key=True,index=True)
    total_price = Column(Float,nullable=False)
    status = Column(SQLEnum(OrderStatus),default=OrderStatus.pending,nullable=False)
    stripe_payment_intent = Column(String,nullable=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    user_id = Column(Integer,ForeignKey("users.id"))
    user = relationship("User",back_populates="orders")

    items = relationship("OrderItem",back_populates="order",cascade="all, delete")


class OrderItem(Base):

    __tablename__="order_items"

    id = Column(Integer,primary_key=True,index=True)
    quantity = Column(Integer,nullable=False)
    price_at_purchase = Column(Float,nullable=False)

    order_id = Column(Integer,ForeignKey("orders.id"))
    order = relationship("Order",back_populates="items")

    product_id = Column(Integer,ForeignKey("products.id"))
    product = relationship("Product")
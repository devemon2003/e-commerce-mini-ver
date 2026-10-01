from pydantic import BaseModel,EmailStr,ConfigDict,Field
from typing import Optional,List
from datetime import datetime
from app.models import UserRole,OrderStatus


class UserCreate(BaseModel):
    email : EmailStr
    password : str


class UserResponse(BaseModel):
    id : int
    email : EmailStr
    role : UserRole
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token : str
    token_type : str


class CategoryCreate(BaseModel):
    name : str


class CategoryResponse(BaseModel):
    id : int
    name : str

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name : str
    description : Optional[str] = None
    price : float = Field(gt=0)
    stock : int = Field(default=0,ge=0)
    category_id : int


class ProductUpdate(BaseModel):
    name : Optional[str] = None
    description : Optional[str] = None
    price : Optional[float] = Field(default=None,gt=0)
    stock : Optional[int] = Field(default=None,ge=0)
    category_id : Optional[int] = None


class ProductResponse(BaseModel):
    id : int
    name : str
    description : Optional[str]
    price : float
    stock : int
    image_url : Optional[str]
    created_at : datetime
    category_id : int
    category : CategoryResponse

    model_config = ConfigDict(from_attributes=True)


class CartItemCreate(BaseModel):
    product_id : int
    quantity : int = 1


class CartItemUpdate(BaseModel):
    quantity : int


class CartItemResponse(BaseModel):
    id : int
    quantity : int
    product : ProductResponse

    model_config = ConfigDict(from_attributes=True)


class CartSummaryResponse(BaseModel):
    items : List[CartItemResponse]
    total_price : float


class OrderItemResponse(BaseModel):
    id : int
    quantity : int
    price_at_purchase : float
    product : ProductResponse

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id : int
    total_price : float
    status : OrderStatus
    created_at : datetime
    items : List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class PaymentIntentResponse(BaseModel):
    client_secret : str
    order_id : int
    amount : float
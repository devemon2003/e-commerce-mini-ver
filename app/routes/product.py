import io
from fastapi import APIRouter,Depends,HTTPException,status,Query,UploadFile,File
from sqlalchemy.orm import Session,joinedload
from typing import List,Optional
import cloudinary.uploader
from sqlalchemy import or_

from app.database import get_db
from app.dependencies import get_current_admin
from app import models,schemas,cloudinary_config


router = APIRouter(prefix="/products",tags=["products"])

ALLOWED_IMAGES = ["image/jpeg", "image/png", "image/webp"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def get_active_product_or_404(db:Session,product_id) -> models.Product:
    product = db.query(models.Product).filter(models.Product.id == product_id,models.Product.is_active == True).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found.")

    return product


@router.get("/",response_model=List[schemas.ProductResponse])
def get_all_product(db:Session=Depends(get_db),category_id:Optional[int]=Query(None),search:Optional[str]=Query(None),min_price:Optional[float]=Query(None,ge=0),max_price:Optional[float]=Query(None,ge=0),page:int=Query(1,ge=1),limit:int=Query(10,ge=1,le=100)):
    query = db.query(models.Product).options(joinedload(models.Product.category)).filter(models.Product.is_active == True)

    if category_id:
        query = query.filter(models.Product.category_id == category_id)

    if search:
        query = query.filter(
            or_(
                models.Product.name.ilike(f"%{search}%"),
                models.Product.description.ilike(f"%{search}%")
            )
        )

    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)

    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    products = query.order_by(models.Product.id).offset((page - 1) * limit).limit(limit).all()
    return products


@router.get("/{product_id}",response_model=schemas.ProductResponse)
def get_single_product(product_id:int,db:Session=Depends(get_db)):
    return get_active_product_or_404(db,product_id)


    
@router.post("/",response_model=schemas.ProductResponse)
def create_product(product:schemas.ProductCreate,db:Session=Depends(get_db),admin:models.User=Depends(get_current_admin)):
    category = db.query(models.Category).filter(models.Category.id == product.category_id).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found.")

    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.patch("/{product_id}",response_model=schemas.ProductResponse)
def update_product(product_id:int,product_update:schemas.ProductUpdate,db:Session=Depends(get_db),admin:models.User=Depends(get_current_admin)):
    product = get_active_product_or_404(db,product_id)

    update_data = product_update.model_dump(exclude_unset=True,exclude_none=True)

    if "category_id" in update_data:
        category = db.query(models.Category).filter(models.Category.id == update_data["category_id"]).first()

        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found.")


    for key, value in update_data.items():
        setattr(product,key,value)

    db.commit()
    db.refresh(product)
    return product



@router.delete("/{product_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id:int,db:Session=Depends(get_db),admin:models.User=Depends(get_current_admin)):
    product = get_active_product_or_404(db,product_id)
    product.is_active = False
    db.commit()
    return None

@router.post("/{product_id}/image",response_model=schemas.ProductResponse)
def upload_product_image(product_id:int,file:UploadFile=File(...),db:Session=Depends(get_db),admin:models.User=Depends(get_current_admin)):
    product = get_active_product_or_404(db,product_id)

    if file.content_type not in ALLOWED_IMAGES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only JPG, PNG, WEBP allowed")

    content = file.file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Image must be under 5MB")

    try:
        result = cloudinary.uploader.upload(
            io.BytesIO(content),
            folder="ecommerce/product",
            transformation=[{"width":800,"height":800,"crop":"limit"}]
        )

    except Exception as e:
        print("CLOUDINARY ERROR:", repr(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,detail="Image upload failed")

    if product.image_public_id:
        try:
            cloudinary.uploader.destroy(product.image_public_id)

        except Exception:
            pass

    

    product.image_url = result["secure_url"]
    product.image_public_id = result["public_id"]
    db.commit()
    db.refresh(product)
    return product

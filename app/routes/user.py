from fastapi import APIRouter,status,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models,schemas,auth
from app.database import get_db
from app.dependencies import get_current_user



router = APIRouter(prefix="/users",tags=["users"])


@router.post("/register",response_model=schemas.UserResponse,status_code=status.HTTP_201_CREATED)
def create_user(user:schemas.UserCreate,db:Session=Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already registerd.")

    hash_password = auth.hashed_password(user.password)

    new_user = models.User(email = user.email, hashed_password = hash_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login",response_model=schemas.Token)
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not auth.verify_hashed_password(plain_password=form_data.password,password=user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid email or password.")

    

    token = auth.create_access_token(data={"sub":user.email})

    return {"access_token":token,"token_type":"bearer"}

@router.get("/me",response_model=schemas.UserResponse)
def get_me(current_user:models.User=Depends(get_current_user)):
    return current_user

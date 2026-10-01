from fastapi import Depends,status,HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_token
from app import models


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(token:str=Depends(oauth_scheme),db:Session=Depends(get_db)):

    credential_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )

    email = verify_token(token)

    if not email:
        raise credential_exceptions

    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise credential_exceptions

    return user


def get_current_admin(current_user:models.User=Depends(get_current_user)):

    if current_user.role != models.UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",           
        )

    return current_user
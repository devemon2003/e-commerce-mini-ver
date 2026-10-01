from datetime import datetime,timedelta,timezone
from passlib.context import CryptContext
from jose import jwt,JWSError
from dotenv import load_dotenv
from typing import Optional
import os


load_dotenv()


SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES=int(os.getenv("ACCESS_TOKEN_EXPIRES"))


pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")


def hashed_password(password:str) -> str:
    password = password[:72]
    return pwd_context.hash(password)

def verify_hashed_password(plain_password:str,password:str) -> bool:
    plain_password = plain_password[:72]
    return pwd_context.verify(plain_password,password)


def create_access_token(data:dict,expires_delta:Optional[timedelta] = None):
    to_encoded = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRES))
    to_encoded.update({"exp":expire})
    return jwt.encode(to_encoded,SECRET_KEY,algorithm=ALGORITHM)


def verify_token(token:str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWSError:
        return None
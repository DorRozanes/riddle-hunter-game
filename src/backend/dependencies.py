from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from .config import get_settings
from .models import User
from .db import SessionLocal



settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # used by docs

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_token(token: str = Depends(oauth2_scheme)) -> int:
    """
    Verifies the token signature and returns the user_id (sub claim).
    Raises HTTPException(401) if invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise credentials_exception

def get_current_user(user_id: int = Depends(authenticate_token), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


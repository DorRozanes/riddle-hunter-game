# services/auth_service.py
import bcrypt
from datetime import datetime, timedelta
import jwt

from sqlalchemy.orm import Session

from models import User
from config import get_settings

settings = get_settings()

def get_password_hash(plain_password: str) -> str:
    # bcrypt requires bytes
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False

def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=(expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    # PyJWT returns a string
    return token

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    print (f"username: {username}, password: {password}")

    if not user:
        return None
    print (f"User's password: {user.password_hash}")
    if not verify_password(password,user.password_hash):
        print ("Unverified")
        return None
    print ("Verified")
    return user

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..services.auth_service import get_password_hash, create_access_token, authenticate_user
from ..dependencies import get_db
from ..schemas.auth import UserCreate, UserOut, LoginRequest, Token
from ..models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # ensure unique username/email
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="User with that username already exists")

    hashed = get_password_hash(user_in.password)
    user = User(username=user_in.username, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm provides username & password fields
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token_data = {"sub": str(user.user_id)}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

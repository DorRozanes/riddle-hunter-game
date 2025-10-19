from fastapi import APIRouter, Depends

from dependencies import get_current_user
from schemas.auth import UserOut

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def read_me(current_user = Depends(get_current_user)):
    # current_user is the SQLAlchemy model instance
    return current_user


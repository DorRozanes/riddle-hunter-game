from fastapi import APIRouter

router = APIRouter(prefix="/api/ping", tags=["ping"])

@router.post("/", tags=["ping"])
def ping():
    return {"msg": "pong"}
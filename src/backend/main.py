from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from db import engine, Base, init_postgis, check_schema_sync
from dependencies import get_db
from routers import auth, user, location
from enemies import router as enemies_router


# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: enable PostGIS, then create tables
    init_postgis(engine)

    # Schema verification step
    if not check_schema_sync(engine,Base.metadata):
        print("❌ Schema mismatch detected — aborting startup.")
        raise SystemExit(1)
    else:
        print("✅ Database and models are synced")

    yield  # <-- the app runs while inside this block

    # Shutdown (optional cleanup)
    print("👋 Shutting down")

app = FastAPI(lifespan=lifespan)

# Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",  # React dev
#         "http://127.0.0.1:3000"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# I'm using this version, because ngrok sends requests using random ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(location.router)
app.include_router(enemies_router.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

@app.get("/api/db-check")
def db_check(db: Session = Depends(get_db)):
    try:
        db.execute(sqlalchemy.text('SELECT 1'))
        return {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


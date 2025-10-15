from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routers import quizes
from app.routers.all_routers import api_router
from app.db.database import engine, Base, AsyncSessionLocal
from app.crud import init_tree_catalog
from app.routers import quizes 
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"]) 

app = FastAPI(swagger_ui_parameters={"oauth2RedirectUrl": None})
app.include_router(quizes.router)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.on_event("startup")
async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        await init_tree_catalog(db)

@app.get("/healthz")
def healthz():
  return {"ok": True}

app.include_router(quizes.router)

if __name__ == "__main__":
  import uvicorn
  uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
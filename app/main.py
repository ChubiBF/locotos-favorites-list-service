from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router as favorites_router

app = FastAPI(title="Locotos Interaction Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(favorites_router)

@app.get("/health", tags=["Utility"])
async def health_check():
    return {"status": "online", "service": "Interaction Service"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router as favorites_router
from app.api.download_routes import router as downloads_router
from app.api.media_routes import router as media_router

app = FastAPI(title="Locotos Interaction Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "Accept"], 
    expose_headers=["*"]
)

app.include_router(favorites_router)
app.include_router(downloads_router)
app.include_router(media_router)

@app.get("/health", tags=["Utility"])
async def health_check():
    return {"status": "online", "service": "Interaction Service"}
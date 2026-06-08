import os
import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.core.database import download_tokens_collection
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/media", tags=["Persistencia Local"])


VIDEO_SAMPLE_PATH = os.path.join(os.getcwd(), "sample_offline.mp4")

@router.get("/download-file/{id_contenido}")
async def download_video_binary(id_contenido: str, token: str = Query(None)):
    
    if not token: 
        raise HTTPException(status_code=403, detail="Token requerido.")
        
    token_db = await download_tokens_collection.find_one({"token": token})
    if not token_db or datetime.utcnow() > token_db["expira_en"]:
        raise HTTPException(status_code=403, detail="Token inválido o expirado.")
        
    await download_tokens_collection.delete_one({"token": token})

    video_url = None
    usar_respaldo_local = True

    
    try:
        client_mongo = AsyncIOMotorClient("mongodb://127.0.0.1:27017")
        db = client_mongo["ContenidoDB"]
        coleccion = db["contenidos"]
        
        documento = None
        if len(id_contenido) == 24:
            try:
                documento = await coleccion.find_one({"_id": ObjectId(id_contenido)})
            except Exception: pass
            
        if not documento:
            documento = await coleccion.find_one({"$or": [{"_id": id_contenido}, {"id_contenido": id_contenido}]})

        if documento:
            video_url = documento.get("url") or documento.get("trailer_url")
            if video_url and "youtube" not in video_url.lower():
                usar_respaldo_local = False
    except Exception:
        pass

    
    async def streamer():
        
        if not usar_respaldo_local and video_url:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                async with httpx.AsyncClient(follow_redirects=True, headers=headers, timeout=15.0) as client:
                    async with client.stream("GET", video_url) as res:
                        if res.status_code == 200:
                            bytes_enviados = 0
                            async for chunk in res.iter_bytes(chunk_size=65536):
                                bytes_enviados += len(chunk)
                                yield chunk
                            
                            
                            if bytes_enviados > 0:
                                return
            except Exception:
                pass

        
        if os.path.exists(VIDEO_SAMPLE_PATH):
            with open(VIDEO_SAMPLE_PATH, "rb") as video_file:
                while chunk := video_file.read(65536):
                    yield chunk
        else:
            
            yield b""

    return StreamingResponse(
        streamer(), 
        media_type="video/mp4", 
        headers={
            "Cache-Control": "no-cache"
        }
    )
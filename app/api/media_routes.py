import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.core.database import download_tokens_collection
from datetime import datetime

router = APIRouter(prefix="/media", tags=["HU-15 Descargas Real"])

@router.get("/download-file/{id_contenido}")
async def download_video_binary(id_contenido: str, token: str = Query(None)):
    
    if not token: raise HTTPException(status_code=403, detail="Falta token")
    token_db = await download_tokens_collection.find_one({"token": token})
    if not token_db or datetime.utcnow() > token_db["expira_en"]:
        raise HTTPException(status_code=403, detail="Token expirado")
    await download_tokens_collection.delete_one({"token": token})

    
    movie_data = None
    async with httpx.AsyncClient() as client:
        for puerto in ["5000", "3001"]:
            try:
                
                url_catalogo = f"http://127.0.0.1:{puerto}/contenido/{id_contenido}"
                response = await client.get(url_catalogo, timeout=3.0)
                if response.status_code == 200:
                    movie_data = response.json()
                    break
            except Exception: continue

    if not movie_data:
        raise HTTPException(status_code=504, detail="No se encontró la película en el catálogo real.")

    
    video_url = movie_data.get("trailer_url") or movie_data.get("url")
    
    
    async def streamer():
        async with httpx.AsyncClient(follow_redirects=True) as col:
            async with col.stream("GET", video_url) as res:
                async for chunk in res.iter_bytes(chunk_size=32768):
                    yield chunk

    nombre = movie_data.get("titulo", "video").replace(" ", "_")
    return StreamingResponse(streamer(), media_type="video/mp4", headers={
        "Content-Disposition": f"attachment; filename={nombre}.mp4"
    })
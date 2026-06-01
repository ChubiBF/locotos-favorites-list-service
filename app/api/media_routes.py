import os
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import FileResponse
from app.core.database import download_tokens_collection
from datetime import datetime

router = APIRouter(prefix="/media", tags=["Download"]) 

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) 
VIDEO_FILE_PATH = os.path.join(BASE_DIR, "storage", "sample_offline.mp4") 

@router.get("/download-file/{id_contenido}")
async def download_video_binary(id_contenido: int, token: str = Query(None)):
    """
    Endpoint protegido. Requiere un token firmado válido y vigente en MongoDB Atlas 
    para poder descargar los bytes del archivo de video.
    """
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requiere un token de autorización para descargar este contenido."
        )

    
    token_db = await download_tokens_collection.find_one({"token": token, "id_contenido": id_contenido})
    
    if not token_db:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: El token proporcionado no es válido o no corresponde a este contenido."
        )

    
    if datetime.utcnow() > token_db["expira_en"]:
        
        await download_tokens_collection.delete_one({"token": token})
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Acceso denegado: El enlace de descarga ha expirado (límite de 60 segundos superado)."
        )

    await download_tokens_collection.delete_one({"token": token})

    if not os.path.exists(VIDEO_FILE_PATH): 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El archivo físico de video no se encuentra disponible."
        ) 
    
    return FileResponse(
        path=VIDEO_FILE_PATH,
        media_type="video/mp4",
        filename=f"video_content_{id_contenido}.mp4"
    ) 
    
#     import httpx
# from fastapi import APIRouter, HTTPException, status, Query
# from fastapi.responses import StreamingResponse
# from app.core.database import download_tokens_collection
# from app.core.config import settings
# from datetime import datetime

# router = APIRouter(prefix="/media", tags=["HU-15 Media Download"])

# @router.get("/download-file/{id_contenido}")
# async def download_video_binary(id_contenido: int, token: str = Query(None)):
#     # 1. Validar el token de seguridad temporal que guardamos en Mongo Atlas
#     if not token:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token requerido.")

#     token_db = await download_tokens_collection.find_one({"token": token, "id_contenido": id_contenido})
#     if not token_db or datetime.utcnow() > token_db["expira_en"]:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token inválido o expirado.")

#     # Consumimos el token eliminándolo de Atlas
#     await download_tokens_collection.delete_one({"token": token})

#     # 2. obtener la URL real del video
#     async with httpx.AsyncClient() as client:
#         try:
#             # Consulta al microservicio del catalogo 
#             catalog_response = await client.get(f"{settings.CATALOG_SERVICE_URL}/content/{id_contenido}")
#         except httpx.RequestError:
#             raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Catálogo no disponible.")

#     if catalog_response.status_code != 200:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contenido no encontrado en el catálogo.")

#     movie_data = catalog_response.json()
#     video_url_real = movie_data.get("url_video") # Extrae la URL real

#     if not video_url_real:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El contenido no tiene una URL de video válida.")

#     # DESCARGA Y STREAMING DEL BINARIO REAL
#     async def video_streamer():
#         async with httpx.AsyncClient() as client:
#             async with client.stream("GET", video_url_real) as r:
#                 async for chunk in r.iter_bytes(chunk_size=8192):
#                     yield chunk

#     return StreamingResponse(
#         video_streamer(),
#         media_type="video/mp4",
#         headers={"Content-Disposition": f"attachment; filename=video_catalogo_{id_contenido}.mp4"}
#     )
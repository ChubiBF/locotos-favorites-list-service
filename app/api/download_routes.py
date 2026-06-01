from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.download import DownloadCreate
from app.services.download_service import DownloadService
from typing import Optional


router = APIRouter(prefix="/downloads", tags=["Downloads"])

security = HTTPBearer()

@router.post("", status_code=status.HTTP_201_CREATED)
async def start_download(payload: DownloadCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Endpoint para autorizar descargas offline. 
    Requiere obligatoriamente un token JWT válido enviado en la cabecera Authorization.
    """
    token_string = f"Bearer {credentials.credentials}"

    response = await DownloadService.authorize_and_create(payload, token_string)
    return response

@router.get("/user/{id_usuario}")
async def get_user_downloads(id_usuario: int):
    downloads = await DownloadService.get_active_downloads(id_usuario)
    return {
        "id_usuario": id_usuario,
        "total_descargas": len(downloads),
        "descargas": downloads
    }

@router.delete("/user/{id_usuario}/content/{id_contenido}")
async def delete_download(id_usuario: int, id_contenido: int):
    was_deleted = await DownloadService.revoke_download(id_usuario, id_contenido)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se encontró ningún registro de descarga activa para este contenido."
        )
    return {"message": "Registro de descarga removido de la base de datos con éxito."}
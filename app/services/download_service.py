import secrets
import httpx 
from app.core.database import downloads_collection, download_tokens_collection
from app.schemas.download import DownloadCreate
from datetime import datetime, timedelta
from fastapi import HTTPException, status

AUTH_VALIDATE_URL = "http://localhost:3000/api/auth/validate-session"

class DownloadService:
    
    @staticmethod
    async def authorize_and_create(payload: DownloadCreate, auth_header: str) -> dict:
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se proporcionó el token de autenticación (Authorization Header faltante)."
            )
            
        async with httpx.AsyncClient() as client:
            try:
                auth_response = await client.get(
                    AUTH_VALIDATE_URL,
                    headers={"Authorization": auth_header}
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="El servicio de Autenticación (M1) no se encuentra disponible temporalmente."
                )
                
        if auth_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión inválida o expirada en el sistema central de identidad."
            )
            
        auth_data = auth_response.json()
        

        id_usuario_verificado = auth_data.get("id_usuario")
        
        existing = await downloads_collection.find_one({
            "id_usuario": id_usuario_verificado,
            "id_contenido": payload.id_contenido
        })
        
        if not existing:
            document = {
                "id_usuario": id_usuario_verificado,
                "id_contenido": payload.id_contenido,
                "dispositivo": payload.dispositivo,
                "fecha_descarga": datetime.utcnow(),
                "fecha_expiracion": datetime.utcnow() + timedelta(days=7),
                "tamano_estimado_mb": 45.0
            }
            await downloads_collection.insert_one(document)

        # generacion token pa descarga
        secure_token = secrets.token_urlsafe(32)
        token_document = {
            "token": secure_token,
            "id_contenido": payload.id_contenido,
            "id_usuario": id_usuario_verificado,
            "expira_en": datetime.utcnow() + timedelta(minutes=1)
        }
        await download_tokens_collection.insert_one(token_document)

        return {
            "status": "authorized",
            "message": f"Sesión verificada para usuario {id_usuario_verificado}. Token válido por 60s.",
            "id_contenido": payload.id_contenido,
            "url_video_offline": f"http://localhost:3010/media/download-file/{payload.id_contenido}?token={secure_token}"
        }

    @staticmethod
    async def get_active_downloads(id_usuario: int) -> list:
        cursor = downloads_collection.find({"id_usuario": id_usuario})
        active_list = []
        async for doc in cursor:
            active_list.append({
                "id_contenido": doc["id_contenido"],
                "dispositivo": doc["dispositivo"],
                "fecha_descarga": doc["fecha_descarga"].isoformat(),
                "fecha_expiracion": doc["fecha_expiracion"].isoformat()
            })
        return active_list

    @staticmethod
    async def revoke_download(id_usuario: int, id_contenido: int) -> bool:
        result = await downloads_collection.delete_one({
            "id_usuario": id_usuario,
            "id_contenido": id_contenido
        })
        return result.deleted_count > 0
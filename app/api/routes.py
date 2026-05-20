from fastapi import APIRouter, HTTPException, status
from app.schemas.favorite import FavoriteCreate
from app.core.database import favorites_collection
from datetime import datetime

router = APIRouter(prefix="/favorites", tags=["Favorites & Personalization"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_to_favorites(payload: FavoriteCreate):

    existing = await favorites_collection.find_one({
        "id_usuario": payload.id_usuario,
        "id_contenido": payload.id_contenido,
        "tipo_lista": payload.tipo_lista
    })
    if existing:
        raise HTTPException(status_code=400, detail="El contenido ya se encuentra en la lista de favoritos")
    

    new_favorite = {
        "id_usuario": payload.id_usuario,
        "id_contenido": payload.id_contenido,
        "tipo_lista": payload.tipo_lista,
        "fecha_agregado": datetime.utcnow()
    }
    
    await favorites_collection.insert_one(new_favorite)
    return {"message": "Contenido agregado a favoritos exitosamente"}

@router.get("/user/{id_usuario}")
async def get_user_favorites(id_usuario: int):
    cursor = favorites_collection.find({"id_usuario": id_usuario, "tipo_lista": "favorito"})
    results = []
    
    async for document in cursor:
        results.append({
            "id_contenido": document["id_contenido"],
            "tipo_lista": document["tipo_lista"],
            "fecha_agregado": document["fecha_added"].isoformat() if "fecha_added" in document else document.get("fecha_agregado")
        })
        
    return {
        "id_usuario": id_usuario,
        "total": len(results),
        "favoritos": results
    }

@router.delete("/user/{id_usuario}/content/{id_contenido}")
async def remove_from_favorites(id_usuario: int, id_contenido: int):
    result = await favorites_collection.delete_one({
        "id_usuario": id_usuario,
        "id_contenido": id_contenido,
        "tipo_lista": "favorito"
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="El contenido no se encontró en la lista de favoritos de este usuario")
        
    return {"message": "Contenido removido de favoritos exitosamente"}
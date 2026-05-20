from pydantic import BaseModel
from typing import Optional

class FavoriteCreate(BaseModel):
    id_usuario: int
    id_contenido: int
    tipo_lista: Optional[str] = "favorito"
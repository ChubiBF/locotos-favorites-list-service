from pydantic import BaseModel
from typing import Optional

class DownloadCreate(BaseModel):
    id_usuario: int
    id_contenido: int
    dispositivo: Optional[str] = "Web Browser"
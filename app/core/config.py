import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Locotos Interaction & Personalization Service"
    PORT: int = int(os.getenv("PORT", 3003))
    
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "StreamingDB_Interaction")

settings = Settings()
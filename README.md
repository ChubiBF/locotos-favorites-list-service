**.env**
####
**importante puerto 3010 no confundir con otros**
PORT=3010
####
MONGO_URI= aqui url
####
MONGO_DB_NAME=StreamingDB_Interaction
##
**INSTALAR Y CORRER**
####
pip install -r requirements.txt
####
uvicorn app.main:app --reload --port 3010
<img width="767" height="115" alt="image" src="https://github.com/user-attachments/assets/8a17f8af-997d-456b-811f-7de4712d09a7" />

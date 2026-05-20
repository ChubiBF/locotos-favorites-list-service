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

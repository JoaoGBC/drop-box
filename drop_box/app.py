from fastapi import FastAPI
from api.v0.routes.clientAccess import storage_router


app = FastAPI()


app.include_router(storage_router)
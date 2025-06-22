from fastapi import FastAPI
from .minIO.routes.clientAccess import minio_client_access_router


app = FastAPI()


app.include_router(minio_client_access_router)
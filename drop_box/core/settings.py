from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    ENDPOINT_OS: Annotated[str, 'Endpoint de acesso ao object storage']
    ACCESS_KEY_OS: Annotated[str, 'Id de acesso ao object storage']
    SECRET_KEY_OS: Annotated[str, 'Key/senha de acesso ao object storage']
    ALLOWED_FILE_TYPES: str
    MAX_SINGLEPART_UPLOAD_SIZE_BYTES: int
    MULTIPART_CHUNK_SIZE_BYTES: int
    SECRET_KEY_UPLOAD_SERVICE_TOKEN: str



settings = Settings()

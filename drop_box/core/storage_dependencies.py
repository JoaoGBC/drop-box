from http import HTTPStatus
from typing import Annotated
from fastapi import HTTPException, Header
from functools import lru_cache
import boto3


from .settings import settings
from services import UploadService, MinioStorageService, IStorageService
from services.types import TokenPayload





client_b3 = boto3.client(
    's3',
    region_name='us-east-1',
    endpoint_url=settings.ENDPOINT_OS,
    aws_access_key_id=settings.ACCESS_KEY_OS,
    aws_secret_access_key=settings.SECRET_KEY_OS,
    verify=False,
)

@lru_cache
def get_storage_service() -> IStorageService:
    storage_service = MinioStorageService(
        client=client_b3,
        url_duration_seconds=900
    )

    return storage_service

@lru_cache
def get_upload_service() -> UploadService:
    storage_service = get_storage_service()
    upload_serivce = UploadService(
        storage_service=storage_service,
        allowed_types=settings.ALLOWED_FILE_TYPES,
        max_singlepart_size_bytes=settings.MAX_SINGLEPART_UPLOAD_SIZE_BYTES,
        multpart_chunk_size_bytes=settings.MULTIPART_CHUNK_SIZE_BYTES,
        secret_key=settings.SECRET_KEY_UPLOAD_SERVICE_TOKEN,
        overwrite_allowed=False
    )

    return upload_serivce


def get_upload_token(
    update_token: Annotated[str, Header()]
    ) -> TokenPayload:

    if not update_token:
        raise HTTPException(
            status_code= HTTPStatus.UNAUTHORIZED,
            detail = 'For url generation, put upload_token on header'
        )
    
    try:
        payload = UploadService.decode_upload_token(
            token=update_token,
            secret_key=settings.SECRET_KEY_UPLOAD_SERVICE_TOKEN,
        )

        return payload
    except Exception as e:
        raise HTTPException(
            status_code= HTTPStatus.UNAUTHORIZED,
            detail='Invalid or expired token'
        )
    
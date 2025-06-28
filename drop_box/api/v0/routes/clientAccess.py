from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException

from core.storage_dependencies import get_upload_service, get_upload_token
from services.types import TokenPayload
from schemas.upload_flow import UploadInfo
from services.upload_service import UploadService
from services.exceptions import (
    UnauthorizedOverWriteAttempt,
    UnauthorizedUrlPartRequest,
)
from .exceptions import unauthorized_url_part_exception



storage_router = APIRouter(
    prefix='/obs', tags=['Object Storage for Client Side']
)


T_upload_service = Annotated[UploadService, Depends(get_upload_service)]
T_upload_token = Annotated[TokenPayload, Depends(get_upload_token)]

@storage_router.post('/init_upload_flow')
async def start_upload_flow(
    upload_info: UploadInfo,
    uploader: T_upload_service,
):
    response = None
    while not response:
        try:
            file_name = f'{uuid4()}__{upload_info.file_name}'
            upload_ticket = await uploader.initiate_upload(
                file_name=file_name,
                file_size=upload_info.file_size,
                content_type=upload_info.mime_type,
                bucket_name='app1-teste1'
            )
        except UnauthorizedOverWriteAttempt as e:
            raise unauthorized_url_part_exception
    return upload_ticket



@storage_router.post('/')
async def get_urls(
    upload_token: T_upload_token,
    uploader: T_upload_service,
    parts: list[int]
):
    try:
        url_obj = await uploader.generate_url(
            update_token=upload_token,
            bucket_name='app1-teste1',
            parts=parts,
        )
        return url_obj
    except UnauthorizedUrlPartRequest:
        raise unauthorized_url_part_exception
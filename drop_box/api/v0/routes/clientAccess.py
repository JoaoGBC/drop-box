from fastapi import APIRouter

from drop_box.minIO.schemas.upload_flow import UploadInfo
from drop_box.minIO.services.presigned_url_generation import generate_presigned_urls



minio_client_access_router = APIRouter(
    prefix='/obs', tags=['MinIO Client Side']
)


@minio_client_access_router.post('/upload')
async def start_upload_flow(upload_info: UploadInfo):
    '''
    Inicia o fluxo de upload pelo client side,
    retornando a(s) url(s) pre-assinada(s).
    '''
    try:
        urls = await generate_presigned_urls(
            file_name= upload_info.file_name,
            bucket_name='app1-teste1',
            content_type=upload_info.mime_type,
            part_range=upload_info.part_range,
            overwrite_allowed=False,
            duration_seconds=3600
        )
        return urls
    except Exception as e:
        raise e
    

@minio_client_access_router.put('/end-multipart')
async def end_multipart_upload(
    upload_id: str,
    file_name: str,
):
    '''Finaliza o fluxo de um upload multipart'''
    
    if await end_multipart_upload(
        upload_id=upload_id,
        file_name=file_name,
    ):
        return {'message' : f'multipart upload completed. id: {upload_id}'}
    
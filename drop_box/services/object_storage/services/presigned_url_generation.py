# from miniopy_async import Minio
import asyncio
import boto3
from botocore.exceptions import ClientError
from .exceptions import UnauthorizedOverWriteAttempt

from typing import Any, Coroutine, TypedDict, Literal
from datetime import datetime, timezone

class ObjectStorageLinkDict(TypedDict):
    url: str
    send_method: Literal['POST', 'GET', 'PUT', 'DELETE']
    expires_at: datetime


class SinglepartUploadLinksDict(TypedDict):
    object_name: str
    urls: ObjectStorageLinkDict


class MultipartUploadLinksDict(TypedDict):
    object_name: str
    file_name: str
    upload_id: str
    current_part_count: int
    urls: list[ObjectStorageLinkDict]




NOT_FOUND = '404'


client_b3 = boto3.client(
    's3',
    endpoint_url='http://minio.ykkl.duckdns.org:8080',
    aws_access_key_id='ZMPHEHKnLo3fH33mgFb5',
    aws_secret_access_key='kQkNzfxcpQCZgZ0n3zPMEMXvZNp3IXP9nmIpQf0F',
    region_name = 'us-east-1',
    verify=False
)


async def object_in_bucket(
    *,
    file_name: str,
    bucket_name: str,
) -> bool:
    try :
        obj = await asyncio.to_thread(
                client_b3.head_object,
                Bucket=bucket_name,
                Key=file_name
        )
        if obj:
            return True
    except ClientError as e:
        if e.response.get('Error').get('Code') == NOT_FOUND:
            return False
        raise e
    

async def _generate_presigned_url_batch(
    *,
    upload_id: str,
    bucket_name: str,
    file_name: str,
    part_range: tuple[int, int],
    duration_seconds: int,
) -> list[str]:
    '''
    Gera uma batch de urls pré assinadas para uploads multiparts.
    '''
    tasks = [
        asyncio.to_thread(
            client_b3.generate_presigned_url,
            'upload_part',
            Params = {
                'Bucket': bucket_name,
                'Key' : file_name,
                'UploadId': upload_id,
                'PartNumber': part_number,
            },
            ExpiresIn = duration_seconds,
        ) for part_number in 
        range(part_range[0], part_range[1]+1)
    ]

    url_list = await asyncio.gather(*tasks)

    return url_list


    

async def generate_multipart_upload_urls(
    *,
    file_name: str,
    bucket_name: str,
    content_type: str,
    part_range: tuple[int, int],
    duration_seconds: int = 3600,
    upload_id: str | None = None,
) -> MultipartUploadLinksDict:
    if not upload_id:
        try:
            init_upload_response = await asyncio.to_thread(
                client_b3.create_multipart_upload,
                Bucket=bucket_name,
                Key=file_name,
                ContentType = content_type,
            )
            breakpoint()
            upload_id = init_upload_response.get('UploadId')
        except ClientError as e:
            ## TODO: Configurar erro na hierarquia do modulo para esse ponto
            ## e adicionar logs.
            raise e
        
    urls = await _generate_presigned_url_batch(
        upload_id= upload_id,
        bucket_name=bucket_name,
        file_name=file_name,
        part_range=part_range,
        duration_seconds=duration_seconds
    )

    return {
        'current_part_count' : part_range[1],
        'object_name': file_name,
        'file_name': file_name,
        'upload_id' : init_upload_response.get('UploadId'),
        'urls': [
            {
                'expires_at' : datetime.fromtimestamp(
                    int(item.split('Expires=')[1]), tz=timezone.utc
                ),
                'send_method' : 'PUT',
                'url': item
            }
            for item in urls
        ]
    }

    ...

async def generate_singlepart_upload_url(
    *,
    file_name,
    bucket_name: str,
    duration_seconds: int,
) -> SinglepartUploadLinksDict:
    url = await asyncio.to_thread(
        client_b3.generate_presigned_url,
        'put_object',
        Params = {
            'Bucket': bucket_name,
            'Key' : file_name,
        },
        ExpiresIn = duration_seconds
    )

    return {
        'object_name' : file_name,
        'urls': {
            'expires_at' : datetime.fromtimestamp(int(url.split("Expires=")[1]), tz=timezone.utc),
            'send_method': 'PUT',
            'url' : url
        }
    }
    
    ...




async def generate_presigned_urls(
    *,
    file_name: str,
    bucket_name: str,
    part_range: tuple[int, int] | None = None,
    upload_id: str | None = None,
    content_type: str | None = None,
    overwrite_allowed: bool = False,
    duration_seconds: int = 3600,
) -> SinglepartUploadLinksDict | MultipartUploadLinksDict:

    if not overwrite_allowed:
        object_exists = await object_in_bucket(file_name=file_name, bucket_name=bucket_name)
        if object_exists:
            raise UnauthorizedOverWriteAttempt()
    
    
    if part_range:
        urls = await generate_multipart_upload_urls(
            file_name=file_name,
            bucket_name=bucket_name,
            content_type=content_type,
            duration_seconds=duration_seconds,
            part_range=part_range,
            upload_id=upload_id,
        )
        return urls
    
    resp = await generate_singlepart_upload_url(
        file_name=file_name,
        bucket_name=bucket_name,
        duration_seconds=duration_seconds
    )

    return resp




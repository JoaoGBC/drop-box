import asyncio
from datetime import datetime, timedelta, timezone
from mypy_boto3_s3 import S3Client
from botocore.client import ClientError
from tzlocal import get_localzone
from drop_box.services.object_storage.interface import IStorageService
from .exceptions import (
    UnauthorizedOverWriteAttempt,
    UnexpectedPartCount
)
from .types import SinglepartUploadLinksDict, MultipartUploadLinksDict

class MinioStorageService(IStorageService):
    _NOT_FOUND = '404'

    def __init__(
            self,
            client: S3Client,
            url_duration_seconds: int
        ):
        self._client = client
        self.url_duration_seconds = url_duration_seconds

    
    def _calculate_expiration_time(self) -> datetime:
        return (
            datetime.now(
                tz=get_localzone()
                ) + timedelta(seconds=self.url_duration_seconds)
            )

    async def generate_single_presigned_url(
        self,
        *,
        file_name,
        bucket_name: str,
        duration_seconds: int,
    ) -> SinglepartUploadLinksDict:
        url = await asyncio.to_thread(
                self._client.generate_presigned_url,
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
                'expires_at' : self._calculate_expiration_time(),
                'send_method': 'PUT',
                'url' : url
            }
        }
    
    async def generate_multipart_upload_urls(
        self,
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
                    self._client.create_multipart_upload,
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
            
        urls = await self._generate_presigned_url_batch(
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
                    'expires_at' : self._calculate_expiration_time(),
                    'send_method' : 'PUT',
                    'url': item
                }
                for item in urls
            ]
        }

    async def object_in_bucket(
        self,
        *,
        file_name: str,
        bucket_name: str,
    ) -> bool:
        try :
            obj = await asyncio.to_thread(
                    self._client.head_object,
                    Bucket=bucket_name,
                    Key=file_name
            )
            if obj:
                return True
        except ClientError as e:
            if e.response.get('Error').get('Code') == self._NOT_FOUND:
                return False
            raise e

    async def _generate_presigned_url_batch(
        self,
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
                self._client.generate_presigned_url,
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
    
    async def _end_multipart_upload(
        self,
        *,
        upload_id: str,
        file_name: str,
        bucket_name: str,
    ) -> None:
        try:
            await asyncio.to_thread(
                self._client.complete_multipart_upload,
                Bucket= bucket_name,
                Key=file_name,
                UploadId=upload_id
            )
        except ClientError as e:
            raise e
    
    async def verify_part_count(
        self,
        *,
        bucket_name: str,
        expected_part_count: str,
        upload_id: str,
        file_name: str,
    ) -> bool:
        '''
        Verifica se existem `expected_part_count` partes no servidor. Caso exista 
        retorna true, caso não existam, levanta `UnexpectedPartCount`.

        :param str bucket_name: Nome do bucket onde irá verificar as partes.
        :param int expected_part_count: Numero de partes que se espera que existam.
        :param str upload_id: id do multipart upload referente às partes.
        :param str filename: key referente do upload.

        :return bool: True caso o numero de partes seja o esperado.
            
        :raises UnexpectedPartCount: Caso o numero de partes não seja o esperado.
        '''
        parts = await asyncio.to_thread(
            self._client.list_parts,
            Bucket= bucket_name,
            Key = file_name,
            UploadId= upload_id,
        )

        parts = parts.get('Parts')
        if len(parts) != expected_part_count:
            raise UnexpectedPartCount()

        return True


    async def end_multipart_upload(
        self,
        *
        upload_id,
        file_name,
        bucket_name: str,
        current_part_count: int | None,
        verify_parts: bool = True,
    ) -> None:

        if verify_parts:
            await self.verify_part_count(
                bucket_name=bucket_name,
                file_name=file_name,
                expected_part_count=current_part_count,
                upload_id=upload_id,
            )
        
        await self._end_multipart_upload(
            upload_id=upload_id,
            file_name=file_name,
            bucket_name=bucket_name
        )
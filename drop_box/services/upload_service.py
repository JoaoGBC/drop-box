from datetime import datetime, timedelta
import math
from typing import Iterable
from jwt import encode, decode
from tzlocal import get_localzone

from .types import TokenPayload, UploadTicket, UrlDict
from .exceptions import TypeNotAllowed, UnauthorizedUrlPartRequest
from services.object_storage.interface import IStorageService






class UploadService:
    jwt_algorithm = "HS256"
    def __init__(
        self,
        *,
        storage_service: IStorageService,
        allowed_types: Iterable[str],
        max_singlepart_size_bytes: int,
        multpart_chunk_size_bytes: int,
        secret_key: str,
        overwrite_allowed: bool = False,
    ) -> None:
        self.storage_service = storage_service
        self.allowed_types = allowed_types
        self.max_singlepart_size_bytes = max_singlepart_size_bytes
        self.multpart_chunk_size_bytes = multpart_chunk_size_bytes
        self.allow_overwrite = overwrite_allowed
        self.__secret_key = secret_key

    def _verify_allowed_type(self, type: str) -> bool:
        if (
                "*" in self.allowed_types
                or
                f'{type.split("/")}/*' in self.allowed_types
            ):
            return True
        if type not in self.allowed_types:
            return False
        return True


    def _verity_max_size_singlepart(self, file_size) -> bool:
        if file_size <= self.max_singlepart_size_bytes:
            return True
        return False
    
    def _calculate_chunks(self, file_size) -> int:
        return math.ceil(file_size/self.max_singlepart_size_bytes)
    
    def _generate_upload_jwt(
            self,
            *,
            file_name: str,
            file_size: str,
            content_type: str,
            upload_id: str | None,
            
        ) -> str:
            return encode(
                payload={
                    'chunk_quantity': self._calculate_chunks(file_size),
                    'file_name': file_name,
                    'file_size': file_size,
                    'upload_id': upload_id,
                    'content_type': content_type,
                    'exp': (
                        datetime.now(tz= get_localzone())
                        + timedelta(hours=24)
                    )
                },
                key=self.__secret_key,
                algorithm = self.jwt_algorithm
            )
    
    @classmethod
    def decode_upload_token(
        cls,
        *,
        token: str,
        secret_key: str,
    ) -> TokenPayload:
    
        payload = decode(
            token,
            key = secret_key,
            algorithms= cls.jwt_algorithm
        )
        return payload
        

        
    async def initiate_upload(
        self,
        *,
        file_name: str,
        file_size: int,
        content_type: str,
        bucket_name: str
    ) ->  UploadTicket:
        if not self._verify_allowed_type(content_type):
            raise TypeNotAllowed
        
        url = None
        if self._verity_max_size_singlepart(file_size=file_size):
            url = await self.storage_service.generate_single_presigned_url(
                file_name=file_name,
                bucket_name=bucket_name,
                allow_override=self.allow_overwrite
            )
        
        else:
            url = await self.storage_service.generate_multipart_upload_urls(
                file_name=file_name,
                bucket_name=bucket_name,
                content_type=content_type,
                parts=list(range(5)),
                upload_id=None,
                allow_override=self.allow_overwrite                
            )

        token = self._generate_upload_jwt(
            file_name=file_name,
            file_size=file_size,
            content_type=content_type,
            upload_id= url.get('upload_id',None)
        )

        return {
            'number_of_chunks': self._calculate_chunks(file_size),
            'url' : url,
            'token': token,

        }
        
        
    async def generate_url(
            self,
            *,
            update_token: TokenPayload,
            bucket_name: str,
            parts: Iterable[int] | None,
        ) -> list[UrlDict]:
        

        if parts and not all(
            map(lambda x: 0< x <= update_token['chunk_quantity'], parts)
            ):
            raise UnauthorizedUrlPartRequest
        
        if parts:
            urls = await self.storage_service.generate_multipart_upload_urls(
                file_name=update_token['file_name'],
                allow_override=self.allow_overwrite,
                bucket_name=bucket_name,
                content_type=update_token['content_type'],
                parts=parts
            )
            return [
                {
                    'part_number': part,
                    'url': url['url'],
                    'expiration': url['expires_at'],
                } for url, part in zip(urls['urls'], parts)
            ]
        
        url = await self.storage_service.generate_single_presigned_url(
            file_name=update_token['file_name'],
            allow_override=self.allow_overwrite,
            bucket_name=bucket_name,
        )

        return [
            {'part_number' : 1,
            'url' : url['urls']['url'],
            'expiration': url['urls']['expires_at']}
        ]

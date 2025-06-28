from abc import ABC, abstractmethod
from typing import Iterable
from .types import SinglepartUploadLinksDict, MultipartUploadLinksDict

class IStorageService(ABC):
    @abstractmethod
    async def generate_single_presigned_url(
        *,
        file_name,
        bucket_name: str,
        allow_override: bool = False
    ) -> SinglepartUploadLinksDict:
        raise NotImplementedError
    
    @abstractmethod
    async def generate_multipart_upload_urls(
        *,
        file_name: str,
        bucket_name: str,
        content_type: str,
        parts: Iterable[int],
        upload_id: str | None = None,
        allow_override: bool = False
    ) -> MultipartUploadLinksDict:
        raise NotImplementedError
    

    @abstractmethod
    async def verify_part_count(
        *,
        bucket_name: str,
        expected_part_count: str,
        upload_id: str,
        file_name: str,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def end_multipart_upload(
        upload_id: str,
        file_name: str,
        bucket_name: str,
        current_part_count: int | None,
        verify_parts: bool = True,
    ) -> None:
        raise NotADirectoryError
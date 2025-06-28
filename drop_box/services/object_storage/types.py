from typing import Any, Coroutine, TypedDict, Literal
from datetime import datetime

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
    urls: list[ObjectStorageLinkDict]
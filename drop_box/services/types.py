from datetime import datetime
from typing import TypedDict

class UploadTicket(TypedDict):
    token: str
    number_of_chunks: int
    url: str

class UrlDict(TypedDict):
    url: str
    part_number: int
    expiration: datetime

class TokenPayload(TypedDict):
    chunk_quantity: int
    file_name: str
    file_size: int
    content_type: str
    upload_id: str | None
    exp: datetime
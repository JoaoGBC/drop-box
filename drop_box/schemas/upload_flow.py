from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, AnyHttpUrl, Field



class UploadInfo(BaseModel):
    file_name: str
    mime_type: str
    part_range: Annotated[
        tuple[int, int], 
        Field(
            description="Uma tupla contendo exatamente dois inteiros: o início e o fim do intervalo.",
            examples=[(1, 10)] # Adicionar um exemplo claro ajuda muito!
        )
    ] | None = None


class ObjectStorageLinkItem(BaseModel):
    url: AnyHttpUrl
    send_method: Literal['POST', 'GET', 'PUT', 'DELETE']
    expires_at: datetime


class UploadLinkResponse(UploadInfo):
    object_name: str
    upload_id: str | None = None
    current_part_count: int | None = None
    urls: list[ObjectStorageLinkItem]




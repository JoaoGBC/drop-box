from .minio import MinioStorageService






async def teste():
    a = MinioStorageService()
    await a.end_multipart_upload()
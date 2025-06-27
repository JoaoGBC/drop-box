import asyncio
from mypy_boto3_s3 import S3Client
from botocore.exceptions import ClientError
from .exceptions import UnexpectedPartCount

    
    

client_b3: S3Client

async def verify_part_count(
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
        client_b3.list_parts,
        Bucket= bucket_name,
        Key = file_name,
        UploadId= upload_id,
    )

    parts = parts.get('Parts')
    if len(parts) != expected_part_count:
        raise UnexpectedPartCount()

    return True

async def _end_multipart_upload(
    upload_id: str,
    file_name: str,
    bucket_name: str,
) -> None:
    try:
        await asyncio.to_thread(
            client_b3.complete_multipart_upload,
            Bucket= bucket_name,
            Key=file_name,
            UploadId=upload_id
        )
    except ClientError as e:
        raise e


async def end_multipart_upload(
    upload_id: str,
    file_name: str,
    bucket_name: str,
    current_part_count: int | None,
    verify_parts: bool = True,
) -> None:
    '''
    Finaliza um upload multipart. Caso a flag 'verify_parts' esteja ativa,
    compara o numero de partes com o numero de partes esperado 
    `current_part_count` e caso sejam diferentes,
    levanta `UnexpectedPartCount`.

    :param str upload_id: id do multipart upload referente às partes.
    :param str file_name: key referente do upload.
    :param str bucket_name: Nome do bucket onde irá verificar as partes.
    :param int verity_parts: O numero de partes que se espera que existam.
    :param bool current_part_count: Se o numero de partes deve ser verificado.

    :returns None: None

    :raises UnexpectedPartCount: Caso o numero de partes não seja o esperado.
    '''

    if verify_parts:
        await verify_part_count(
            bucket_name=bucket_name,
            file_name=file_name,
            expected_part_count=current_part_count,
            upload_id=upload_id,
        )
    
    await _end_multipart_upload(
        upload_id=upload_id,
        file_name=file_name,
        bucket_name=bucket_name
    )
    
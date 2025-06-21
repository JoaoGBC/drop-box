# services.pyi

from typing import TypedDict, Literal, overload, Coroutine, Any
from datetime import datetime
from botocore.exceptions import ClientError
from mypy_boto3_s3.client import S3Client

# --- Tipos de Dados (Data Contracts) ---

class ObjectStorageLinkDict(TypedDict):
    """Representa uma única URL pré-assinada com seus metadados."""
    part_number: int | None # None para single-part
    url: str
    send_method: Literal['PUT']
    expires_at: datetime

class SinglepartUploadLinksDict(TypedDict):
    """Representa a resposta para um upload de parte única."""
    object_name: str
    urls: list[ObjectStorageLinkDict]

class MultipartUploadLinksDict(TypedDict):
    """Representa a resposta para um upload de múltiplas partes."""
    upload_id: str
    object_name: str
    urls: list[ObjectStorageLinkDict]


# --- Variáveis Públicas ---

client_b3: S3Client

# --- Funções Públicas ---

async def object_in_bucket(file_name: str, bucket_name: str) -> bool:
    '''Verify if a file exits in an S3/s3-compatible-service bucket

    :param file_name: File to verify existence
    :param bucket: Bucket to verify file existence
    :return: True if file exists, else False
    :raises: botocore.exception.ClientError for client errors
    '''
    ...



async def generate_multipart_upload_urls(
    *,
    file_name: str,
    bucket_name: str,
    part_range: tuple[int, int],
    content_type: str,
    upload_id: str | None = None,
    duration_seconds: int = 3600
) -> MultipartUploadLinksDict:
    """ Função de alto nivel para iniciar uploads multipart via urls 
    pre-asinadas. Se um upload_id é informado, apenas as urls são geradas,
    caso contrario, o upload-multipart será aberto e as urls serão geradas.

    :param upload_id `str`:  Id do upload multipart para qual as urls serão geradas
    :param file_name `str`: Nome do objeto a ser salvo no bucket.
    :param bucket_name `str`: Bucket onde o objeto será salvo.
    :param part_count `int`: Número de partes em que o arquivo será dividido.
    :param duration_seconds `int`: Duração em segundos da validade das URLs.
    
    :raises botocore.exceptions.ClientError: Para erros de cliente do Boto3.
    
    :return `MultipartUploadLinksDict`: Um dicionário contendo os dados para o cliente iniciar o upload,
             com a seguinte estrutura:
             
             - **upload_id** (str): O ID único para este upload multipart.
             - **object_name** (str): O nome final do objeto no bucket.
             - **urls** (list[dict]): Uma lista de dicionários, um para cada parte.
    :rtype: dict
    """
    ...

async def generate_singlepart_upload_url(
    *,
    file_name: str,
    bucket_name: str,
    duration_seconds: int
) -> SinglepartUploadLinksDict:
    """ Função para iniciar uploads singlepart via urls 
    pre-asinadas. 

    :param file_name `str`: Nome do objeto a ser salvo no bucket.
    :param bucket_name `str`: Bucket onde o objeto será salvo.
    :param duration_seconds `int`: Duração em segundos da validade das URLs.
    
    :return `SinglepartUploadLinksDict`: Um dicionário contendo os dados para o cliente iniciar o upload,
             com a seguinte estrutura:

    :rtype: dict
    """
    ...

# --- A Interface Pública Unificada com @overload ---

@overload
async def generate_presigned_urls(
    *,
    file_name: str,
    bucket_name: str,
    content_type: str,
    part_range: tuple[int, int],
    upload_id: str | None = None,
    overwrite_allowed: bool = False,
    duration_seconds: int = 3600
) -> MultipartUploadLinksDict:
    """
    **Multipart Upload**
    Gera URLs pré-assinadas para upload de objetos. 
    Gera urls para multiplas partes de acordo com o parametro part_range.
    É possivel reemitir urls especificando um range repetido,
    especificando (X, X) sendo X o numero da parte que se deseja reemitir a url.

    :param file_name `str`: Nome do objeto a ser salvo no bucket.
    :param bucket_name `str`: Bucket onde o objeto será salvo.
    :param part_range `tuple`: Tupla contendo o range de partes para as quais devem ser geradas/reemitidas as urls. O range é inclusivo tanto no inicio quanto fim, e deve conter exatamente 2 entidades.
    :upload_id `str`: id do upload multipart em caso de emisão de urls para novas partes ou reemissão de partes.
    :content_type `str`: mimetype do objeto/arquivo.
    :overwrite_allowed `bool`: se overwrites devem ser permitidos. Em caso de False levanta um erro UnauthorizedOverWriteAttempt.
    :param duration_seconds `int`: Duração em segundos da validade das URLs.
    :raises `UnauthorizedOverWriteAttempt`: Quando overwrite_allowed é False e o objeto já existe no bucket.
    :return `MultipartUploadLinksDict`: Um dicionário contendo os dados para o cliente iniciar o upload,
             com a seguinte estrutura:
             
    :rtype: dict
    """
    ...

@overload
async def generate_presigned_urls(
    *,
    file_name: str,
    bucket_name: str,
    content_type: None = None,
    overwrite_allowed: bool = False,
    duration_seconds: int = 3600
) -> SinglepartUploadLinksDict:
    """
    **Singlepart Upload**
    Gera URLs pré-assinadas para upload de objetos, 
    não inicia um multipart upload, não sendo possivel gerar urls
    para 'partes' do arquivo/objeto a ser enviado posterior à emissão da primeira url.
    
    :param file_name `str`: Nome do objeto a ser salvo no bucket.
    :param bucket_name `str`: Bucket onde o objeto será salvo.
    :content_type `str`: mimetype do objeto/arquivo.
    :overwrite_allowed `bool`: se overwrites devem ser permitidos. Em caso de False levanta um erro UnauthorizedOverWriteAttempt.
    :param duration_seconds `int`: Duração em segundos da validade das URLs.
    :raises `UnauthorizedOverWriteAttempt`: Quando overwrite_allowed é False e o objeto já existe no bucket.
    :return `SinglepartUploadLinksDict`: Um dicionário contendo os dados para o cliente iniciar o upload,
             com a seguinte estrutura:
             
             - **object_name** (str): O nome final do objeto no bucket.
             - **urls** (list[dict]): Uma lista de dicionários, um para cada parte.
    :rtype: dict
    """

async def generate_presigned_urls(
    *,
    file_name: str,
    bucket_name: str,
    part_range: tuple[int, int] | None = None,
    upload_id: str | None = None,
    content_type: str | None = None,
    overwrite_allowed: bool = False,
    duration_seconds: int = 3600
) -> SinglepartUploadLinksDict | MultipartUploadLinksDict:
    
    ...
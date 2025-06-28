from typing import Iterable, overload

from mypy_boto3_s3 import S3Client
from .types import MultipartUploadLinksDict, SinglepartUploadLinksDict

class MinioStorageService():
    def __init__(
        self,
        client: S3Client,
        url_duration_seconds: int
    ):
        ...
        
    async def generate_multipart_upload_urls(
        self,
        *,
        file_name: str,
        bucket_name: str,
        parts: Iterable[int],
        content_type: str,
        upload_id: str | None = None,
        duration_seconds: int = 3600
    ) -> MultipartUploadLinksDict:
        """ Função de alto nivel para iniciar uploads multipart via urls 
        pre-asinadas. Se um upload_id é informado, apenas as urls são geradas,
        caso contrario, o upload-multipart será aberto e as urls serão geradas.

        :param file_name `str`: Nome do objeto a ser salvo no bucket.
        :param bucket_name `str`: Bucket onde o objeto será salvo.
        :param parts `Iterable[int]`: Um iterable com o conjunto de partes que se quer gerar as urls.
        :param upload_id `str`:  Id do upload multipart para qual as urls serão geradas
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
        self,
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


    async def end_multipart_upload(
        self,
        *,
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

    @overload
    async def generate_presigned_urls(
        self,
        *,
        file_name: str,
        bucket_name: str,
        content_type: str,
        part: Iterable[int],
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
        :content_type `str`: mimetype do objeto/arquivo.
        :param parts `Iterable[int]`: Um iterable com o conjunto de partes que se quer gerar as urls.
        :param upload_id `str`: id do upload multipart em caso de emisão de urls para novas partes ou reemissão de partes.
        :param overwrite_allowed `bool`: se overwrites devem ser permitidos. Em caso de False levanta um erro UnauthorizedOverWriteAttempt.
        :param duration_seconds `int`: Duração em segundos da validade das URLs.
        :raises `UnauthorizedOverWriteAttempt`: Quando overwrite_allowed é False e o objeto já existe no bucket.
        :return `MultipartUploadLinksDict`: Um dicionário contendo os dados para o cliente iniciar o upload,
                com a seguinte estrutura:
                
        :rtype: dict
        """
    ...

    @overload
    async def generate_presigned_urls(
        self,
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
        ...
    async def generate_presigned_urls(
        self,
        *,
        file_name: str,
        bucket_name: str,
        parts: Iterable[int] | None = None,
        upload_id: str | None = None,
        content_type: str | None = None,
        overwrite_allowed: bool = False,
        duration_seconds: int = 3600
    ) -> SinglepartUploadLinksDict | MultipartUploadLinksDict:
        ...

    
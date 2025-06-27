class MinioBaseException(Exception):
    """Exceção base para todos os erros relacionados à integração com Minio."""
    pass


class UnauthorizedOverWriteAttempt(MinioBaseException):
    """
    Levantada ao tentar sobrescrever um objeto quando a proteção está ativa.
    """
    DEFAULT_MESSAGE = 'Object already exists and overwrite protection is enabled!'

    def __init__(self, message=None, bucket=None, object_name=None):
        self.bucket = bucket
        self.object_name = object_name
        
        # Se nenhuma mensagem específica for passada, usa a padrão.
        if message is None:
            message = self.DEFAULT_MESSAGE

        # Formata a mensagem para incluir os detalhes, se disponíveis
        if bucket and object_name:
            message = f"{message} (Bucket: '{bucket}', Object: '{object_name}')"

        super().__init__(message)

class UnexpectedPartCount(MinioBaseException):
    '''
    Levantada ao tentar finalizar um multipart upload conferindo o numero de 
    partes
    '''

    DEFAULT_MESSAGE = 'Expected parts quantity differs from parts on bucket!'

    def __init__ (
            self,
            message: str = None,
            bucket: str = None,
            upload_id: str = None,
            part_count: int = None,
            expected_part_count: int = None,
            key: str = None
        ):
        if message is None:
            message = self.DEFAULT_MESSAGE

        if bucket and upload_id and key:
            message = (
                f"{message} (Bucket: '{bucket}', 'upload_id':"
                f" {upload_id}, key: '{key}',"
                f" 'expected parts: '{expected_part_count}'"
                f" 'actual parts: '{part_count}"
            )
        
        super().__init__(message)

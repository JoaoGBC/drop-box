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
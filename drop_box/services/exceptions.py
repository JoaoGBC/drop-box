class UploadServiceBaseException(Exception):
    """Exceção base para todos os erros relacionados à integração com Minio."""
    pass


class UnauthorizedOverWriteAttempt(UploadServiceBaseException):
    """
    Levantada ao tentar sobrescrever um objeto quando a proteção está ativa.
    """
    DEFAULT_MESSAGE = 'Object already exists and overwrite protection is enabled!'

    def __init__(self, message=None):        
        # Se nenhuma mensagem específica for passada, usa a padrão.
        if message is None:
            message = self.DEFAULT_MESSAGE

        super().__init__(message)
        

class UnexpectedPartCount(UploadServiceBaseException):
    '''
    Levantada ao tentar finalizar um multipart upload conferindo o numero de 
    partes
    '''

    DEFAULT_MESSAGE = 'Expected parts quantity differs from parts on bucket!'

    def __init__ (
            self,
            message: str = None,            
        ):
        if message is None:
            message = self.DEFAULT_MESSAGE
        
        super().__init__(message)



class TypeNotAllowed(UploadServiceBaseException):
    '''
    Levantada ao tentar finalizar um multipart upload conferindo o numero de 
    partes
    '''

    DEFAULT_MESSAGE = 'Object/file type not allowed'

    def __init__ (
            self,
            message: str = None,            
        ):
        if message is None:
            message = self.DEFAULT_MESSAGE
        
        super().__init__(message)


class UnauthorizedUrlPartRequest(UploadServiceBaseException):
    '''
    Levantada ao tentar finalizar um multipart upload conferindo o numero de 
    partes
    '''

    DEFAULT_MESSAGE = 'A url for a part not authorized was requested'

    def __init__ (
            self,
            message: str = None,            
        ):
        if message is None:
            message = self.DEFAULT_MESSAGE
        
        super().__init__(message)
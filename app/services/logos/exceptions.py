from app.services.exceptions import ServiceException

class LogoServiceException(ServiceException):
    def __init__(self, message):
        super().__init__(message)

class InvalidContentTypeError(LogoServiceException):
    """ Exception for invalid logos content-type uploads """
    def __init__(self, content_type: str):
        super().__init__(f"Invalid content-type {content_type}")
        self.content_type = content_type

class InvalidLogoTypeError(LogoServiceException):
    def __init__(self, logo_type: str):
        """ Exception for unknown logo types """
        super().__init__(f"Unkown logo type {logo_type}")
        self.logo_type = logo_type

class LogoNotFoundError(LogoServiceException):
    def __init__(self, resource_id: str):
        """ Exception for resources without a logo """
        super().__init__(f"{resource_id} doesn't have a logo")
        self.resource_id = resource_id 
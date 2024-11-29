from app.services.exceptions import ServiceException


class FenixException(ServiceException):
    def __init__(self, message):
        super().__init__(message)

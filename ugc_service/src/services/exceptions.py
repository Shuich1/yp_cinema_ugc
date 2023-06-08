class ServiceException(Exception):
    ...


class ResourceDoesNotExist(ServiceException):
    ...


class ResourceAlreadyExists(ServiceException):
    ...

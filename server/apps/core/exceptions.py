from abc import abstractmethod


class BaseException(Exception):
    @abstractmethod
    def config(self):
        pass


class RequestValidationError(BaseException):
    def __init__(self, resource_name, errors):
        self.resource_name = resource_name
        self.errors = errors

    def config(self):
        return {
            'resource_name': self.resource_name,
            'errors': self.errors,
        }

    def __str__(self):
        return f"Request Validation for Resource: {self.resource_name}"


class ResourceNotFound(BaseException):
    def __init__(self, resource_name, errors):
        self.resource_name = resource_name
        self.errors = errors

    def config(self):
        return {
            'resource_name': self.resource_name,
            'errors': self.errors,
        }

    def __str__(self):
        return f"Request Not Found: {self.resource_name}"

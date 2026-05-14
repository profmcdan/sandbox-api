from rest_framework import status
from rest_framework.exceptions import APIException


class FeeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class RoutingException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class IrregularWalletException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PaymentStatusException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UnAuthorizedAccessException(APIException):
    """
    DRF-compatible exception that returns a structured APIResponse.
    """

    status_code = 401

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BadRequestException(APIException):
    """
    DRF-compatible exception that returns a structured APIResponse.
    """

    status_code = 400

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NotFoundException(APIException):
    """
    DRF-compatible exception that returns a structured APIResponse.
    """

    status_code = 404


# class PaymentStatusException(APIException):
#     status_code = status.HTTP_400_BAD_REQUEST

#     def __init__(self, message):
#         self.message = message
#         super().__init__(self.message)


class PermissionDeniedException(APIException):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

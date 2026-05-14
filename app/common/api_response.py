# common/utils/response.py


class ResponseBuilder:
    SUCCESS_CODE = "success"
    FAILURE_CODE = "failed"
    PENDING_CODE = "pending"
    UNCOMPLETED_CODE = "uncompleted"

    SUCCESS_STATUS = 200
    FAILURE_STATUS = 400
    UNAUTHORIZED_STATUS = 401
    NOT_FOUND_STATUS = 404

    @staticmethod
    def success(
        data: dict = None, message: str = "Success", status: int = None
    ) -> dict:
        return {
            "requestSuccessful": True,
            "responseCode": ResponseBuilder.SUCCESS_CODE,
            "responseMessage": message,
            "responseBody": data or {},
            "statusCode": status or ResponseBuilder.SUCCESS_STATUS,
        }

    @staticmethod
    def fail(
        message: str = "Failed", code: str = None, status: int = None, data: dict = None
    ) -> dict:
        return {
            "requestSuccessful": False,
            "responseCode": code or ResponseBuilder.FAILURE_CODE,
            "responseMessage": message,
            "responseBody": data or {},
            "statusCode": status or ResponseBuilder.FAILURE_STATUS,
        }

    @staticmethod
    def pending(
        message: str = "Pending", data: dict = None, status: int = None
    ) -> dict:
        return {
            "requestSuccessful": False,
            "responseCode": ResponseBuilder.PENDING_CODE,
            "responseMessage": message,
            "responseBody": data or {},
            "statusCode": status or ResponseBuilder.SUCCESS_STATUS,
        }

    @staticmethod
    def unauthorized(
        message: str = "UnAuthorize", data: dict = None, status: int = None
    ) -> dict:
        return {
            "requestSuccessful": False,
            "responseCode": ResponseBuilder.FAILURE_CODE,
            "responseMessage": message,
            "responseBody": data or {},
            "statusCode": status or ResponseBuilder.UNAUTHORIZED_STATUS,
        }

    @staticmethod
    def notfound(
        message: str = "Not found", data: dict = None, status: int = None
    ) -> dict:
        return {
            "requestSuccessful": False,
            "responseCode": ResponseBuilder.FAILURE_CODE,
            "responseMessage": message,
            "responseBody": data or {},
            "statusCode": status or ResponseBuilder.NOT_FOUND_STATUS,
        }

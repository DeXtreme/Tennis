from typing import TypeVar

import graphene
from django.core.exceptions import PermissionDenied, ValidationError

generic_data = TypeVar("generic_data")  # pylint: disable=C0103


class ResponseStatus(graphene.ObjectType):
    """
    Adds response status to the schema.
    """

    error_code = graphene.String(default_value="")
    status_code = graphene.Int(default_value=200)
    is_success = graphene.Boolean(default_value=True)

    @classmethod
    def success(cls, status_code=200):
        return cls(
            error_code="",
            status_code=status_code,
            is_success=True,
        )

    @classmethod
    def error(cls, error_code="ERROR_400", status_code=400):
        return cls(
            error_code=error_code,
            status_code=status_code,
            is_success=False,
        )


def _generic_response():
    from utils.common.generic_exception_response import generic_response

    return generic_response()


class QueryResponse(graphene.ObjectType):
    """
    Adds response errors, message and status and empty to the schema.
    """

    data = graphene.Field(generic_data, default_value=None)
    response_message = graphene.String(default_value="")
    response_status = graphene.Field(ResponseStatus)
    errors = graphene.List(graphene.String)

    @classmethod
    def response(
            cls, data=None, response_message="", response_status=None, errors=None
    ):
        return cls(
            data=data,
            response_message=response_message,
            response_status=response_status,
            errors=errors,
        )

    @classmethod
    def success(cls, data=None, response_message="Success", errors=None):
        return cls.response(
            data=data,
            response_message=response_message,
            response_status=ResponseStatus.success(),
            errors=errors,
        )

    @classmethod
    def error(
            cls,
            response_message: str = "An error occurred",
            error_code: str = "ERROR_400",
            status_code: int = 400,
            errors: list[str] = None,
            response_status=None,
    ):
        return cls.response(
            data=None,
            response_message=response_message,
            response_status=ResponseStatus.error(
                error_code=error_code or f"ERROR_{status_code}", status_code=status_code
            )
            if not response_status
            else response_status,
            errors=errors or [response_message],
        )

    @classmethod
    def error400(
            cls,
            response_message: str = "An error occurred",
            errors: list[str] = None,
    ):
        return cls.error(
            response_message=response_message,
            error_code="INVALID_QUERY_PARAMS",
            status_code=400,
            errors=errors,
        )

    @classmethod
    def error404(
            cls,
            response_message: str = "The referenced item was not found",
            errors: list[str] = None,
    ):
        return cls.error(
            response_message=response_message,
            error_code="NOT_FOUND",
            status_code=404,
            errors=errors,
        )

    @classmethod
    def error403(
            cls, error: PermissionError | PermissionDenied, errors_list: list[str] = None
    ):
        return cls.error(
            response_message=str(error),
            error_code="PERMISSION_DENIED",
            status_code=403,
            errors=errors_list or [str(error)],
        )

    @classmethod
    def error500(
            cls,
            response_message: str = None,
            errors: list[str] = None,
    ):
        return cls.error(
            response_message=response_message
            if response_message
            else _generic_response(),
            error_code="INTERNAL_SERVER_ERROR",
            status_code=500,
            errors=errors,
        )

    @classmethod
    def validation_error(cls, error: ValidationError, model_name: str = "record"):
        from utils.common import error_dict_to_list  # noqa
        from utils.common import prettify_validation_error  # noqa

        try:
            return cls.error(
                response_message=prettify_validation_error(error=error),
                error_code="INVALID_QUERY_PARAMETERS",
                errors=error_dict_to_list(error.message_dict),
            )
        except:
            return cls.error(
                response_message=error.message,
                error_code="INVALID_QUERY_PARAMETERS",
                errors=error.messages,
            )

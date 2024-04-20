from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist, FieldError
from django.db.models import ProtectedError
from inflect import engine

from utils.query_response import QueryResponse
from utils.common.format_string import list_to_string, snake_to_lower_spaced, format_class_name
from utils.logging import logger


def generic_mutation_404(
    item: str = None, action: str = "save"
) -> QueryResponse.error404:
    from utils import logger  # noqa

    """
    returns a QueryResponse error class, used when an object is not found or does not exist.
    ideally, an error should be reported to the admin. For now a warning log is thrown.
    * item refers to the model name.
    * action refers to the method or operation. example: Create, Update, Delete, etc.
    """
    logger.warning(f"a referenced {item} record was not found")
    return QueryResponse.error404(
        response_message=f"Could not {action.lower()} record. The referenced {item.lower()} was not found",
        errors=[f"{item.title()} not found"],
    )


def generic_response(item: str = None, action: str = None) -> str:
    """
    returns an error response message, preferably used in mutations.
    * item refers to the model name.
    * action refers to the method or operation. example: Create, Update, Delete, etc.
    """
    if not action and not item:
        return "An error occurred, kindly try again or contact support."
    if action and not item:
        return f"Could not {action.lower()}, kindly try again or contact support."

    return f"Could not {action.lower()} {item.title()}. Try again or contact support."


def generic_query_error_msg(name: str) -> str:
    """
    returns an error message: Could not fetch {name}.
    this is only applicable to queries!
    """
    return f"Could not fetch {name}"


def generic_403_msg(model_name: str = "item") -> str:
    return f"You do not have permission to modify this {model_name.lower()}"


def prettify_validation_error(
    error: ValidationError,
    model_name: str = None,  # todo: remove usages of model_name
) -> str:
    """
    Convert a validation error dict into a user-friendly string.
    """
    try:
        error_dict = dict(error)
        ret_str = ""
        if "__all__" in error_dict.keys():
            return str(error_dict.pop("__all__")[0])
            # ret_str = "The " + str(error_dict.pop('__all__')[0].lower())

        if len(error_dict.keys()) > 0:
            return str(list(error_dict.values())[0][0])
            # return f"{ret_str}{list(error_dict.values())[0][0]}"

            # invalid_fields = [snake_to_camel(item) for item in error_dict.keys()]
            # return f"Could not save {format_class_name(model_name)} with invalid {list_to_string(invalid_fields)}."
    except:
        return error.message


def refine_complex_errors_list(e) -> list | tuple | set:
    if not isinstance(e, Exception):
        if isinstance(e, list):
            return e
        return [e]
    e = list_to_string(e.args)
    if isinstance(e, list) or isinstance(e, tuple):
        return e
    return [e]


class DoesNotExist:
    pass


class AlreadyExists(Exception):
    """Raised when an item is already present in a superset/parent obj"""


class InheritedError(Exception):
    def __init__(self, message: str, errors: list, status_code: int = None):
        super().__init__(errors if errors else message)
        self.response_message = message
        self.errors = errors
        self.status_code = status_code

    def mutation_error(self):
        if self.status_code == 404:
            return QueryResponse.error404(
                response_message=self.response_message, errors=self.errors
            )
        if 400 <= self.status_code < 500:
            return QueryResponse.error(
                response_message=self.response_message, errors=self.errors
            )
        return QueryResponse.error500(
            response_message=generic_response(), errors=self.errors
        )


class NotFoundError(Exception):
    def __init__(self, field_name: str, field_value: list):
        super().__init__()
        self.field_name = field_name
        self.field_value = field_value

    def mutation_error(self):
        return QueryResponse.error404(
            response_message=f"The referenced {snake_to_lower_spaced(self.field_name)} could not be found."
        )


class InvalidToken(Exception):
    """Raised when an authorization token is invalid"""

    @classmethod
    def error401(cls, response_message="Token expired or invalid"):
        return QueryResponse.error(
            error_code="INVALID_TOKEN",
            response_message=response_message,
        )


class ExceptionHandlers:
    def query(func, *args, **kwargs):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PermissionDenied as e:
                return QueryResponse.error403(e)
            except FieldError:
                return QueryResponse.error400(errors=["Invalid Parameters Provided"])
            except PermissionError as e:
                return QueryResponse.error403(e)
            except:
                logger.exception("Query error")
                return QueryResponse.error500()

        return wrapper

    def mutation(model_name="item"):
        def model_name_wrapper(func, *args, **kwargs):
            from utils.common import error_dict_to_list  # noqa
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except PermissionDenied as e:
                    return QueryResponse.error403(e)
                except PermissionError as e:
                    return QueryResponse.error403(e)
                except ObjectDoesNotExist:
                    return QueryResponse.error404(response_message=f"{model_name} instance was not found")
                except AlreadyExists:
                    return QueryResponse.error(
                        response_message="Record already exists, consider updating instead.",
                        errors=error_dict_to_list({"__all__": ["This record already exists"]}),
                    )
                except ProtectedError as e:
                    p = engine()
                    protected_objects = [
                        f"{format_class_name(i._meta.model_name)}: {str(i).lower()}"
                        for i in e.protected_objects
                    ]
                    msg = f"A dependency on this record does not allow deletion. First, remove the related {p.join(protected_objects)}"
                    return QueryResponse.error403(msg)
                except InheritedError as e:
                    return e.mutation_error()
                except ValidationError as e:
                    return QueryResponse.validation_error(e)
                except ValueError:
                    logger.exception(f"Invalid Value")
                    return QueryResponse.error500()
                except:
                    logger.exception("Mutation Error")
                    return QueryResponse.error500()
            return wrapper
        return model_name_wrapper

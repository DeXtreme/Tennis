from django.core.exceptions import (
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ValidationError,
)
from utils.common import pascal_case_to_uppercase_with_underscore as pascal_to_uppercase
from utils.common.format_string import pascal_to_title_spaces


def retrieve_object_by_id(model, **kwargs):
    """
    Retrieve an object by id.

    :param model: The model to retrieve the object from.
    :param kwargs: dict containing the id of the object to retrieve and any other query parameters.
    :return: A dictionary containing the object, response message, response status, and errors.
    """
    spaced_name = pascal_to_title_spaces(model.__name__)
    item_name = model.__name__.capitalize()
    try:
        obj = model.objects.get(**kwargs)
    except ObjectDoesNotExist:
        return {
            "data": None,
            "response_message": f"{spaced_name} not found.",
            "response_status": {
                "status_code": 404,
                "is_success": False,
                "error_code": f"{pascal_to_uppercase(item_name)}_NOT_FOUND",
            },
            "errors": [f"{spaced_name} not found."],
        }
    except MultipleObjectsReturned:
        return {
            "data": None,
            "response_message": "Multiple objects found.",
            "response_status": {
                "status_code": 409,
                "is_success": False,
                "error_code": "MULTIPLE_OBJECTS_FOUND",
            },
            "errors": ["Multiple objects found."],
        }
    except (ValidationError, TypeError, ValueError):
        return {
            "data": None,
            "response_message": "Invalid query parameters.",
            "response_status": {
                "status_code": 400,
                "is_success": False,
                "error_code": "INVALID_QUERY_PARAMETERS",
            },
            "errors": ["Invalid query parameters."],
        }

    return {
        "response_message": f"{spaced_name} found.",
        "response_status": {"status_code": 200, "is_success": True},
        "data": obj,
        "errors": None,
    }

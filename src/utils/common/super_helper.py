from utils.common.generic_exception_response import InheritedError


def mutate(mutation, get_data=True, **kwargs):
    result = mutation(**kwargs)

    if result.response_status.status_code != 200:
        raise InheritedError(
            message=result.response_message,
            errors=result.errors,
            status_code=result.response_status.status_code,
        )
    if not get_data:
        return result
    return result.data

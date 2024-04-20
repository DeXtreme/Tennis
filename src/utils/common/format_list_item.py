from typing import Union

from graphql.pyutils import snake_to_camel


def format_list_item(key: str, value: Union[str, dict]) -> str:
    """
    Format a dictionary key-value pair as a string item for the list.
    """
    if isinstance(value, str) and value.startswith("This field"):
        return f"{key} {value[10:].strip()}"

    return f"{key}: {value}"


def error_dict_to_list(dictionary: dict) -> list:
    """
    Convert a dictionary to a list of strings.
    """
    result = []
    for key, value in dictionary.items():
        key = snake_to_camel(key.strip()) if key != "__all__" else key

        if isinstance(value, dict):
            result.append(f"{key}: {', '.join(error_dict_to_list(value))}")
        elif isinstance(value, list):
            for item in value:
                result.append(format_list_item(key, item))
        else:
            result.append(format_list_item(key, value))
    return result

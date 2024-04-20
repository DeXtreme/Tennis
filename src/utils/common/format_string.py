import re


def strip_and_title_case(field: str) -> str:
    if not isinstance(field, str):
        return field
    words_to_lowercase = ("of", "and", "is", "or", "for", "in")
    field = field.strip()
    field = field.title()
    for word in words_to_lowercase:
        field = field.replace(word.title(), word.lower())
    return field


def camel_to_snake_case(camel_case):
    snake_case = re.sub('([A-Z])', '_\\1', camel_case).lower()
    if snake_case.startswith('_'):
        snake_case = snake_case[1:]
    return snake_case


def snake_to_lower_spaced(snake_case: str) -> str:
    spaced_string = snake_case.replace("_", " ")
    return spaced_string.lower()


def space_to_snake_case(string: str) -> str:
    return string.replace(" ", "_").lower()


def upper_to_title_case(string: str) -> str:
    words = string.split("_")
    title_case = " ".join(word.capitalize() for word in words)
    return title_case


def pascal_case_to_uppercase_with_underscore(name: str) -> str:
    """
    Convert PascalCase to UPPERCASE_WITH_UNDERSCORE.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()


def pascal_to_title_spaces(string: str) -> str:
    """
    Convert PascalCase to Titled Words With Spaces
    """
    converted_string = ""
    for char in string:
        if char.isupper() and converted_string != "":
            converted_string += " " + char
        else:
            converted_string += char
    return converted_string


def format_class_name(string: str) -> str:
    """
    Convert a string representation of a django model to a lowercase string with spaces between words.
    """
    return " ".join(re.findall("[a-zA-Z][^A-Z]*", string)).lower()


def list_to_string(the_list: list | tuple) -> str:
    """
    convert a list into a string with 'and' before the last item.
    """
    if len(the_list) == 0:
        return ""
    if len(the_list) == 1:
        return the_list[0]
    if len(the_list) == 2:
        return " and ".join(the_list)

    return ", ".join(the_list[:-1]) + ", and " + the_list[-1]

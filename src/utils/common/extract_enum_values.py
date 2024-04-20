import enum


def extract_enum_values(instance):
    values = {}

    for key, value in instance.__dict__.items():
        if isinstance(value, enum.Enum):
            values[key] = value.name
    return values

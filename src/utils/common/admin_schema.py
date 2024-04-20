equipment_schema = {
    "type": "dict",
    "keys": {
        "type": {"type": "string"},
        "brand": {"type": "string"},
        "color": {"type": "string"},
        "height": {"type": "integer"},
        "weight": {"type": "integer"},
        "width": {"type": "integer"},
    },
}

group_capacity_schema = {
    "type": "dict",
    "keys": {"min": {"type": "integer"}, "max": {"type": "integer"}},
}

duration_schema = {
    "type": "dict",
    "keys": {
        "hour": {"type": "integer", "maximum": 24, "minimum": 0},
        "minute": {"type": "integer", "maximum": 60, "minimum": 0},
    },
}
list_schema = {
    "type": "array",
    "items": {
        "type": "string",
    },
}

place_type_schema = {
    "type": "array",
    "items": {
        "type": "string",
        "choices": ["Sports", "Wellness", "Health"],
    },
    "maxItems": 3,
}

service_type_schema = {
    "type": "array",
    "items": {
        "type": "string",
        "choices": ["EVENT", "PROGRAM", "BOOTCAMP", "CONSULTATION"],
    },
    "maxItems": 4,
}

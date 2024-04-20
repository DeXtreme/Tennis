import pendulum
from django.db.models import Q  # noqa

from utils.abstract.schema.query_response import QueryResponse
from utils.common.format_string import camel_to_snake_case


def get_search_result(queryset, search_text: str, filters: list[str]):
    filter_types = {
        "^": "istartswith",
        "=": "iexact",
        "@": "search",
    }
    query_str = ""
    for i in filters:
        query_str += f"\nQ({i}__{filter_types.get(i[0], 'icontains')}=search_text) |"
    query_str = query_str[1:-1]
    result = eval(f"queryset.filter({query_str})")
    return result


def filter_by_datetime_range(queryset, date_range: dict, field: str = 'date_created'):
    if date_range.get('start') and date_range.get('end') and date_range['start'] > date_range['end']:
        return QueryResponse.error400("start date must be less/earlier than end date")
    filers = {}
    if date_range.get('start'):
        filers[f"{field}__gte"] = pendulum.parse(date_range['start'].isoformat())
    if date_range.get('end'):
        filers[f"{field}__lte"] = pendulum.parse(date_range['end'].isoformat())
    return queryset.filter(**filers)


def refine_sort_keys(fields, key_map: dict = None):
    if not fields:
        return ["-date_created"]
    fields = [camel_to_snake_case(i) for i in fields]
    if not key_map:
        return fields
    mapped_keys = key_map.keys()
    for i in range(len(fields)):
        key = fields[i]
        if key in mapped_keys:
            fields[i] = key_map[key]
    return fields

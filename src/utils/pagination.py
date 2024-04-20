from typing import List, Dict, Any

from django.core.paginator import EmptyPage, Paginator
from django.db.models import QuerySet, Model
from graphene import Int

from utils.query_response import QueryResponse, ResponseStatus


class PaginatedModelList(QueryResponse):
    data = None
    next_page = Int()
    previous_page = Int()
    page_count = Int()
    total_records = Int()
    errors = None
    response_message = ""
    response_status = ResponseStatus.success()

    @classmethod
    def from_queryset(
        cls, queryset: QuerySet[Model], per_page: int, page: int
    ) -> "PaginatedModelList":
        if not per_page and per_page != 0:
            per_page = 10
        if not page:
            page = 1

        if per_page == 0:
            per_page = len(queryset) if len(queryset) > 0 else 1
            page = 1
        paginator = Paginator(queryset, per_page)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            data = []
            next_page = None
            previous_page = None
        else:
            data = list(page_obj.object_list)
            next_page = page_obj.next_page_number() if page_obj.has_next() else None
            previous_page = (
                page_obj.previous_page_number() if page_obj.has_previous() else None  # noqa: E501
            )
        page_count = paginator.num_pages
        total_records = paginator.count
        response_message = f"{total_records if total_records >= 1 else 'No'} record{'s' if total_records > 1 else ''} Found."
        return cls(
            data=data,
            next_page=next_page,
            previous_page=previous_page,
            page_count=page_count,
            total_records=total_records,
            response_status=cls.response_status,
            response_message=response_message,
            errors=cls.errors,
        )

    @classmethod
    def from_dict_queryset(
        cls, queryset: List[Dict[str, Any]], per_page: int, page: int
    ) -> "PaginatedModelList":
        if not per_page and per_page != 0:
            per_page = 10
        if not page:
            page = 1

        # try:
        if per_page == 0:
            per_page = len(queryset) if len(queryset) > 0 else 1
            page = 1
        paginator = Paginator(queryset, per_page)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            data = []
            next_page = None
            previous_page = None
        else:
            data = list(page_obj.object_list)
            next_page = page_obj.next_page_number() if page_obj.has_next() else None
            previous_page = (
                page_obj.previous_page_number() if page_obj.has_previous() else None  # noqa: E501
            )
        page_count = paginator.num_pages
        total_records = paginator.count
        response_message = f"{total_records if total_records >= 1 else 'No'} record{'s' if total_records > 1 else ''} Found."
        return cls(
            data=data,
            next_page=next_page,
            previous_page=previous_page,
            page_count=page_count,
            total_records=total_records,
            response_message=response_message,
            response_status=cls.response_status,
            errors=cls.errors,
        )

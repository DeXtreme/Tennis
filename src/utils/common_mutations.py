from enum import Enum
from typing import Tuple, List, Type

import inflect
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from django.db.models import Model, ProtectedError
from graphene import Mutation, Field, String, Int, Boolean
from graphql.pyutils import snake_to_camel

from utils.logging import logger
from utils.query_response import QueryResponse, ResponseStatus
from utils.common import format_class_name
from utils.common.format_list_item import error_dict_to_list
from utils.common.format_string import snake_to_lower_spaced
from utils.common.generic_exception_response import (
    generic_response,
    NotFoundError,
    AlreadyExists, ExceptionHandlers,
)
from utils.common.generic_exception_response import prettify_validation_error
from utils.post_save_mutation_registry import PostSaveMutationRegistry


def _handle_pricing(payload) -> None:
    """
    * check for individual_price and group_price fields in payload
    * convert those fields from cedis to pesewas (dollars to cents)
    """
    if payload.get("individual_price"):
        payload["individual_price"] = int(
            round(payload.get("individual_price") * 100, 2)
        )
    if payload.get("group_price"):
        payload["group_price"] = int(round(payload.get("group_price") * 100, 2))


def _handle_related(fields_list, payload, relationship_type: str = None) -> None:
    """
    * Retrieve objects by ids to validate existence and parse related objects into payload.
    * Raises an ObjectDoesNotExist Exception when an object is not found.
    """
    if relationship_type:
        logger.debug(f"Pre {relationship_type}")
    if isinstance(fields_list, list):
        for field, related_model in fields_list:
            value = payload.get(field, 0)
            if value == 0:
                logger.debug(f"{field} not in payload")
                continue
            if value is None:
                logger.debug(f"{field} is None")
                continue
            pk = payload[field]
            try:
                payload[field] = related_model.objects.get(pk=pk)
            except ObjectDoesNotExist:
                raise NotFoundError(field, value)
            logger.debug(f"{field} processed")
    if relationship_type:
        logger.debug(f"Done {relationship_type}")


def _handle_m2m(fields_list, payload) -> dict:
    """
    * Retrieve objects by ids to validate existence.
    * pop value from payload.
    * add field and value to a dict that would be later used by the mutation to set/add the m2m keys
    * Raises an ObjectDoesNotExist Exception when an object is not found.
    """
    logger.debug("Pre M2M")
    m2m_values = {}
    if isinstance(fields_list, list):  # validate many-to-many fields
        for field, model in fields_list:
            value = payload.get(field, 0)
            if value == 0:
                logger.debug(f"{field} not in payload")
                continue
            if value is None:
                logger.debug(f"{field} is None")
                payload.pop(field)
                m2m_values[field] = []
                continue
            for pk in value:
                try:
                    model.objects.get(id=pk)
                except ObjectDoesNotExist:
                    raise NotFoundError(field, value)
            m2m_values[field] = payload.pop(field, None)
            logger.debug(f"{field} processed")
        logger.debug(f"m2m values: {m2m_values}")
        return m2m_values


def _set_m2m(cls, instance, m2m_values: dict, model_str: str = None):
    logger.debug("Before m2m handler")
    if isinstance(cls.m2m_fields, list):  # save many-to-many relations using .set()
        for field, model in cls.m2m_fields:
            value = m2m_values.get(field, None)
            if value is None:
                continue
            logger.debug(f"M2M field for {model_str or instance._meta.verbose_name} -> {field}: {value}")
            eval(f"instance.{field}.set(value)")
    logger.debug("Completed m2m handler")


def _handle_enum(fields_list, payload) -> None:
    """convert enums to strings"""
    if not isinstance(fields_list, list):
        return
    for field in fields_list:
        value = payload.get(field, None)
        if value is None:
            payload.pop(field, None)
            continue
        if isinstance(value, list):  # in case of a list of enums
            logger.debug(f"{field} is '{value} -> list'")
            payload[field] = [
                i.name if isinstance(i, Enum) else i for i in payload[field]
            ]
            continue
        if not isinstance(value, Enum):
            logger.debug(f"{field} is '{value}'")
            continue
        payload[field] = payload[field].name
        logger.debug(f"{field} processed")
    logger.debug(f"Post Enum processing")


def _handle_permissions(cls, **kwargs) -> None:
    """function to evaluate permissions"""
    logger.debug("Before Permission Handler")
    if not cls.permissions:
        return
    for i in cls.permissions:
        result = i
        if callable(i):
            result = i(**kwargs)
        if not result:
            raise PermissionDenied(f"You do not have permission to perform this action")
    logger.debug("Completed Permission Handler")


def _handle_post_save(instance, **kwargs) -> None:
    """function to run extra functions after saving"""

    logger.debug("Before Post Save")
    callables = PostSaveMutationRegistry.get_post_save_methods(
        instance._meta.model_name
    )
    if callables and not isinstance(callables, list):
        raise NotImplementedError(
            f"Post save handler expected a list but got {type(callables)}"
        )
    for function in callables:
        if not callable(function):
            return
        function(instance, **kwargs)
    logger.debug("Completed Post Save")


def _handle_bulk_post_save(queryset, **kwargs) -> None:
    """function to run extra functions after bulk saving"""

    logger.debug("Before Post Save")
    callables = PostSaveMutationRegistry.get_post_save_methods(
        queryset.model._meta.model_name
    )
    if callables and not isinstance(callables, list):
        raise NotImplementedError(
            f"Post save handler expected a list but got {type(callables)}"
        )
    for function in callables:
        if not callable(function):
            return
        function(queryset, **kwargs)
    logger.debug("Completed Post Save")


class BaseMutation(Mutation, QueryResponse):
    """
    * Base mutation class that contains common attributes and methods for Create and Update.
    * This abstraction is not suitable for models with more than 100 many-to-many fields.
    * Neither is it suitable for a model with a many-to-many field that may contain over 100 relations.
    This limitation is due to validation of the m2m fields and relations of those fields.
    """

    model: Type[Model] | Model = None
    enum_fields: list = None
    json_fields: list = None
    one_to_one_fields: List[Tuple[str, Model]] = None
    m2m_fields: List[Tuple[str, Model]] = None
    foreign_key_fields: List[Tuple[str, Model]] = None
    deprecated_fields: list = None
    permissions: list = None

    # output field
    data = None

    @classmethod
    def mutate(cls, root, info, id=None, payload=None, token=None):
        try:
            _handle_permissions(
                cls=cls,
                root=root,
                info=info,
                id=id,
                payload=payload,
                token=token,
            )
        except PermissionDenied as e:
            return cls.error403(e)
        except PermissionError as e:
            return cls.error403(e)
        except ObjectDoesNotExist as e:
            return cls.error404(str(e))
        except Exception as e:
            logger.critical(f"An error occurred when evaluating permissions - {e}")

        model_str = format_class_name(cls.model.__name__)
        try:
            if id:
                queryset = cls.model.objects.filter(id=id)
                if not queryset.exists():
                    logger.warning(f"{model_str} not found")
                    response_message = f"The referenced {model_str} could not be found."
                    return BaseMutation.error404(
                        response_message=response_message,
                        errors=[response_message],
                    )
                if queryset.count() > 1:
                    logger.critical(f"Multiple {model_str} found with the same id")
                    return BaseMutation.error500(
                        response_message=generic_response(
                            action="save", item=model_str
                        ),
                    )

            if isinstance(cls.deprecated_fields, list):  # pop deprecated fields
                for field in cls.deprecated_fields:
                    payload.pop(field) if field in payload.keys() else None
            if isinstance(cls.deprecated_fields, str):
                payload.pop(
                    cls.deprecated_fields
                ) if cls.deprecated_fields in payload.keys() else None

            _handle_pricing(payload)
            _handle_enum(cls.enum_fields, payload)
            _handle_related(cls.foreign_key_fields, payload, "FK")
            _handle_related(cls.one_to_one_fields, payload, "1-1")
            m2m_values = _handle_m2m(cls.m2m_fields, payload)

            logger.debug(f"Parse Complete - {payload}")
        except NotFoundError as e:
            logger.error(f"{e.field_name}, with value: {e.field_value} Does Not Exist")
            response_message = f"The referenced {snake_to_lower_spaced(e.field_name)} could not be found."
            return BaseMutation.error404(
                response_message=response_message,
                errors=[f"{snake_to_camel(e.field_name)}: Not found"],
            )
        except Exception as e:
            logger.exception(f"Exception {type(e)} -> {e}")
            return BaseMutation.error500(
                response_message=generic_response(action="save", item=model_str),
                errors=[],
            )
        try:
            if id is None:
                logger.debug(f"creating {model_str}")
                instance = cls.model.objects.create(**payload)
            else:
                logger.debug(f"updating {model_str}")
                instance = queryset.first()

                for key, value in payload.items():
                    if cls.json_fields and key in cls.json_fields and value is None:
                        continue
                    setattr(instance, key, value)
                logger.debug("instance unpacked")
                instance.full_clean()
                logger.debug("instance validated")
                instance.save()

            _set_m2m(
                cls=cls, m2m_values=m2m_values, model_str=model_str, instance=instance
            )
            _handle_post_save(
                root=root, info=info, instance=instance, created=False if id else True
            )
            return BaseMutation.success(
                response_message=f"{model_str.capitalize()} {'updated' if id else 'created'} successfully",
                data=instance,
            )
        except ObjectDoesNotExist:
            logger.exception("Object does not exist")
            return BaseMutation.error404(
                response_message=f"The referenced {model_str} does not exist.",
                errors=[f"The referenced {model_str} does not exist."],
            )
        except AlreadyExists:
            return cls.error(
                response_message="Record already exists, consider updating instead.",
                errors=error_dict_to_list({"__all__": ["This record already exists"]}),
            )
        except ValidationError as e:
            logger.exception(f"Validating {cls.model.__name__}: {e}")
            return BaseMutation.error(
                response_message=prettify_validation_error(
                    error=e, model_name=cls.model.__name__
                ),
                error_code="INVALID_QUERY_PARAMETERS",
                errors=error_dict_to_list(e.message_dict),
            )
        except ValueError as e:
            logger.exception(f"Invalid Value -> {e}")
            return BaseMutation.error500(
                response_message=generic_response(action="save", item=model_str),
                errors=[str(e)],
            )
        except Exception:
            logger.exception(f"An error occurred while mutating {cls.model.__name__}")
            return BaseMutation.error500(
                response_message=generic_response(action="save", item=model_str),
                errors=[],
            )


class Create(BaseMutation):
    """Create a new record."""


class Update(BaseMutation):
    """Update an existing record."""


class Delete(Mutation, QueryResponse):
    """Delete an existing record."""

    permissions: list = None
    model: Model = None
    soft_delete = False

    class Arguments:
        id = Int(required=True)
        token = String(required=True)

    data = None

    @classmethod
    def mutate(cls, root, info, id, token=None):
        try:
            _handle_permissions(
                cls=cls,
                root=root,
                info=info,
                id=id,
                token=token,
                has_permissions=cls.permissions,
            )
        except PermissionDenied as e:
            return cls.error403(e)
        except PermissionError as e:
            return cls.error403(e)
        except ObjectDoesNotExist as e:
            return cls.error404(str(e))
        except Exception as e:
            logger.critical(f"An error occurred when evaluating permissions - {e}")

        model_str = format_class_name(cls.model.__name__)
        try:
            model_object = cls.model.objects.get(id=id)
        except ObjectDoesNotExist:
            return Delete.error404(
                response_message=f"The requested {model_str} does not exist.",
                errors=[f"The requested {model_str} does not exist."],
            )
        else:
            try:
                if cls.soft_delete:
                    logger.warning(f"Soft deleting {model_str}")
                    model_object.soft_delete()
                else:
                    logger.warning(f"Hard deleting {model_str}")
                    model_object.delete()

                _handle_post_save(root=root, info=info, instance=model_object, deleted=True)
                return Delete.response(
                    response_message=f"{cls.model.__name__} Successfully Deleted",
                    response_status=ResponseStatus.success(status_code=204),
                )
            except PermissionDenied as e:
                logger.exception(f"Deleting {cls.model.__name__}: {e}")
                return BaseMutation.error(
                    response_message=str(e),
                    error_code="PERMISSION_DENIED",
                    errors=[str(e)],
                )
            except ProtectedError as e:
                p = inflect.engine()
                protected_objects = [
                    f"{format_class_name(i._meta.model_name)}: {str(i).lower()}"
                    for i in e.protected_objects
                ]
                msg = f"A dependency on this record does not allow deletion. First, remove the related {p.join(protected_objects)}"
                return BaseMutation.error(
                    response_message=msg,
                    error_code="PERMISSION_DENIED",
                    errors=[msg],
                )
            except Exception as e:
                logger.error(f"Could not delete {model_str}. {type(e)} -> {e}")
                response_msg = f"Could not delete the requested {model_str}. Try again or contact the administrator"
                return Delete.error500(
                    response_message=response_msg, errors=[response_msg]
                )


class BulkDelete(Mutation, QueryResponse):
    """Delete a batch existing records."""

    permissions: list = None
    model: Model = None
    soft_delete = False

    class Arguments:
        ids = Int(required=True)
        token = String(required=True)

    data = String()

    @classmethod
    def mutate(cls, root, info, ids, token=None):
        try:
            _handle_permissions(
                cls=cls,
                root=root,
                info=info,
                ids=ids,
                token=token,
                has_permissions=cls.permissions,
            )
        except PermissionDenied as e:
            return cls.error403(e)
        except PermissionError as e:
            return cls.error403(e)
        except ObjectDoesNotExist as e:
            return cls.error404(str(e))
        except Exception as e:
            logger.critical(f"An error occurred when evaluating permissions - {e}")

        model_str_plural = cls.model._meta.verbose_name_plural.lower()
        queryset = cls.model.objects.filter(pk__in=ids)
        if not queryset.exists():
            return cls.error404(
                response_message=f"The requested {model_str_plural} do not exist.",
                errors=[f"The requested {model_str_plural} do not exist."],
            )
        else:
            try:
                if cls.soft_delete:
                    logger.warning(f"Soft deleting {model_str_plural}")
                    queryset.update(deleted=True)
                else:
                    logger.warning(f"Hard deleting {model_str_plural}")
                    queryset.delete()

                _handle_bulk_post_save(root=root, info=info, queryset=queryset, deleted=True)
                return Delete.response(
                    response_message=f"{model_str_plural.title()} Successfully Deleted",
                    response_status=ResponseStatus.success(status_code=204),
                )
            except PermissionDenied as e:
                logger.exception(f"Failed to bulk delete {model_str_plural}")
                return BaseMutation.error(
                    response_message=str(e),
                    error_code="PERMISSION_DENIED",
                    errors=[str(e)],
                )
            except ProtectedError as e:
                # p = inflect.engine()
                # protected_objects = [
                #     f"{format_class_name(i._meta.model_name)}: {str(i).lower()}"
                #     for i in e.protected_objects
                # ]
                # msg = f"A dependency on this record does not allow deletion. First, remove the related {p.join(protected_objects)}"
                msg = f"A dependency on this record does not allow deletion. First, remove the related objects"
                return BaseMutation.error(
                    response_message=msg,
                    error_code="PERMISSION_DENIED",
                    errors=[msg],
                )
            except Exception as e:
                logger.error(f"Could not delete {model_str_plural}. {type(e)} -> {e}")
                response_msg = f"Could not delete the requested {model_str_plural}. Try again or contact the administrator"
                return Delete.error500(
                    response_message=response_msg, errors=[response_msg]
                )


def generate_m2m_mutations(
        model: Type[Model] | Model,
        related_model: Type[Model] | Model,
        field: str,
        primary_key_name: str = "primary_key",
        related_primary_key_name: str = "related_primary_key",
):
    class Add(Mutation, QueryResponse):
        class Arguments:
            primary_key = Int(required=True, name=snake_to_camel(primary_key_name))
            related_primary_key = Int(
                required=True, name=snake_to_camel(related_primary_key_name)
            )
            token = String(required=True)

        data = Boolean()

        @staticmethod
        def mutate(_, __, primary_key, related_primary_key, token=None):
            try:
                obj = model.objects.get(id=primary_key)
            except ObjectDoesNotExist:
                return Add.error404(
                    errors=[
                        f"The referenced {format_class_name(model.__name__)} does not exist."
                    ],
                    response_message=generic_response(),
                )
            try:
                related_obj = related_model.objects.get(id=related_primary_key)
            except ObjectDoesNotExist:
                return Add.error404(
                    errors=[
                        f"The referenced {format_class_name(related_model.__name__)} does not exist."
                    ],
                    response_message=generic_response(),
                )

            getattr(obj, field).add(related_obj)

            return Add.success(
                response_message=f"{field.capitalize()} added successfully",
            )

    class Remove(Mutation, QueryResponse):
        class Arguments:
            primary_key = Int(required=True, name=snake_to_camel(primary_key_name))
            related_primary_key = Int(
                required=True, name=snake_to_camel(related_primary_key_name)
            )
            token = String(required=True)

        data = Boolean()

        @staticmethod
        def mutate(_, __, primary_key, related_primary_key, token):
            try:
                obj = model.objects.get(id=primary_key)
            except ObjectDoesNotExist:
                return Remove.error404(
                    errors=[
                        f"The referenced {format_class_name(model.__name__)} does not exist."
                    ],
                    response_message=generic_response(),
                )

            try:
                related_obj = related_model.objects.get(id=related_primary_key)
            except ObjectDoesNotExist:
                return Remove.error404(
                    errors=[
                        f"The referenced {format_class_name(related_model.__name__)} does not exist."
                    ],
                    response_message=generic_response(),
                )

            getattr(obj, field).remove(related_primary_key)

            return Remove.success(
                response_message=f"{field.capitalize()} removed successfully.",
            )

    return Add, Remove



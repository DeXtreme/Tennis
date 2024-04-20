import graphene
from courts.models import Court
from courts.api.schema import CourtOutput, CourtListOutput

from utils.model_helpers import retrieve_object_by_id


class CourtQuery(graphene.ObjectType):
    get_court = graphene.Field(CourtOutput, id=graphene.Int(required=True))
    get_all_courts = graphene.Field(CourtListOutput,
                                    name=graphene.String(),
                                    location=graphene.String(),
                                    page=graphene.Int(),
                                    per_page=graphene.Int(),)

    def resolve_get_court(root, info, id):
        data = retrieve_object_by_id(model=Court, id=id)
        return CourtOutput.response(**data)

    def resolve_get_all_courts(root, info, name=None, location=None, page=None, per_page=None):
        queryset = Court.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        if location:
            queryset = queryset.filter(location__icontains=location)

        return CourtListOutput.from_queryset(queryset, per_page, page)

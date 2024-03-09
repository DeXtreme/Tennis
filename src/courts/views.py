from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin,RetrieveModelMixin
from drf_spectacular.utils import extend_schema

from . import models,serializers

class CourtsViewSet(GenericViewSet,
                    ListModelMixin,
                    RetrieveModelMixin):
    
    queryset = models.Court.objects.all()
    lookup_field = "court_id"


    def get_serializer_class(self):
        if self.action == "list":
            return serializers.CourtListSerializer
        else:
            return serializers.CourtSerializer


    @extend_schema(
        responses=serializers.CourtListSerializer,
        summary="List all courts",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

    @extend_schema(
        responses=serializers.CourtSerializer,
        summary="Retrieve court",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


import graphene

from graphql_jwt.decorators import login_required
from equipment.models import Equipment
from equipment.api.schema import EquipmentOutput, EquipmentListOutput

from utils.model_helpers import retrieve_object_by_id

class EquipmentQuery(graphene.ObjectType):
    get_equipment = graphene.Field(EquipmentOutput, id=graphene.Int(required=True))
    list_equipment = graphene.Field(EquipmentListOutput, page=graphene.Int(), per_page=graphene.Int())
    list_all_equipment = graphene.Field(EquipmentListOutput, page=graphene.Int(), per_page=graphene.Int())

    def resolve_get_equipment(root, info, id):
        data = retrieve_object_by_id(model=Equipment, id=id)
        return EquipmentOutput.response(**data)
    
    @login_required
    def resolve_list_equipment(root,info,page=None,per_page=None):
        account = info.context.user.account
        queryset = Equipment.objects.filter(users=account)
        return EquipmentListOutput.from_queryset(queryset,per_page,page)
    
    def resolve_list_all_equipment(root,info,page=None,per_page=None):
        queryset = Equipment.objects.all()
        return EquipmentListOutput.from_queryset(queryset,per_page,page)

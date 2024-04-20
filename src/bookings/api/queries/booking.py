import graphene
from graphql_jwt.decorators import login_required
from bookings.models import Booking
from bookings.api.schema import BookingOutput,BookingListOutput

from utils.model_helpers import retrieve_object_by_id

class BookingQuery(graphene.ObjectType):
    get_booking = graphene.Field(BookingOutput, id=graphene.Int(required=True))

    list_bookings = graphene.Field(BookingListOutput,
                                   page=graphene.Int(),
                                   per_page=graphene.Int())
    @login_required
    def resolve_get_booking(root, info, id):
        account = info.context.user.account
        data = retrieve_object_by_id(model=Booking, id=id, account=account)
        return BookingOutput.response(**data)
    
    @login_required
    def resolve_list_bookings(root,info,page=None, per_page=None):
        account = info.context.user.account
        queryset = Booking.objects.filter(account=account)
        return BookingListOutput.from_queryset(queryset,per_page,page)
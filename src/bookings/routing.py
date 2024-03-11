from django.urls import path
from . import consumers


urlpatterns = [
    path("", consumers.BookingsConsumer.as_asgi(), name="bookings-ws")
]
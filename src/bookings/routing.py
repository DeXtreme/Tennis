from django.urls import path
from . import consumers


urlpatterns = [
    path("ws/bookings", consumers.BookingsConsumer.as_asgi(), name="bookings-ws")
]
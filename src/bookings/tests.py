from datetime import time,timedelta
from django.utils import timezone
from django.urls import reverse
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator

from accounts.models import Account
from courts.models import Court

from . import models,consumers,routing


class BookingsConsumerTestCase(TransactionTestCase):
    
    @database_sync_to_async
    def setUpTestData(self):
        self.user = User.objects.create_user(username="test@email.com",
                                        password="Test_password1")
        self.account = Account.objects.create(user=self.user,
                                                    first_name="first",
                                                    last_name="last")
        
        self.court = Court.objects.create(name="Test court",
                                                location="Test location",
                                                open=time(8,0),
                                                close=time(16,0))

        self.booking = models.Booking.objects.create(court=self.court,
                                                    account=self.account,
                                                    start_time=timezone.now(),
                                                    end_time=timezone.now(),
                                                    duration=2)

        token = RefreshToken.for_user(self.user)
        self.access = str(token.access_token)

    async def setup(self):
        await self.setUpTestData()
        url = reverse("bookings-ws",routing)
        headers = {"Authorization": f"Bearer {self.access}"}
        self.communicator = WebsocketCommunicator(consumers.BookingsConsumer.as_asgi(), url, headers)
        self.communicator.scope["user"] = self.user
        result = await self.communicator.connect()
    
    
    async def test_subscribe(self):
        await self.setup()
        await self.communicator.send_json_to({
            "type":"sub",
            "court_id": str(self.court.court_id)
        })

        response = await self.communicator.receive_json_from()
        
        self.assertIn("status", response)
        self.assertEqual(response["status"], "success")

        
    async def test_unsubscribe(self):
        
        await self.setup()
        await self.communicator.send_json_to({
            "type":"unsub",
            "court_id": str(self.court.court_id)
        })

        response = await self.communicator.receive_json_from()
        self.assertIn("status", response)
        self.assertEqual(response["status"], "success")
    

    async def test_book(self):
        
        await self.setup()

        await self.communicator.send_json_to({
            "type":"sub",
            "court_id": str(self.court.court_id)
        })

        response = await self.communicator.receive_json_from()
        start_time = (timezone.now() + timedelta(days=1)).replace(hour=12)
        await self.communicator.send_json_to({
            "type":"book",
            "court_id": str(self.court.court_id),
            "start_time": str(start_time),
            "duration": 1
        })

        response = await self.communicator.receive_json_from()

        self.assertIn("status", response)
        self.assertEqual(response["status"], "success")

        response = await self.communicator.receive_json_from()

        self.assertIn("booked", response)
        self.assertIn("start_time", response["booked"])
        self.assertIn("end_time", response["booked"])
    
    async def test_cancel(self):

        await self.setup()

        await self.communicator.send_json_to({
            "type":"sub",
            "court_id": str(self.court.court_id)
        })

        response = await self.communicator.receive_json_from()

        await self.communicator.send_json_to({
            "type":"cancel",
            "booking_id": str(self.booking.booking_id),
        })

        response = await self.communicator.receive_json_from()

        self.assertIn("status", response)
        self.assertEqual(response["status"], "success")

        response = await self.communicator.receive_json_from()

        self.assertIn("cancelled", response)
        self.assertIn("start_time", response["cancelled"])
        self.assertIn("end_time", response["cancelled"])


    

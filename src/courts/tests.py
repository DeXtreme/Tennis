from django.urls import reverse
from datetime import time
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase


from accounts.models import Account
from bookings.models import Booking
from . import models


class CourtsViewSetTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(username="test@email.com",
                                        password="Test_password1")
        cls.account = Account.objects.create(user=cls.user,
                                                    first_name="first",
                                                    last_name="last")
        
        cls.court = models.Court.objects.create(name="Test court",
                                                location="Test location",
                                                open=time(8,0),
                                                close=time(16,0))

        cls.booking = Booking.objects.create(court=cls.court,
                                                    account=cls.account,
                                                    start_time=timezone.now(),
                                                    end_time=timezone.now(),
                                                    duration=2)

        token = RefreshToken.for_user(cls.user)
        cls.access = str(token.access_token)
    

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
    
    def test_list_court(self):
        url = reverse("courts:courts-list")
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(len(json), 1)
        
        court = json[0]

        self.assertIn("court_id",court)
        self.assertEqual(str(self.court.court_id),court["court_id"])
        self.assertIn("name",court)
        self.assertEqual(self.court.name,court["name"])
        self.assertIn("location",court)
        self.assertEqual(self.court.location,court["location"])
    

    def test_retrieve_court(self):

        url = reverse("courts:courts-detail", args=[self.court.court_id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        court = response.json()
        
        self.assertIn("court_id",court)
        self.assertEqual(str(self.court.court_id),court["court_id"])
        self.assertIn("name",court)
        self.assertEqual(self.court.name,court["name"])
        self.assertIn("location",court)
        self.assertEqual(self.court.location,court["location"])
        self.assertIn("open",court)
        self.assertEqual(str(self.court.open),court["open"])
        self.assertIn("close",court)
        self.assertEqual(str(self.court.close),court["close"])
        self.assertIn("booked",court)
        self.assertEqual(len(court["booked"]),1)

        booked = court["booked"][0]

        self.assertIn("start_time",booked)
        self.assertIn("end_time",booked)
     



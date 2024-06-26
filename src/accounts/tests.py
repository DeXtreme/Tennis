import json
from datetime import time
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from graphql_jwt.testcases import JSONWebTokenTestCase

from bookings.models import Booking
from courts.models import Court
from . import models


class AccountsTestCase(JSONWebTokenTestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(username="test@email.com",
                                            password="Test_password1")

        cls.account = models.Account.objects.create(user=cls.user,
                                                    first_name="first",
                                                    last_name="last")

        """
        cls.court = Court.objects.create(name="Test court",
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
        cls.refresh = str(token)
        """

    def test_register(self):
        query = """
            mutation Register($firstName:String!,
                              $lastName:String!,
                              $email:String!,
                              $password:String!){
                register(input:{
                            firstName:$firstName,
                            lastName:$lastName,
                            email:$email,
                            password:$password
                        }){
                    success
                    errors{
                        field
                        messages
                    }
                }
            }
        """

        with self.subTest("Valid details"):
            vars = {"firstName": "First",
                    "lastName": "Last",
                    "email": "test1@email.com",
                    "password": "Testpassword1"}

            response = self.client.execute(query, vars)

            self.assertIsNone(response.errors)
            self.assertIsNotNone(response.data["register"])
            self.assertIn("errors", response.data["register"])
            self.assertTrue(response.data["register"]["success"])

        with self.subTest("Invalid details"):

            vars = {"firstName": "",
                    "lastName": "",
                    "email": "test1",
                    "password": "passtest"}

            response = self.client.execute(query, vars)
            self.assertIsNone(response.errors)
            self.assertIsNotNone(response.data["register"])
            self.assertIn("errors", response.data["register"])
            self.assertFalse(response.data["register"]["success"])

    """
    def test_retrieve_token(self):
        url = reverse("accounts:accounts-token")

        data = {
            "email": "test@email.com",
            "password": "Test_password1"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()

        self.assertIn("access", json)
        self.assertIn("refresh", json)

    def test_refresh_token(self):
        url = reverse("accounts:accounts-refresh")

        data = {
            "refresh": self.refresh
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()

        self.assertIn("access", json)
        self.assertIn("refresh", json)

    def test_retrieve_account(self):
        url = reverse("accounts:accounts-detail",
                      args=[self.account.account_id])

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()

        self.assertIn("account_id", json)
        self.assertEqual(str(self.account.account_id), json["account_id"])
        self.assertIn("first_name", json)
        self.assertEqual(self.account.first_name, json["first_name"])
        self.assertIn("last_name", json)
        self.assertEqual(self.account.last_name, json["last_name"])
        self.assertIn("email", json)
        self.assertEqual(self.user.username, json["email"])

    
    def test_list_account_bookings(self):
        url = reverse("accounts:accounts-bookings-list",
                      args=[self.account.account_id])

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        booking = json[0]

        self.assertIn("booking_id", booking)
        self.assertEqual(str(self.booking.booking_id), booking["booking_id"])
        self.assertIn("court_name", booking)
        self.assertEqual(self.booking.court.name, booking["court_name"])
        self.assertIn("start_time", booking)
        self.assertIn("duration", booking)
        self.assertEqual(self.booking.duration, booking["duration"])
    """

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase

from . import models

class AccountViewSetTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(username="test@email.com",
                                        password="Test_password1")
        cls.account = models.Account.objects.create(user=cls.user,
                                                    first_name="first",
                                                    last_name="last")

        token = RefreshToken.for_user(cls.user)

        cls.access = str(token.access_token)
        cls.refresh = str(token)

    

    def test_create_account(self):
        url = reverse("accounts:accounts-list")

        data = {
            "email": "test@gmail.com",
            "first_name": "first",
            "last_name": "last",
            "password": "Test_password1"
        }

        response = self.client.post(url,data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_token(self):
        url = reverse("accounts:accounts-token")

        data = {
            "email": "test@email.com",
            "password": "Test_password1"
        }

        response = self.client.post(url,data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()

        self.assertIn("access", json)
        self.assertIn("refresh", json)

    
    def test_refresh_token(self):
        url = reverse("accounts:accounts-refresh")

        data = {
            "refresh": self.refresh
        }

        response = self.client.post(url,data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()

        self.assertIn("access", json)
        self.assertIn("refresh", json)
    
    def test_retrieve_account(self):
        url = reverse("accounts:accounts-detail", args=[self.account.account_id])

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

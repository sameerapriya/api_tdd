from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """Helper function to create user"""
    return get_user_model().objects.create_user(**params)


class PublicApiUsersTest(TestCase):
    """Tests for creating public users"""

    def setUp(self):
        self.client = APIClient()

    def test_public_user_create_successful(self):
        """Creation of user successful with the given details"""
        payload = {
            'email': 'xx@xx.com',
            'password': 'test123',
            'name': 'test',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test for user already exists"""
        payload = {
            'email': 'test@test.com',
            'password': 'test123'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test for password length to be more than 5 characters"""
        payload = {
            'email': 'xx@x.com',
            'password': 'pw'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test for successfully creating a token for the user"""
        payload = {
            'email': 'xx@x.com',
            'password': 'password123'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_for_token_invalid_credentials(self):
        """Test for token not generated if invalid credentials are provided"""
        create_user(email='test@test.com', password='pass123')
        payload = {
            'email': 'test@test.com',
            'password': 'blahblah'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_for_token_no_user(self):
        """Test for not creating a token if the user doesnt exist"""
        payload = {
            'email': 'test@test.com',
            'password': 'pass123'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_for_missing_fields(self):
        """Test for not creating token if the fields are not provided"""
        res = self.client.post(TOKEN_URL, {'email': 'test', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

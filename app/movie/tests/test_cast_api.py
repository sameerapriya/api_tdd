from rest_framework.test import APIClient
from rest_framework import status

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from movie.serializers import CastSerializer
from core.models import Cast

CAST_URL = reverse('movie:cast-list')


class PublicApiCastTests(TestCase):
    """Test for public cast objects"""
    def setUp(self):
        self.client = APIClient()

    def test_cast_get(self):
        """Test that login is required for this endpoint"""
        res = self.client.get(CAST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiCastTests(TestCase):
    """Tests for private Cast objects"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password123'
        )
        self.client.force_authenticate(self.user)

    def test_successful_retrieval(self):
        """Tests for checking casts can be viewed"""
        Cast.objects.create(user=self.user, name='Stephanie')
        Cast.objects.create(user=self.user, name='Rosa')

        res = self.client.get(CAST_URL)
        casts = Cast.objects.all().order_by('-name')
        serializer = CastSerializer(casts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_cast_limited_to_user(self):
        """Tests casts only for authenticated users"""
        user_1 = get_user_model().objects.create_user('test@other.com',
                                                      'testother1223')
        Cast.objects.create(user=user_1, name='Boyle')
        cast = Cast.objects.create(user=self.user, name='Jake')

        res = self.client.get(CAST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], cast.name)

    def test_create_cast(self):
        """Tests for creating valid cast"""
        payload = {
            'name': 'Raymond Holt'
        }
        self.client.post(CAST_URL, payload)
        exists = Cast.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_cast_invalid(self):
        """Tests for creating invalid cast"""
        payload = {
            'name': ''
        }
        res = self.client.post(CAST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

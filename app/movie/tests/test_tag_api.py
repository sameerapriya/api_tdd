from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from movie.serializers import TagSerializer
from core.models import Tag, Movie
import datetime

from rest_framework.test import APIClient
from rest_framework import status

TAG_URL = reverse('movie:tag-list')


class PublicApiTagTests(TestCase):
    """Tests for the Tag without user authentication"""
    def setUp(self):
        self.client = APIClient()

    def test_tag_get_unauthenticated(self):
        """Test that login is a must for retrieving the url """
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiTagTests(TestCase):
    """Tests for the tag after authentication"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_api_tags_get(self):
        """Test for user authenticated ,is able to view the tags."""
        Tag.objects.create(name='Comedy', user=self.user)
        Tag.objects.create(name='Drama', user=self.user)
        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_limited_authenticated_users(self):
        """Tests for making sure created tags are limited
         to authenticated users."""
        user_2 = get_user_model().objects.create_user(
            'test@tasty.com',
            'password567'
        )
        Tag.objects.create(name='Thriller', user=user_2)
        tag = Tag.objects.create(name='Horror', user=self.user)

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_tag_creation(self):
        """Test for valid tag creation"""
        payload = {
            'name': 'Test Name',
        }
        self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_invalid_tag(self):
        """Test for invalid tag creation"""
        payload = {'name': ''}
        res = self.client.post(TAG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_movie_assigned_tags_display(self):
        """Test for returning only assigned tags for the movie"""
        tag1 = Tag.objects.create(user=self.user, name='Drama')
        tag2 = Tag.objects.create(user=self.user, name='Romance')
        movie = Movie.objects.create(
            user=self.user,
            title='Desperate Housewives',
            duration=datetime.timedelta(minutes=40),
            price=5.99
        )
        movie.tag.add(tag1)
        res = self.client.get(TAG_URL, {'assigned_only': 1})
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertEqual(len(res.data), 1)

    def test_movie_assigned_tags_unique(self):
        """Tests for returning unique tags for different movie's assigned to"""
        tag1 = Tag.objects.create(user=self.user, name='Feel Good')
        movie_1 = Movie.objects.create(
            user=self.user,
            title='A walk to remember',
            duration=datetime.timedelta(hours=1, minutes=59),
            price=9.00
        )
        movie_1.tag.add(tag1)
        movie_2 = Movie.objects.create(
            user=self.user,
            title='Eternal sunshine of spotless mind',
            duration=datetime.timedelta(hours=2, minutes=5),
            price=18.00
        )
        movie_2.tag.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

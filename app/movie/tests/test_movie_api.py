from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Movie
from movie.serializers import MovieSerializer

import datetime


def sample_movie(user, **params):
    """Create and return a movie"""
    defaults = {
        'title': 'A Walk to Remember',
        'duration': datetime.timedelta(hours=2, minutes=15),
        'price': 8.99
    }

    defaults.update(params)
    return Movie.objects.create(user=user, **defaults)


MOVIE_URL = reverse('movie:movie-list')


class PublicApiMovieTests(TestCase):
    """Tests for public Movie objects"""
    def setUp(self):
        self.client = APIClient()

    def test_page_get(self):
        """Test for unauthorized access of page"""
        res = self.client.get(MOVIE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiMovieTests(TestCase):
    """Tests for private Movie Objects"""
    def setUp(self):
        self.user = get_user_model().objects.create_user('test@test.com',
                                                         'password123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_successful_retrieve(self):
        sample_movie(self.user)
        sample_movie(self.user)
        res = self.client.get(MOVIE_URL)
        movies = Movie.objects.all().order_by('-id')
        serializer = MovieSerializer(movies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_movies_limited_to_user(self):
        sample_movie(self.user)
        user_1 = get_user_model().objects.create_user(
            'hello@test.com',
            'hellotest123')
        sample_movie(user_1)
        res = self.client.get(MOVIE_URL)
        movies = Movie.objects.filter(user=self.user)
        serializer = MovieSerializer(movies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

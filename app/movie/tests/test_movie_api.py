import os
import tempfile
from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Movie, Tag, Cast
from movie.serializers import MovieSerializer, MovieDetailSerializer

import datetime
import decimal


def sample_tag(user, name='Comedy'):
    """Creates a sample Tag"""
    return Tag.objects.create(user=user, name=name)


def sample_cast(user, name='David'):
    """Creates a sample Cast"""
    return Cast.objects.create(user=user, name=name)


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


def detail_url(movie_id):
    """Return movie detail url"""
    return reverse('movie:movie-detail', args=[movie_id])


def image_upload_url(movie_id):
    """Returns an image upload URL"""
    return reverse('movie:movie-upload-image', args=[movie_id])


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
        """Tests for authorized access of page"""
        sample_movie(self.user)
        sample_movie(self.user)
        res = self.client.get(MOVIE_URL)
        movies = Movie.objects.all().order_by('-id')
        serializer = MovieSerializer(movies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_movies_limited_to_user(self):
        """Tests for movies access limited to the respective user."""
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

    def test_view_movie_detail(self):
        """Detail view of movies """
        movie = sample_movie(user=self.user)
        movie.tag.add(sample_tag(user=self.user))
        movie.cast.add(sample_cast(user=self.user))
        url = detail_url(movie.id)
        res = self.client.get(url)
        serializer = MovieDetailSerializer(movie)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_movie(self):
        """Test for creation of movie"""
        payload = {
            'title': 'Se7en',
            'duration': datetime.timedelta(hours=1, minutes=43),
            'price': decimal.Decimal('7.990')
        }
        res = self.client.post(MOVIE_URL, payload)
        movie = Movie.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(movie, key))

    def test_create_movie_tag(self):
        """Test for creation of movie with tags"""
        tag1 = sample_tag(user=self.user)
        tag2 = sample_tag(user=self.user, name='Drama')
        payload = {
            'title': 'House',
            'duration': datetime.timedelta(minutes=40),
            'price': 8.99,
            'tag': [tag1.id, tag2.id]
        }
        res = self.client.post(MOVIE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movie = Movie.objects.get(id=res.data['id'])
        tags = movie.tag.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_cast_tag(self):
        """Test for creation of movie with cast"""
        cast1 = sample_cast(user=self.user)
        cast2 = sample_cast(user=self.user, name='Dwayne')
        payload = {
            'title': 'FF7',
            'duration': datetime.timedelta(hours=2, minutes=4),
            'price': 10,
            'cast': [cast1.id, cast2.id]
        }
        res = self.client.post(MOVIE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movie = Movie.objects.get(id=res.data['id'])
        casts = movie.cast.all()
        self.assertEqual(casts.count(), 2)
        self.assertIn(cast1, casts)
        self.assertIn(cast2, casts)

    def test_patch_movie(self):
        movie = sample_movie(user=self.user)
        movie.tag.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Horror')
        payload = {
            'title': 'Baby Babyy',
            'tag': [new_tag.id]
        }
        url = detail_url(movie.id)
        res = self.client.patch(url, payload)
        movie.refresh_from_db()
        self.assertEqual(movie.title, payload['title'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tags = movie.tag.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_put_movie(self):
        movie = sample_movie(user=self.user)
        movie.tag.add(sample_tag(user=self.user))
        payload = {
            'title': 'BBT',
            'duration': datetime.timedelta(minutes=30),
            'price': decimal.Decimal('5.990')
        }
        url = detail_url(movie.id)
        res = self.client.put(url, payload)
        movie.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(movie.title, payload['title'])
        self.assertEqual(movie.duration, payload['duration'])
        self.assertEqual(movie.price, payload['price'])
        tags = movie.tag.all()
        self.assertEqual(len(tags), 0)


class PrivateImageUploadTests(TestCase):
    """Class for testing image uploading functionality"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test1@test.com', 'testhello'
        )
        self.client.force_authenticate(self.user)
        self.movie = sample_movie(user=self.user)

    def tearDown(self):
        self.movie.image.delete()

    def test_upload_image_movie(self):
        """Test for uploading an image to movie"""
        url = image_upload_url(self.movie.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.movie.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.movie.image.path))

    def test_upload_invalid_image(self):
        """Test for uploading an invalid image"""
        url = image_upload_url(self.movie.id)
        res = self.client.post(url, {'image': 'lol'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

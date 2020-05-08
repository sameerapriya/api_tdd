from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Tag


def sample_user(email='sam@yahoo.com', password='jhjnaa1122'):
    """Creates a sample user"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """Tests for the models"""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@test.com'
        password = 'Password123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_for_new_user_email_normalized(self):
        """Test the email for new user is normalized"""
        email = 'test@TEST.COM'
        user = get_user_model().objects.create_user(
            email,
            'test1223'
        )
        self.assertEqual(user.email, email.lower())

    def test_for_invalid_email(self):
        """Test for creating users with no email address raising errors"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test1223'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Testing the tag string model"""
        tag = Tag.objects.create(
            user=sample_user(),
            name='genre'
        )
        self.assertEqual(str(tag), tag.name)

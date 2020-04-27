from django.test import TestCase
from django.contrib.auth import get_user_model


# from model_mommy import mommy
# from model_mommy.recipe import Recipe


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

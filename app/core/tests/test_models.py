"""Test user model"""

from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_sucessful(self):
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.com", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "testpass123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("")

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            "test@example.com", "testpass123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe"""

        # cria usuário pra meter na receita
        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123",
        )

        title = "Sample recipe"

        recipe = models.Recipe.objects.create(
            user=user,
            title=title,
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description",
        )

        self.assertEqual(title, recipe.title)

    def test_create_tag(self):
        """Test creating a tag is sucessful"""
        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123",
        )
        nome_tag = "tag1"
        tag = models.Tag.objects.create(user=user, name=nome_tag)

        self.assertEqual(nome_tag, tag.name)

    def test_create_ingredient(self):
        """Test creating a tag is sucessful"""
        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123",
        )
        ingredient_name = "ingredient1"
        ingredient = models.Ingredient.objects.create(
            user=user,
            name=ingredient_name,
        )

        self.assertEqual(ingredient_name, ingredient.name)

    @patch("core.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Testgenerating image path"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "example.jpg")

        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")

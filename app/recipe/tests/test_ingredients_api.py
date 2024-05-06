"""Tests for the ingredients API"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse("recipe:ingredient-list")


def create_user(email="test@example.com", password="testpass123"):
    return get_user_model().objects.create_user(
        email,
        password,
    )


def detail_url(ingredient_id):
    """Create and return a recipe detail url"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


class PublicIngredientAPITests(TestCase):
    """Test unauthenticated tag API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_authorization_required(self):
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test authenticated tag API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_get_ingredients(self):
        Ingredient.objects.create(user=self.user, name="testIngredient")
        Ingredient.objects.create(user=self.user, name="testIngredient2")

        res = self.client.get(INGREDIENT_URL)

        ingredient = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_tags_only_for_user(self):
        """Test retrieving ingredients only for authenticated user"""
        other_user = create_user(email="user2@example.com", password="test123")
        Ingredient.objects.create(
            user=other_user,
            name="testIngredient another user",
        )

        Ingredient.objects.create(user=self.user, name="testIngredient")

        res = self.client.get(INGREDIENT_URL)

        ingredient = Ingredient.objects.filter(
            user=self.user,
        ).order_by("-name")
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_ingredient(self):
        """Test updating a tag"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="testIngredient",
        )

        payload = {"name": "ingrediente modificada"}

        res = self.client.patch(detail_url(ingredient.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Test deleting a ingredient"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="testIngredient",
        )

        res = self.client.delete(detail_url(ingredient.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Ingredient.objects.filter(user=self.user).exists())

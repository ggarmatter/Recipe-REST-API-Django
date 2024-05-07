"""Tests for the ingredients API"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

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

    def test_filter_ingredients_assigned_to_recipe(self):
        """Test listing ingredients by those assigned to recipes."""
        in1 = Ingredient.objects.create(user=self.user, name="Apples")
        in2 = Ingredient.objects.create(user=self.user, name="Orange")
        recipe = Recipe.objects.create(
            title="apple pie",
            time_minutes=5,
            price=Decimal("4.5"),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENT_URL, {"assigned_only": 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test that the filtered ingredients are unique"""
        ing = Ingredient.objects.create(user=self.user, name="Apples")
        Ingredient.objects.create(user=self.user, name="Oranges")

        recipe1 = Recipe.objects.create(
            title="apple pie",
            time_minutes=5,
            price=Decimal("4.5"),
            user=self.user,
        )

        recipe2 = Recipe.objects.create(
            title="orange pie",
            time_minutes=5,
            price=Decimal("4.5"),
            user=self.user,
        )

        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENT_URL, {"assigned_only": 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

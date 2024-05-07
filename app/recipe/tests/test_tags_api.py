"""Test the tags api"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


def create_user(email="test@example.com", password="testpass123"):
    return get_user_model().objects.create_user(
        email,
        password,
    )


def detail_url(tag_id):
    """Create and return a recipe detail url"""
    return reverse("recipe:tag-detail", args=[tag_id])


class PublicTagAPITests(TestCase):
    """Test unauthenticated tag API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_authorization_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """Test authenticated tag API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""
        Tag.objects.create(user=self.user, name="testTag")
        Tag.objects.create(user=self.user, name="testTag2")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_tags_only_for_user(self):
        """Test retrieving tags only for authenticated user"""
        other_user = create_user(email="user2@example.com", password="test123")
        Tag.objects.create(user=other_user, name="testTag another user")

        Tag.objects.create(user=self.user, name="testTag")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user).order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name="testTag")

        payload = {"name": "tag modificada"}

        res = self.client.patch(detail_url(tag.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name="testTag")

        res = self.client.delete(detail_url(tag.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Tag.objects.filter(user=self.user).exists())

    def test_filter_tags_assigned_to_recipe(self):
        """Test listing tags by those assigned to recipes."""
        tag1 = Tag.objects.create(
            user=self.user,
            name="tag1",
        )
        tag2 = Tag.objects.create(
            user=self.user,
            name="tag2",
        )

        recipe = Recipe.objects.create(
            title="apple pie",
            time_minutes=5,
            price=Decimal("4.5"),
            user=self.user,
        )

        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test that the filtered tags are unique"""
        tag1 = Tag.objects.create(
            user=self.user,
            name="tag1",
        )
        Tag.objects.create(
            user=self.user,
            name="tag2",
        )

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

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

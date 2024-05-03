"""Test the tags api"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


def create_user(email="test@example.com", password="testpass123"):
    return get_user_model().objects.create_user(
        email,
        password,
    )


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

"""Views for the receipe api"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API"""

    # serializer converte os dados do model (database)
    # para objetos python que podem ser usados para view
    serializer_class = serializers.RecipeDetailSerializer
    # diz quais objetos serão acessíveis por essa view
    queryset = Recipe.objects.all()
    # autenticacao
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes forauthenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == "list":
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """View para as tags"""

    serializer_class = serializers.Tag
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve tags for the authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-name")

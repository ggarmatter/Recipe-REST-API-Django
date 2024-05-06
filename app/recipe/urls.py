"""Url mappings for the recipe app"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter
from recipe import views

# aqui serve pra dar reverse lookup na url
app_name = "recipe"

router = DefaultRouter()
router.register("recipes", views.RecipeViewSet)
router.register("tags", views.TagViewSet)
router.register("ingredients", views.IngredientViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

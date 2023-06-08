from django.urls import include, path
from rest_framework import routers
from .views import (
   IngredientViewSet, TagViewSet, RecipeViewSet,
   FavoritesViewSet, ShoppingCartViewSet
)


router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(
   r'recipes(?P<recipes_id>\d+)/favorite',
   FavoritesViewSet,
   basename='favorite'
)
router.register(
   r'recipes(?P<recipes_id>\d+)/shopping_cart',
   ShoppingCartViewSet,
   basename='shopping_cart'
)


urlpatterns = [
   path('', include(router.urls)),
]

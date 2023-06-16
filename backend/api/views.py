from rest_framework import filters, permissions, viewsets, status
from .filters import RecipeFilter
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (
    FavoriteSerializer, IngredientSerializer, ShoppingCartSerializer,
    TagSerializer, RecipeReadSerializer, RecipeСreateSerializer
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminReadOnly
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингрердиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""
    queryset = Tag.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeСreateSerializer
    permission_classes = [IsAuthorOrAdminReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeСreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                recipe,
                request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                recipe,
                request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            shopping_cart = get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=recipe
            )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

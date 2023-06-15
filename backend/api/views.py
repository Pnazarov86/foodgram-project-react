from rest_framework import filters, permissions, viewsets
from .filters import RecipeFilter
from recipes.models import (Ingredient, Recipe, Tag)
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeСreateSerializer,
    RecipeReadSerializer
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminReadOnly
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет ингрердиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class TagViewSet(viewsets.ModelViewSet):
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

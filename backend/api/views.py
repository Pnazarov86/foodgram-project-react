from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeMiniSerializer,
    RecipeReadSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингрердиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def create_or_del_method(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not model.objects.filter(
                user=self.request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            ).exists():
                model.objects.create(user=self.request.user, recipe=recipe)
                serializer = RecipeMiniSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            raise ValidationError('Рецепт уже добавлен!')
        if model.objects.filter(
                user=self.request.user,
                recipe=recipe).exists():
            model.objects.filter(
                user=self.request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.create_or_del_method(Favorite, request, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.create_or_del_method(ShoppingCart, request, pk)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))
        filename = 'shopping_list.txt'
        shopping_list = 'Список покупок:\n\n'
        shopping_list += '\n'.join([
            f'{ingredient["ingredient__name"]} '
            f'- {ingredient["total"]} '
            f'{ingredient["ingredient__measurement_unit"]}.'
            for ingredient in ingredients
        ])
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""
    list_display = ('name', 'color', 'slug',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""
    list_display = ('id', 'name', 'author', 'favorite_count')
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранного."""
    list_display = ('user', 'recipe',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка списка покупок."""
    list_display = ('user', 'recipe',)
    empty_value_display = '-пусто-'

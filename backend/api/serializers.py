import base64
import webcolors
from rest_framework import serializers
from django.core.files.base import ContentFile
from recipes.models import (
    Favorites, Ingredient, QuantityOfIngredients, Recipe, ShoppingCart, Tag
    )
from users.models import User
from users.serializers import CustomUserSerializer
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.exceptions import ValidationError


class Hex2NameColor(serializers.Field):
    """Сериализатор цвета тегов."""
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингрердиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    """Сериализатор картинок."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class QuantityOfIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингрердиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = QuantityOfIngredients
        fields = fields = ('id', 'name', 'measurement_unit', 'quantity')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра рецептов"""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = QuantityOfIngredientsSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return Recipe.objects.filter(
            shopping_cart__user=user, id=obj.id
        ).exists()


class RecipeСreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = QuantityOfIngredientsSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def validate(self, ingredients):
        if not ingredients:
            raise ValidationError('Укажите ингредиенты.')

        ingredient_list = []
        for ingredient in ingredients:
            if ingredient in ingredient_list:
                raise ValidationError('Ингредиенты не должны повторяться.')

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            QuantityOfIngredients.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                quantity=ingredient.get('quantity'),
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        if "ingredients" in self.initial_data:
            ingredients = validated_data.pop("ingredients")
            recipe.ingredients.clear()
            self.create_ingredients(ingredients, recipe)
        if "tags" in self.initial_data:
            tags_data = validated_data.pop("tags")
            recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={'request': self.context.get('request')},
        ).data


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор избранного."""
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorites
        fields = '__all__'

    def validate(self, data):
        if Favorites.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise ValidationError('Рецепт уже избранном!')
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, data):
        if ShoppingCart.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError('Рецепт уже в списке покупок!')
        return data

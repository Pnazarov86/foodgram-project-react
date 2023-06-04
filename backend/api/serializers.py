import base64
import webcolors
from recipes.models import Ingredient
from rest_framework import serializers
from django.core.files.base import ContentFile
from recipes.models import (
    Favorites, Ingredient, IngredientRecipe, Recipe, Shopping_cart, Tag
    )
from users.models import User
from users.serializers import CustomUserSerializer
from rest_framework.fields import SerializerMethodField
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


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингрердиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = fields = ('id', 'name', 'measurement_unit', 'quantity')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    ingredients = SerializerMethodField()
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

    def validate(self, ingredients):
        if not ingredients:
            raise ValidationError('Укажите ингредиенты.')

    for ingredient in ingredients:
        if int(ingredient['quantity']) < 1:
            raise ValidationError('Укажите не менее одного ингредиента.')

    ingredient_list = []
    for ingredient in ingredients:
        if ingredient in ingredient_list:
            raise ValidationError('Ингредиенты не должны повторяться.')

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
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
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

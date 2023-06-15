import base64
import webcolors
from rest_framework import serializers
from django.core.files.base import ContentFile
from users.models import Follow, User
from recipes.models import (
    Ingredient, IngredientRecipe, Recipe, Tag
    )
from users.serializers import CustomUserSerializer
from rest_framework.fields import SerializerMethodField
from rest_framework.exceptions import ValidationError
from django.db.models import F


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


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингрердиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингрердиентов."""

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    """Сериализатор картинок."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientrecipe__amount')
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
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField(required=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def validate(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise ValidationError('Укажите тег.')
        data['tags'] = tags
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError('Укажите ингредиенты.')
        ingredient_list = []
        for ingredient in ingredients:
            if ingredient in ingredient_list:
                raise ValidationError('Ингредиенты не должны повторяться.')
            ingredient_list.append(ingredient)
            data['ingredients'] = ingredients
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < 1:
            raise ValidationError('Укажите время приготовления.')
        data['cooking_time'] = cooking_time
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.create_ingredients(ingredients, recipe)
        if 'tags' in self.initial_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={'request': self.context.get('request')},
        ).data


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов в подписках."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeFollowSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, data):
        user = self.context.get('request').user
        author = self.instance
        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError('Вы уже подписаны.')
        if user == author:
            raise ValidationError('Нельзя подписаться на себя!')
        return data

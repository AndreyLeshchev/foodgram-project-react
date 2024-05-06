from drf_extra_fields.fields import Base64ImageField

from django.contrib.auth import get_user_model
from rest_framework import serializers, validators
from rest_framework.serializers import ValidationError

from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag,
)
from users.models import Subscription

User = get_user_model()


class MyCustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели MyCustomUser."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.author.filter(subscriber=request.user).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""

    class Meta:
        model = Subscription
        fields = (
            'id',
            'author',
            'subscriber',
        )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'subscriber'),
                message='Подписка уже оформлена.',
            )
        ]

    def validate(self, data):
        if data['author'] == data['subscriber']:
            raise serializers.ValidationError(
                'Невозможно оформить самоподписку.'
            )
        return data


class SubscriptionShowSerializer(MyCustomUserSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        return RecipeShowSerializer(
            obj.recipes.all(), many=True,
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = (
            'id', 'name',
            'color', 'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = (
            'id', 'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name',
            'measurement_unit', 'amount',
        )


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'amount',
        )


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов при Get запросах."""

    author = MyCustomUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorite_user.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_user.filter(recipe=obj).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов при Post запросах."""

    image = Base64ImageField(required=True)
    ingredients = CreateRecipeIngredientSerializer(many=True, required=True, )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True,
    )
    author = MyCustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags',
            'image', 'name', 'text',
            'cooking_time', 'author',
        )

    def create_ingredients(self, recipe, ingredients):
        results = [
            RecipeIngredient(
                recipe=recipe, ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(results)

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.name = validated_data.get('name', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time,
        )
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def validate(self, data):
        if 'tags' not in data:
            raise ValidationError(
                {'tags': 'Поле тэгов не может быть пустым!'}
            )
        if 'ingredients' not in data:
            raise ValidationError(
                {'ingredients': 'Поле ингредиентов не может быть пустым!'}
            )
        if 'image' not in data:
            raise ValidationError(
                {'image': 'Поле для картинки не может быть пустым!'}
            )
        return data

    def to_representation(self, instance):
        return GetRecipeSerializer(instance).data


class RecipeShowSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'image', 'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite."""

    class Meta:
        model = Favorite
        fields = ('recipe', 'user',)
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('recipe', 'user'),
                message='Рецепт уже добавлен в избранное.',
            ),
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCart."""

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user',)
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('recipe', 'user'),
                message='Рецепт уже добавлен в cписок покупок.',
            ),
        ]

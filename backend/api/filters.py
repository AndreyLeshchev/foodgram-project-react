from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

from recipes.models import Ingredient, Recipe

User = get_user_model()


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, qs, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return qs.filter(favorite_recipe__user=user)

    def get_is_in_shopping_cart(self, qs, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return qs.filter(shopping_recipe__user=user)

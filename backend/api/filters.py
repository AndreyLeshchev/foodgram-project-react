from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredienFilter(filters.FilterSet):
    """Фильтр для ингредиентов."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.AllValuesMultipleFilter(field_name='author__username')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

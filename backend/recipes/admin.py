from django.contrib import admin

from .models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag,
)

admin.site.empty_value_display = 'Ещё ничего не задано'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeIngredientAdmin(admin.StackedInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'text',
        'get_ingredients',
        'get_tags',
        'cooking_time',
    )
    list_filter = (
        'author', 'name', 'tags',
    )
    search_fields = (
        'author', 'name', 'tags',
    )
    inlines = (RecipeIngredientAdmin,)

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return '\n'.join(
            Recipe.objects.filter(id=obj.id).values_list(
                'ingredients__name', flat=True,
            )
        )

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        return '\n'.join(
            Recipe.objects.filter(id=obj.id).values_list(
                'tags__name', flat=True,
            )
        )



@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'user',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'user',
    )

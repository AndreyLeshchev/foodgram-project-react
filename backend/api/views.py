from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import decorators, permissions, status, viewsets, response

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)
from users.models import Subscription
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CreateRecipeSerializer, FavoriteSerializer, GetRecipeSerializer,
    IngredientSerializer, MyCustomUserSerializer, RecipeShowSerializer,
    ShoppingCartSerializer, SubscriptionSerializer, SubscriptionShowSerializer,
    TagSerializer,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    serializer_class = MyCustomUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    lookup_url_kwarg = 'id'

    @decorators.action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(permissions.IsAuthenticated, ),
    )
    def get_subscriptions(self, request):
        """Список подписок."""

        authors = User.objects.filter(author__subscriber=request.user)
        result_pages = self.paginate_queryset(queryset=authors,)
        context = {'request': request}
        serializer = SubscriptionShowSerializer(
            result_pages, context=context, many=True,
        )
        return self.get_paginated_response(serializer.data)

    @decorators.action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(permissions.IsAuthenticated, )
    )
    def get_subscribe(self, request, id=None):
        """Оформление подписки."""

        author = get_object_or_404(User, id=id)
        subscriber = get_object_or_404(User, id=request.user.id)
        data = {'subscriber': subscriber.id, 'author': author.id}
        serializer = SubscriptionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        context = {'request': request}
        result_serializer = SubscriptionShowSerializer(
            author, context=context,
        )
        return response.Response(
            result_serializer.data, status=status.HTTP_201_CREATED,
        )

    @get_subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Удаление подписки."""

        try:
            subscription = Subscription.objects.get(
                subscriber=request.user, author=id,
            )
        except Subscription.DoesNotExist:
            return HttpResponseBadRequest(
                'Вы еще не подписаны на этого пользователя.'
            )
        subscription.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(), )
        return super().get_permissions()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    lookup_url_kwarg = 'id'

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return GetRecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @decorators.action(
        detail=True,
        methods=['post'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=(permissions.IsAuthenticated, )
    )
    def get_favorite(self, request, id=None):
        """Добавление рецепта в избранные."""

        try:
            recipe = Recipe.objects.get(id=id)
        except Recipe.DoesNotExist:
            return HttpResponseBadRequest('Рецепт ещё не создан.')
        user = get_object_or_404(User, id=request.user.id)
        data = {'user': user.id, 'recipe': recipe.id}
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        result_serializer = RecipeShowSerializer(recipe)
        return response.Response(
            result_serializer.data, status=status.HTTP_201_CREATED
        )

    @get_favorite.mapping.delete
    def delete_favorite(self, request, id=None):
        """Удаления рецепта из избранных."""

        recipe = get_object_or_404(Recipe, id=id)
        try:
            favorite_recipe = Favorite.objects.get(
                user=request.user, recipe=recipe,
            )
        except Favorite.DoesNotExist:
            return HttpResponseBadRequest(
                'У вас нет этого рецепта в избранных.'
            )
        favorite_recipe.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=True,
        methods=['post'],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(permissions.IsAuthenticated, )
    )
    def get_shopping_cart(self, request, id=None):
        """Добавление рецепта в корзину покупок."""

        try:
            recipe = Recipe.objects.get(id=id)
        except Recipe.DoesNotExist:
            return HttpResponseBadRequest('Рецепт ещё не создан.')
        user = get_object_or_404(User, id=request.user.id)
        data = {'user': user.id, 'recipe': recipe.id}
        serializer = ShoppingCartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        shopping_cart_serializer = RecipeShowSerializer(recipe)
        return response.Response(
            shopping_cart_serializer.data, status=status.HTTP_201_CREATED
        )

    @get_shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, id=None):
        """Удаления рецепта из корзины покупок."""

        recipe = get_object_or_404(Recipe, id=id)
        try:
            shopping_cart_recipe = ShoppingCart.objects.get(
                user=request.user, recipe=recipe,
            )
        except ShoppingCart.DoesNotExist:
            return HttpResponseBadRequest(
                'У вас нет этого рецепта в списке покупок.'
            )
        shopping_cart_recipe.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        """Файл со списком покупок."""

        author = get_object_or_404(User, id=request.user.id)
        ingredients_recipes = RecipeIngredient.objects.filter(
            recipe__shopping_recipe__user=author,
        ).values(
            'ingredient__name', 'ingredient__measurement_unit',
        ).annotate(
            amount=Sum('amount'),
        )
        response = HttpResponse(content_type='text/plain', charset='utf-8')
        response['Content-Disposition'] = (
            'attachment; '
            'filename="shopping_cart.txt"'
        )
        results_cart = 'Продуктовая корзина:\n'
        if ingredients_recipes.exists():
            for num, ingredient in enumerate(ingredients_recipes, 1):
                results_cart += (
                    f"{num}. "
                    f"{ingredient['ingredient__name'].capitalize()} - "
                    f"{ingredient['amount']} "
                    f"{ingredient['ingredient__measurement_unit']}.\n"
                )
            response.content = results_cart
            response.status_code = status.HTTP_200_OK
            return response
        response.content = 'Продуктовая корзина пуста.'
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

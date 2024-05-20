from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework import status, response

from recipes.models import Recipe
from .serializers import RecipeShowSerializer

User = get_user_model()


def create_post(model_serializer=None, request=None, id=None):

    try:
        recipe = Recipe.objects.get(id=id)
    except Recipe.DoesNotExist:
        return HttpResponseBadRequest('Рецепт ещё не создан.')
    user = get_object_or_404(User, id=request.user.id)
    data = {'user': user.id, 'recipe': recipe.id}
    serializer = model_serializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    result_serializer = RecipeShowSerializer(recipe)
    return response.Response(
        result_serializer.data, status=status.HTTP_201_CREATED
    )


def delete_post(obj=None, request=None, id=None):

    recipe = get_object_or_404(Recipe, id=id)

    try:
        obj_result = obj.objects.get(
            user=request.user, recipe=recipe,
        )
    except obj.DoesNotExist:
        return HttpResponseBadRequest(
            'У вас еще нет этого рецепта.'
        )
    obj_result.delete()
    return response.Response(status=status.HTTP_204_NO_CONTENT)

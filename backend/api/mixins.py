from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework import status, response


class CreateDeleteMixin:

    def delete_info(obj_one=None, obj_two=None, request=None, id=None):
        if obj_one is not None:
            obj_recipe = get_object_or_404(obj_one, id=id)

        try:
            delete_obj = obj_two.objects.get(
                user=request.user, recipe=obj_recipe,
            )
        except obj_two.DoesNotExist:
            return HttpResponseBadRequest(
                'У вас еще нет этого рецепта.'
            )
        delete_obj.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

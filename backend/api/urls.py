from django.urls import include, path
from rest_framework.routers import DefaultRouter as Router

from .views import (
    CustomUserViewSet, IngredientViewSet, RecipeViewSet, TagViewSet,
)

router = Router()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

apipatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

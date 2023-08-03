from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, ProfileViewSet, RecipeViewSet,
                       TagViewSet)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', ProfileViewSet, basename='users')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

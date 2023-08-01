from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeListSerializer, RecipeWriteSerializer,
                             ShoppingCartSerializer, TagSerializer)
from core.permissions import IsAdminAuthorOrReadOnly
from foodgram_backend.models import (Favorite, Ingredient, Recipe,
                                     ShoppingCart, Tag)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_param = 'name'
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RecipeListSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'ingredients_in_recipe__ingredient', 'tags'
        ).all()
        return recipes

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        serializer = FavoriteSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=request.user.id, recipe=pk)
            favorite.delete()
            return Response(status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        serializer = ShoppingCartSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            shopping_cart = ShoppingCart.objects.filter(
                user=request.user.id,
                recipe=pk
            )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        recipes_in_shopping_cart = self.filter_queryset(
            self.get_queryset()).filter(
            added_to_shopping_carts__user=request.user
        )

        shopping_cart = {}
        for recipe in recipes_in_shopping_cart:
            for ingredient_in_recipe in recipe.ingredients_in_recipe.all():
                ingredient = ingredient_in_recipe.ingredient
                item = f'{ingredient.name} ({ingredient.measurement_unit})'
                if item in shopping_cart:
                    shopping_cart[item] += ingredient_in_recipe.amount
                else:
                    shopping_cart[item] = ingredient_in_recipe.amount
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.txt"')
        for item, amount in shopping_cart.items():
            response.write(f'{item} - {amount}\n')

        return response

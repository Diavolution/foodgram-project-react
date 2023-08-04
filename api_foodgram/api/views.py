from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             ProfileSerializer, RecipeListSerializer,
                             RecipeWriteSerializer, ShoppingCartSerializer,
                             SubscriptionListSerializer,
                             SubscriptionWriteSerializer, TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'ingredients_in_recipe__ingredient', 'tags'
    ).all()
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RecipeListSerializer
        return RecipeWriteSerializer

    @staticmethod
    def create_instance(serializer, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        instance = serializer(data=data, context={'request': request})
        instance.is_valid(raise_exception=True)
        instance.save()
        return Response(instance.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_instance(model, request, pk):
        model_instance = model.objects.filter(user=request.user.id, recipe=pk)

        deleted = model_instance.delete()[0]
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Объекта для удаления не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        return self.create_instance(FavoriteSerializer, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_instance(Favorite, request, pk)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.create_instance(ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_instance(ShoppingCart, request, pk)

    def create_shopping_cart_file(self, shopping_cart):
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.txt"')

        for item, amount in shopping_cart.items():
            response.write(f'{item}, - {amount}\n')

        return response

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__added_to_shopping_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')

        shopping_cart = {}
        for ingredient in ingredients:
            item = (
                f'{ingredient["ingredient__name"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
            )
            shopping_cart[item] = ingredient['amount']

        return self.create_shopping_cart_file(shopping_cart)


class ProfileViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            data = {
                'user': request.user.id,
                'author': author_id
            }
            serializer = SubscriptionWriteSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            list_serializer = SubscriptionListSerializer(
                author,
                context={'request': request}
            )
            return Response(
                list_serializer.data,
                status=status.HTTP_201_CREATED
            )

        subscription = Subscription.objects.filter(
            user=request.user.id,
            author=author
        )
        deleted = subscription.delete()[0]
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Объекта для удаления не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionListSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

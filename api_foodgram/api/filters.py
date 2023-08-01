import django_filters

from foodgram_backend.models import Recipe


class TagFilter(django_filters.Filter):
    def filter(self, queryset, value):
        if not value:
            return queryset

        tags = value.split(',')
        return queryset.filter(tags__slug__in=tags).distinct()


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = TagFilter(field_name='tags__slug', lookup_expr='icontains')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                added_to_shopping_carts__user=self.request.user
            )
        return queryset

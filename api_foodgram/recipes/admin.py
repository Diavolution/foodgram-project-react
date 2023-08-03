from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)


class RecipeIngredientInLine(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('author', 'name', 'tags')
    inlines = (RecipeIngredientInLine,)
    empty_value_display = '-пусто-'

    def favorites_count(self, obj):
        return obj.favorited_by.count()


admin.site.register(Favorite)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientInRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Tag)

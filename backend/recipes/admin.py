from django.contrib import admin

from .models import FavouriteRecipe, Ingredient, Recipe, ShoppingList, Tag


@admin.register(Tag)
class TagInAdmin(admin.ModelAdmin):
    """Модель тегов для отображения в админке"""

    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientInAdmin(admin.ModelAdmin):
    """Модель ингредиентов для отображения в админке"""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeInAdmin(admin.ModelAdmin):
    """Модель рецептов для отображения в админке"""

    list_display = ("id", "name", "author")
    list_filter = ("name", "author", "tags")
    search_fields = ("name", "author")
    readonly_fields = ("count_favorites",)

    def count_favorites(self, obj):
        return obj.favorites.count()


@admin.register(FavouriteRecipe)
class FavouriteRecipeInAdmin(admin.ModelAdmin):
    """Модель избранных для отображения в админке"""

    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")


@admin.register(ShoppingList)
class ShoppingListInAdmin(admin.ModelAdmin):
    """Модель избранных для отображения в админке"""

    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")

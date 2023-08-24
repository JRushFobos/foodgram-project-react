from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredients


@admin.register(Tag)
class TagInAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientInAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeInAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author")
    list_filter = ("name", "author", "tags")
    search_fields = ("name", "author")
    readonly_fields = ("count_favorites",)

    def count_favorites(self, obj):
        return obj.favorites.count()


@admin.register(RecipeIngredients)
class RecipeIngredientsInAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'amount')
    search_fields = ('recipe',)

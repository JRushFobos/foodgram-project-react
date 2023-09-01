from django.contrib import admin

from .models import FavouriteRecipe, Ingredient, Recipe, ShoppingList, Tag


@admin.register(Tag)
class TagInAdmin(admin.ModelAdmin):
    """Класс тегов для отображения в админке."""

    empty_value_display = "значение отсутствует"
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientInAdmin(admin.ModelAdmin):
    """Класс ингредиентов для отображения в админке."""

    empty_value_display = "значение отсутствует"
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


class IngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 0
    mix_num = 1


@admin.register(Recipe)
class RecipeInAdmin(admin.ModelAdmin):
    """Класс рецептов для отображения в админке."""

    empty_value_display = "значение отсутствует"
    list_display = (
        "id",
        "name",
        "author",
        "text",
        "get_ingredients",
        "cooking_time",
        "image",
        "pub_date",
        "count_favourites",
    )
    list_filter = ("name", "author", "tags")
    inlines = (IngredientsInLine,)
    search_fields = ("name", "author")

    def get_ingredients(self, object):
        """Метод получения ингредиентов в рецепте в админке."""
        return "\n".join(
            ingredient.name for ingredient in object.ingredients.all()
        )

    get_ingredients.short_description = "Ингредиенты"

    def count_favourites(self, obj):
        return obj.favourites.count()

    count_favourites.short_description = "Количество добавлений в избранное"


@admin.register(FavouriteRecipe)
class FavouriteRecipeInAdmin(admin.ModelAdmin):
    """Класс избранных для отображения в админке."""

    empty_value_display = "значение отсутствует"
    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")


@admin.register(ShoppingList)
class ShoppingListInAdmin(admin.ModelAdmin):
    """Класс избранных для отображения в админке."""

    empty_value_display = "значение отсутствует"
    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")

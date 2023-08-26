from django_filters import rest_framework
from django.contrib.auth import get_user_model
from recipes.models import Recipe, ShoppingList, FavouriteRecipe, Tag
from django_filters import FilterSet

User = get_user_model()

CHOICES_LIST = (('0', 'False'), ('1', 'True'))


CHOICES_LIST = (('0', 'False'), ('1', 'True'))


class ShoppingListFilter(FilterSet):
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST, method='filter_is_in_shopping_cart'
    )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipe_ids = [item.recipe.id for item in shopping_cart]

        if not rest_framework.utils.str_to_bool(value):
            return queryset.exclude(id__in=recipe_ids)
        else:
            return queryset.filter(id__in=recipe_ids)

    class Meta:
        model = ShoppingList
        fields = ['is_in_shopping_cart']


class FavoriteFilter(FilterSet):
    is_favorited = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST, method='filter_is_favorited'
    )

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        favorites = FavouriteRecipe.objects.filter(user=self.request.user)
        recipe_ids = [item.recipe.id for item in favorites]

        if not rest_framework.utils.str_to_bool(value):
            return queryset.exclude(id__in=recipe_ids)
        else:
            return queryset.filter(id__in=recipe_ids)

    class Meta:
        model = FavouriteRecipe
        fields = ['is_favorited']


class RecipesFilter(FilterSet):
    is_favorited = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST, method='filter_is_favorited'
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST, method='filter_is_in_shopping_cart'
    )
    author = rest_framework.NumberFilter(
        field_name='author', lookup_expr='exact'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        favorite_filter = FavoriteFilter(
            data={'is_favorited': value}, queryset=queryset
        )
        favorite_filter.form.is_valid()

        return favorite_filter.queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        shopping_cart_filter = ShoppingListFilter(
            data={'is_in_shopping_cart': value}, queryset=queryset
        )
        shopping_cart_filter.form.is_valid()
        return shopping_cart_filter.queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

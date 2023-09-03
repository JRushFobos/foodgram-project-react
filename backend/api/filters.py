from django.contrib.auth import get_user_model
from django_filters import FilterSet, rest_framework

from recipes.models import Recipe, Tag

User = get_user_model()


class RecipesFilter(FilterSet):
    """Фильтры для shoppinglist и favourites рецептов"""

    is_favorited = rest_framework.filters.BooleanFilter(
        method='filter_favorited'
    )
    is_in_shopping_cart = rest_framework.filters.BooleanFilter(
        method='filter_shopping_cart'
    )
    tags = rest_framework.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )

    def filter_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return Recipe.objects.filter(
                id__in=self.request.user.favourites.all().values_list(
                    'recipe_id'
                )
            )
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return Recipe.objects.filter(
                id__in=self.request.user.shoppinglist.all().values_list(
                    'recipe_id'
                )
            )
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")

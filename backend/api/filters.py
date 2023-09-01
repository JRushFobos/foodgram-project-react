from django.contrib.auth import get_user_model
from django_filters import FilterSet, rest_framework

from recipes.models import Recipe, Tag

User = get_user_model()

CHOICES_LIST = (("0", "False"), ("1", "True"))


class RecipesFilter(FilterSet):
    """Фильтры для shoppinglist и favourites рецептов"""

    is_favorited = rest_framework.NumberFilter(method="filter_is_favorited")
    is_in_shopping_cart = rest_framework.NumberFilter(
        method="filter_is_in_shopping_cart"
    )
    author = rest_framework.NumberFilter(
        field_name="author", lookup_expr="exact"
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()
        if value == 1:
            return queryset.filter(favourites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()
        if value == 1:
            return queryset.filter(shoppinglist__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")

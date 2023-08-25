from http import HTTPStatus

from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import action
from django.db import transaction
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from django.db.models import Case, When, IntegerField, Sum, Value

from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    FavouriteRecipe,
    ShoppingList,
    RecipeIngredients,
)
from .serializers import (
    IngredientsSerializer,
    TagsSerializer,
    RecipesWriteSerializer,
    RecipesReadSerializer,
    CheckFavouriteSerializer,
    CheckShoppingCartSerializer,
    RecipeAddingSerializer,
)
from .filters import RecipesFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .paginations import CustomPageNumberPagination

FILE_NAME = "shopping-list.txt"
TITLE_SHOP_LIST = "Список покупок с сайта Foodgram:\n\n"


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    """Класс взаимодействия с моделью Recipes. Вьюсет для рецептов."""

    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_class = RecipesFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        """Сериализаторы для рецептов."""
        if self.request.method in SAFE_METHODS:
            return RecipesReadSerializer
        return RecipesWriteSerializer

    def get_queryset(self):
        """Резюме по объектам с помощью annotate()."""
        if self.request.user.is_authenticated:
            return Recipe.objects.annotate(
                is_favorited=Case(
                    When(favourites__user=self.request.user, then=1),
                    default=0,
                    output_field=IntegerField(),
                ),
                is_in_shopping_cart=Case(
                    When(shoppinglist__user=self.request.user, then=1),
                    default=0,
                    output_field=IntegerField(),
                ),
            ).prefetch_related('favourites', 'shoppinglist')
        else:
            return Recipe.objects.annotate(
                is_favorited=Value(0, output_field=IntegerField()),
                is_in_shopping_cart=Value(0, output_field=IntegerField()),
            )

    @transaction.atomic()
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=["POST"], permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавить в избранное."""
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = CheckFavouriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.add_object(FavouriteRecipe, request.user, pk)

    @favorite.mapping.delete
    def del_favorite(self, request, pk=None):
        """Убрать из избранного."""
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = CheckFavouriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.delete_object(FavouriteRecipe, request.user, pk)

    @action(
        detail=True, methods=["POST"], permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Добавить в лист покупок."""
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = CheckShoppingCartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.add_object(ShoppingList, request.user, pk)

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, pk=None):
        """Убрать из листа покупок."""
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = CheckShoppingCartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.delete_object(ShoppingList, request.user, pk)

    @transaction.atomic()
    def add_object(self, model, user, pk):
        """Добавление объектов для избранного/спсика покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeAddingSerializer(recipe)
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @transaction.atomic()
    def delete_object(self, model, user, pk):
        """Удаление объектов для избранного/спсика покупок."""
        model.objects.filter(user=user, recipe__id=pk).delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        methods=["GET"], detail=False, permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать файл листа покупок."""
        ingredients = (
            RecipeIngredients.objects.filter(recipe__list__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .order_by("ingredient__name")
            .annotate(total=Sum("amount"))
        )
        result = TITLE_SHOP_LIST
        result += "\n".join(
            (
                f'{ingredient["ingredient__name"]} - {ingredient["total"]}/'
                f'{ingredient["ingredient__measurement_unit"]}'
                for ingredient in ingredients
            )
        )
        response = HttpResponse(result, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename={FILE_NAME}"
        return response

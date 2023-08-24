from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    ShoppingList,
    FavouriteRecipe,
    RecipeIngredients,
)
from .serializers import (
    IngredientsSerializer,
    TagsSerializer,
    ShortRecipeSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
)
from .filters import RecipeFilter
from .permissions import IsAuthorOrAdmin
from .paginations import CustomPageNumberPagination


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer

        return RecipeSerializer

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if FavouriteRecipe.objects.filter(
                user=user, recipe=recipe
            ).exists():
                raise exceptions.ValidationError('Рецепт уже в избранном.')

            FavouriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe, context={'request': request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not FavouriteRecipe.objects.filter(
                user=user, recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепта нет в избранном, либо он уже удален.'
                )

            favorite = get_object_or_404(
                FavouriteRecipe, user=user, recipe=recipe
            )
            favorite.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    'Рецепт уже в списке покупок.'
                )

            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe, context={'request': request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not ShoppingList.objects.filter(
                user=user, recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепта нет в списке покупок, либо он уже удален.'
                )

            shopping_cart = get_object_or_404(
                ShoppingList, user=user, recipe=recipe
            )
            shopping_cart.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False, methods=('get',), permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_list = (
            RecipeIngredients.objects.filter(recipe__in=recipes)
            .values('ingredient')
            .annotate(amount=Sum('amount'))
        )

        buy_list_text = 'Список покупок с сайта Foodgram:\n\n'
        for item in buy_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            buy_list_text += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )

        response = HttpResponse(buy_list_text, content_type="text/plain")
        response[
            'Content-Disposition'
        ] = 'attachment; filename=shopping-list.txt'

        return response

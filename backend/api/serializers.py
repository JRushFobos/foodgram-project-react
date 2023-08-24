from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework import serializers
from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Ingredient,
    FavouriteRecipe,
    Recipe,
    RecipeIngredients,
    Tag,
    ShoppingList,
)
from users.serializers import CustomUserSerializer

User = get_user_model()


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name="get_id")
    name = serializers.SerializerMethodField(method_name="get_name")
    measurement_unit = serializers.SerializerMethodField(
        method_name="get_measurement_unit"
    )

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    class Meta:
        model = RecipeIngredients
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeIngredientsWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1, message="Количество ингредиента должно быть >= 1."
            ),
        )
    )

    class Meta:
        model = RecipeIngredients
        fields = ("id", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    """[Read] Сериалайзер рецептов."""

    author = serializers.PrimaryKeyRelatedField(read_only=True)
    tags = TagsSerializer(many=True)
    ingredients = RecipeIngredientsWriteSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name="get_is_favorited"
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart"
    )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        serializer = RecipeIngredientsReadSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return FavouriteRecipe.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return ShoppingList.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        exclude = ("pub_date",)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["ingredients"] = [
            {
                "id": item["ingredient"],
                "amount": item["amount"],
            }
            for item in representation["ingredients"]
        ]
        representation["image"] = (
            instance.image.url if instance.image else None
        )

        return representation


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """[Write] Сериалайзер рецептов."""

    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientsWriteSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1, message="Время приготовления должно быть 1 или более."
            ),
        )
    )

    def create(self, validated_data):
        author = self.context.get("request").user
        if not author.is_authenticated:
            raise serializers.ValidationError(
                "Создать рецепт может только авторизованный пользователь"
            )

        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient["amount"]
            ingredient = get_object_or_404(Ingredient, pk=ingredient["id"])

            RecipeIngredients.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            instance.ingredients.clear()

            for ingredient in ingredients:
                amount = ingredient["amount"]
                ingredient = get_object_or_404(Ingredient, pk=ingredient["id"])

                RecipeIngredients.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    defaults={"amount": amount},
                )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        )

        return serializer.data

    class Meta:
        model = Recipe
        fields = "__all__"
        read_only_fields = ("author",)

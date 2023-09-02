from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from users.models import Subscription
from recipes.models import (
    FavouriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingList,
    Tag,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return Subscription.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        )
        ordering = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        )


class RecipeInSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = obj.recipes.all()
        if limit is not None:
            try:
                limit = int(limit)
                if limit >= 0:
                    queryset = queryset[:limit]
                else:
                    return {
                        "error": "Кол-во рецептов не может "
                        "быть отрицательным числом",
                    }
            except ValueError:
                return {
                    "error": "Кол-во рецептов должен быть целым числом",
                }
        else:
            return RecipeInSubscriptionSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class CheckSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор проверки подписки"""

    class Meta:
        model = Subscription
        fields = (
            "user",
            "author",
        )

    def validate(self, attrs):
        user = attrs["user"]
        author = attrs["author"]
        subscribed = user.subscribers.filter(author=author).exists()

        if self.context.get("request").method == "POST":
            if user == author:
                raise serializers.ValidationError(
                    "Ошибка, на себя подписка не разрешена"
                )
            if subscribed:
                raise serializers.ValidationError("Ошибка, вы уже подписались")
        if self.context.get("request").method == "DELETE":
            if user == author:
                raise serializers.ValidationError(
                    "Ошибка, отписка от самого себя не допустима"
                )
            if not subscribed:
                raise serializers.ValidationError(
                    {"errors": "Ошибка, вы уже отписались"}
                )
        return attrs


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipesReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов."""

    tags = TagsSerializer(many=True)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        exclude = ("pub_date",)

    def get_ingredients(self, obj):
        ingredients_data = obj.ingredients.through.objects.filter(
            recipe=obj
        ).values(
            "ingredient__id",
            "ingredient__name",
            "ingredient__measurement_unit",
            "amount",
        )
        modified_ingredients = []

        for ingredient_data in ingredients_data:
            modified_ingredient = {
                "id": ingredient_data["ingredient__id"],
                "name": ingredient_data["ingredient__name"],
                "measurement_unit": ingredient_data[
                    "ingredient__measurement_unit"
                ],
                "amount": ingredient_data["amount"],
            }
            modified_ingredients.append(modified_ingredient)

        return modified_ingredients


class RecipesWriteSerializer(serializers.ModelSerializer):
    """Сериализатор записи рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ("pub_date",)
        read_only_fields = ("author",)

    def get_ingredients(self, obj):
        ingredients_data = obj.ingredients.through.objects.filter(
            recipe=obj
        ).values(
            "id",
            "amount",
        )
        return ingredients_data

    def validate(self, data):
        ingredients = self.initial_data["ingredients"]
        ingredient_list = []
        if not ingredients:
            raise serializers.ValidationError(
                "Минимально должен быть 1 ингредиент."
            )
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item["id"])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    "Ингредиент не должен повторяться."
                )
            if int(item.get("amount")) < 1:
                raise serializers.ValidationError(
                    "Минимальное количество ингридиентов >= 1"
                )
            ingredient_list.append(ingredient)
        data["ingredients"] = ingredients
        return data

    def validate_cooking_time(self, time):
        if int(time) < 1:
            raise serializers.ValidationError("Минимальное время >= 1")
        return time

    def add_ingredients_and_tags(self, instance, **validate_data):
        ingredients = validate_data["ingredients"]
        tags = validate_data["tags"]
        for tag in tags:
            instance.tags.add(tag)

        RecipeIngredients.objects.bulk_create(
            [
                RecipeIngredients(
                    recipe=instance,
                    ingredient_id=ingredient.get("id"),
                    amount=ingredient.get("amount"),
                )
                for ingredient in ingredients
            ]
        )
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = super().create(validated_data)
        return self.add_ingredients_and_tags(
            recipe, ingredients=ingredients, tags=tags
        )

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance = self.add_ingredients_and_tags(
            instance, ingredients=ingredients, tags=tags
        )
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class FavouriteSerializer(serializers.ModelSerializer):
    """Сериализация добавление рецепта в избранное."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = FavouriteRecipe
        fields = ("user", "recipe")

    def validate(self, obj):
        """Проверка добавления рецепта в избранное."""
        user = self.context["request"].user
        recipe = obj["recipe"]
        favorite = user.favourites.filter(recipe=recipe).exists()

        if self.context.get("request").method == "POST" and favorite:
            raise serializers.ValidationError(
                "Рецепт был уже добавлен в избранное"
            )
        if self.context.get("request").method == "DELETE" and not favorite:
            raise serializers.ValidationError("Рецепт отсутствует в избранном")
        return obj


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализация добавление в список покупок"""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingList
        fields = ("user", "recipe")

    def validate(self, obj):
        """Проверка добавления в продуктовую корзину."""
        user = self.context["request"].user
        recipe = obj["recipe"]
        shop_list = user.shoppinglist.filter(recipe=recipe).exists()

        if self.context.get("request").method == "POST" and shop_list:
            raise serializers.ValidationError("Рецепт уже в списке покупок.")
        if self.context.get("request").method == "DELETE" and not shop_list:
            raise serializers.ValidationError("Рецепт не в списке покупок.")
        return obj

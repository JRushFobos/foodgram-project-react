from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator

User = get_user_model()

MAX_CHAR_LENGTH = 200
MAX_COLOR_LENGTH = 7


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name="Название тега",
        max_length=MAX_CHAR_LENGTH,
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цвет тега в формате HEX",
        max_length=MAX_COLOR_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                "^#([a-fA-F0-9]{6})",
                message="Поле только для HEX формата данных",
            )
        ],
    )
    slug = models.SlugField(
        verbose_name="Слаг тега",
        max_length=MAX_CHAR_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("id",)

    def __str__(self):
        return f"{self.name}"


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(
        verbose_name="Название ингридиента",
        max_length=MAX_CHAR_LENGTH,
        blank=False,
    )
    measurement_unit = models.CharField(
        verbose_name="Eдиница измерения ингридиента",
        max_length=MAX_CHAR_LENGTH,
        blank=False,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("id",)

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipes",
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientsInRecipe",
        verbose_name="Список ингредиентов для рецепта",
        help_text="Список ингредиентов для рецепта",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Список id тегов рецепта",
        related_name="recipes",
        help_text="Список id тегов рецепта",
    )
    image = models.ImageField(
        verbose_name="Изображение рецепта",
        blank=True,
        null=True,
        upload_to="image_recipes/",
    )
    name = models.CharField(
        verbose_name="Название рецепта", max_length=MAX_CHAR_LENGTH
    )

    text = models.TextField(
        verbose_name="Описание рецепта",
        help_text="Описание рецепта",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[
            MinValueValidator(
                1, "Ошибка, время приготовления должно быть больше 1 минуты."
            )
        ],
    )
    pud_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pud_date",)

    def __str__(self):
        return f"{self.name}"

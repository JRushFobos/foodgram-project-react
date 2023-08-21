from django.db import models
from django.core.validators import RegexValidator

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

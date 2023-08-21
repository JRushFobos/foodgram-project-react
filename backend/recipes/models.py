from django.db import models


class Tags(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name="Название тега",
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цвет тега в формате HEX",
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Слаг тега",
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("id",)

    def __str__(self):
        return f"{self.name}"

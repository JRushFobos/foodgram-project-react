from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.settings import MAX_CHAR_LENGTH, MAX_EMAIL_LENGTH
from users.validators import validate_username


class User(AbstractUser):
    """Модель пользователей"""

    email = models.EmailField(
        "Email",
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
    )

    username = models.CharField(
        "Имя пользователя",
        blank=False,
        unique=True,
        max_length=MAX_CHAR_LENGTH,
        validators=[validate_username],
    )

    first_name = models.CharField(
        "Имя",
        blank=False,
        max_length=MAX_CHAR_LENGTH,
        validators=[validate_username],
    )

    last_name = models.CharField(
        "Фамилия",
        blank=False,
        max_length=MAX_CHAR_LENGTH,
        validators=[validate_username],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписчиков."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribes",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписки"
        verbose_name_plural = "Подписчики"

        constraints = (
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="no_self_subscribe",
            ),
            models.UniqueConstraint(
                fields=("user", "author"), name="unique_subscription"
            ),
        )

    def __str__(self):
        return f"Подписка {self.user} на {self.author}"

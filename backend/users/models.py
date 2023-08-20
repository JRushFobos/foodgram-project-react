from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_CHAR_LENGTH = 150
MAX_EMAIL_LENGTH = 254


class User(AbstractUser):
    email = models.EmailField(
        'Email',
        max_length=MAX_EMAIL_LENGTH,
        blank=False,
        unique=True,
    )

    username = models.CharField(
        "Имя пользователя",
        blank=False,
        unique=True,
        max_length=MAX_CHAR_LENGTH,
    )

    first_name = models.CharField(
        'Имя', blank=False, max_length=MAX_CHAR_LENGTH
    )

    last_name = models.CharField(
        'Фамилия', blank=False, max_length=MAX_CHAR_LENGTH
    )

    password = models.CharField(
        'Пароль', blank=False, max_length=MAX_CHAR_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribes',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

        constraints = (
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_subscribe',
            ),
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_subscription'
            ),
        )

    def __str__(self):
        return f'Подписка {self.user} на {self.author}'

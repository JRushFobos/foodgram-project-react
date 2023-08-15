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

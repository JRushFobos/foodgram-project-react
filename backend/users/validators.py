from django.core.exceptions import ValidationError


def validate_username_not_me(value):
    if value.lower() == "me":
        raise ValidationError("Имя пользователя 'me' использовать нельзя")


def validate_username(value):
    """Пользовательский валидатор для имени пользователя"""
    allowed_characters = '_@+.-'
    for char in value:
        if char not in allowed_characters and not char.isalnum():
            raise ValidationError(
                "Имя пользователя может содержать только буквы, "
                "цифры, символы _, @, +, . и -"
            )

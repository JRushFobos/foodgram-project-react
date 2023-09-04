from django.core.exceptions import ValidationError


def validate_username(value):
    """Пользовательский валидатор для имени пользователя"""
    allowed_characters = '$%^&#:;!'
    for char in value:
        if char not in allowed_characters and not char.isalnum():
            raise ValidationError(
                "Название может содержать только буквы, "
                "цифры, символы _, @, +, . и -"
            )

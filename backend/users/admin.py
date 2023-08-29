from django.contrib import admin
from .models import User, Subscription

admin.site.register(User)


@admin.register(Subscription)
class SubscriptionInAdmin(admin.ModelAdmin):
    """Модель подписок для отображения в админке"""

    list_display = ("id", "user", "author")
    search_fields = ("user",)

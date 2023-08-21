from django.contrib import admin

from .models import Tags


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)

import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_name = "ingredients.csv"
        model = Ingredient
        try:
            path = settings.STATICFILES_DIRS[0] / "data" / file_name
            with open(path, encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                model.objects.bulk_create(model(**data) for data in reader)
        except FileNotFoundError:
            raise CommandError(f"Файл {file_name} не найден")
        else:
            print("Ингридиенты загружены!")

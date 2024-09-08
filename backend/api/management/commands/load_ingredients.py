import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу данных из CSV-файла'

    def handle(self, *args, **kwargs):
        # file_path = os.path.join(
        #     settings.BASE_DIR, '..', 'data', 'ingredients.csv'
        # )
        # Используем абсолютный путь к файлу в контейнере
        file_path = os.path.join('/app/data', 'ingredients.csv')

        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                count = 0
                for row in reader:
                    name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name, measurement_unit=measurement_unit
                    )
                    count += 1
                    if count % 100 == 0:
                        self.stdout.write(self.style.SUCCESS(
                            f'{count} записей обработано ...'))
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно загружены'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка: {e}'))

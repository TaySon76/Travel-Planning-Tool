# management/commands/load_cities.py
import os
from django.core.management.base import BaseCommand
from ...models import City

class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = 'C:\\Users\\awais\\OneDrive\\Desktop\\Year 1 summer\\Globetide\\mysite\\main\\static\\main\\output.txt'
        with open(file_path, 'r') as file:
            cities_to_create = []
            for line in file:
                country, city = line.strip().split(': ')
                city_obj = City(country=country, city=city)
                cities_to_create.append(city_obj)
            City.objects.bulk_create(cities_to_create)
            self.stdout.write("Cities loaded successfully!")
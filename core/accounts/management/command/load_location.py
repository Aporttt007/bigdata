import json
from django.core.management.base import BaseCommand
from accounts.models import Area, Region

class Command(BaseCommand):
    help = 'extra/locations.json'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the location JSON file')

    def handle(self, *args, **options):
        with open(options['json_file'], 'r', encoding='utf-8') as f:
            locations = json.load(f)
        
        for loc in locations:
            area, created = Area.objects.get_or_create(
                name=loc['name'],
                code=loc['code']
            )
            for subdivision in loc.get('subdivisions', []):
                Region.objects.get_or_create(
                    name=subdivision,
                    area=area
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded location data'))

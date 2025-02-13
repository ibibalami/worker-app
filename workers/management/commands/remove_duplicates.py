from django.core.management.base import BaseCommand
from workers.models import Worker
from django.db.models import Count

class Command(BaseCommand):
    help = 'Remove duplicate Worker records based on name and telephone'

    def handle(self, *args, **kwargs):
        # Find duplicate entries based on 'name' and 'telephone'
        duplicates = Worker.objects.values('name', 'telephone').annotate(name_count=Count('name')).filter(name_count__gt=1)

        for entry in duplicates:
            # Fetch all workers with the same name and telephone
            workers = Worker.objects.filter(name=entry['name'], telephone=entry['telephone'])

            # Loop through the duplicates, keeping the first record and deleting the rest
            for worker in workers[1:]:
                worker.delete()

        self.stdout.write(self.style.SUCCESS('Successfully removed duplicate Worker records!'))

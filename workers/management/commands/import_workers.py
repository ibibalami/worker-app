import pandas as pd
from django.core.management.base import BaseCommand
from workers.models import Worker

class Command(BaseCommand):
    help = 'C:/Users/ENIGMA/WorkerApp/workers_worker.csv'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='C:/Users/ENIGMA/WorkerApp/workers_worker.csv')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)  # Changed to read_csv

            # Iterate over the rows and create Worker instances
            for _, row in df.iterrows():
                Worker.objects.create(
                    name=row['Name'],          # Adjust column names as necessary
                    title=row['Title'],
                    telephone=row['Telephone'],
                    lat=row['Latitude'],
                    long=row['Longitude']
                )
            self.stdout.write(self.style.SUCCESS('Successfully imported workers'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

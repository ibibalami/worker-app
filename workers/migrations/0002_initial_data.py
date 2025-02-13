from django.db import migrations

def create_initial_worker(apps, schema_editor):
    Worker = apps.get_model('workers', 'Worker')
    Worker.objects.create(name='John Doe', title='Healthcare Worker', post_code='7pr111b', lat=60.94139545, long=71.88098894)

class Migration(migrations.Migration):
    dependencies = [('workers', '0001_initial')]
    operations = [migrations.RunPython(create_initial_worker)]

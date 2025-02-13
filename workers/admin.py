from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Worker

class WorkerResource(resources.ModelResource):
    class Meta:
        model = Worker

admin.site.register(Worker)
class WorkerAdmin(ImportExportModelAdmin):
    resource_class = WorkerResource
    
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'telephone', 'lat', 'long')  # Reflect telephone here




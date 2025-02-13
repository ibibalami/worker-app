from django.db import models

class Worker(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    telephone = models.CharField(max_length=30)
    lat = models.FloatField()
    long = models.FloatField()
    worker_type = models.CharField(max_length=10, choices=[('agency', 'Agency'), ('dom', 'Domiciliary')], default='worker')  # Add this line


    def __str__(self):
        return self.name

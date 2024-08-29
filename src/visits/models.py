from django.db import models

# all model fields here: https://docs.djangoproject.com/en/5.1/ref/models/fields/
# Create your models here.
class PageVisits(models.Model):
    path = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
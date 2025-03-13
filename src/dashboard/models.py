from django.db import models
from django.conf import settings
from datetime import datetime
import os

User = settings.AUTH_USER_MODEL


def unique_filename(instance, filename):
    base, ext = os.path.splitext(filename)  # Split name and extension
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Generate timestamp
    new_filename = f"{base}_{timestamp}{ext}"  # Append timestamp to filename
    return f"uploads/{new_filename}"  # Store in 'uploads/' directory



class CVDocument(models.Model):
    file = models.FileField(upload_to=unique_filename)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

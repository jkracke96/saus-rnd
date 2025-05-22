from django.db import models
from django.conf import settings
from datetime import datetime
from django.urls import reverse

import os

User = settings.AUTH_USER_MODEL
CV_UPLOAD_FOLDER = settings.CV_UPLOAD_FOLDER


def unique_filename(instance, filename):
    base, ext = os.path.splitext(filename)  # Split name and extension
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Generate timestamp
    new_filename = f"{base}_{timestamp}{ext}"  # Append timestamp to filename
    return f"{CV_UPLOAD_FOLDER}/{new_filename}"  # Store in 'uploads/' directory



class CVDocument(models.Model):
    file = models.FileField(upload_to=unique_filename)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"File - {self.user.username}"
    
    @property
    def deleteion_url(self):
        file_name = {self.file.name}
        deleteion_url = reverse("delete_user_file", kwargs={"file_name": file_name})
        return deleteion_url
    

class GeneratedCV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.TextField()
    job_url = models.TextField(null=True, blank=True)
    job_title = models.TextField(null=True, blank=True)
    file_name = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Generated CV - {self.user.username}, {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @property
    def download_url(self):
        file_name = {self.file_name}
        download_url = reverse("download_cv", kwargs={"file_name": file_name})
        return download_url
    
    @property
    def deletion_url(self):
        file_name = {self.file_name}
        deletion_url = reverse("delete_generated_cv", kwargs={"file_name": file_name})
        return deletion_url
    
    @property
    def voice_assistant_url(self):
        job_url = {self.job_url}
        voice_assistant_url = reverse("redirect_to_voice_assistant", kwargs={"job_url": job_url})
        return voice_assistant_url

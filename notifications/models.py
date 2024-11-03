# notifications/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # Ajout d'une référence au professionnel
    professional = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification pour {self.user.username}: {self.title}"

    def mark_as_read(self):
        self.is_read = True 
        self.save()
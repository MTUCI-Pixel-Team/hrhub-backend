from django.db import models
from services_app.models import ServiceAccount


class Message(models.Model):
    account = models.ForeignKey(ServiceAccount, on_delete=models.CASCADE)
    from_username = models.CharField(max_length=255)
    from_userphone = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField()
    personal_chat_link = models.URLField(max_length=500, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    received_at = models.DateTimeField(auto_now=True)

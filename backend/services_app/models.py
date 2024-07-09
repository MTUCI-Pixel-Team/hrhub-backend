from django.db import models
from user_app.models import User


class ServiceAccount(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    service_user_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    service_name = models.CharField(max_length=255)
    service_username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    app_password = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.CharField(blank=True, null=True)
    refresh_token = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('service_name', 'service_username'),)
        unique_together = (('user_id', 'service_user_id'),)

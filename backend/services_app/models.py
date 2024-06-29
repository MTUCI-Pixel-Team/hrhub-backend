from django.db import models
from user_app.models import User


class ServiceAccount(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=255)
    service_username = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

# Generated by Django 5.0.6 on 2024-07-03 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services_app', '0002_serviceaccount_app_password_serviceaccount_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceaccount',
            name='app_password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

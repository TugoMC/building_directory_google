# Generated by Django 5.1.2 on 2024-11-03 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='professional',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
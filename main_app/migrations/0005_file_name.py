# Generated by Django 3.2.4 on 2021-06-15 08:36
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0004_storagedetails"),
    ]

    operations = [
        migrations.AddField(
            model_name="file",
            name="name",
            field=models.CharField(default="test_name.txt", max_length=50),
        ),
    ]

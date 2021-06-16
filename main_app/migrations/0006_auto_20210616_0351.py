# Generated by Django 3.2.4 on 2021-06-16 03:51

from django.db import migrations, models
import main_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(max_length=255, null=True, upload_to=main_app.models.user_directory_path, validators=[main_app.models.validate_file_extension]),
        ),
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]

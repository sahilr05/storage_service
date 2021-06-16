from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [".pdf", ".txt", ".docx", ".html"]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension.")


def user_directory_path(instance, filename):
    return "documents/user_{0}/{1}".format(instance.user.id, filename)


class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userfolders")
    folder = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="folders", null=True, blank=True
    )
    name = models.CharField(_("Folder Name"), max_length=70)

    def __str__(self):
        return self.name


class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        related_name="folder_files",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=50)
    file = models.FileField(
        null=True,
        max_length=255,
        upload_to=user_directory_path,
        validators=[validate_file_extension],
    )
    date_created = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_files")

    def __str__(self):
        return self.file.name


class StorageDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    disk_usage = models.FloatField()

    def __str__(self):
        return self.user.username

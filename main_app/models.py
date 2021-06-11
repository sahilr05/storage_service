from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from django.utils import timezone 

# class Folder(models.Model):
# 	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userfolders')
# 	folder = models.ForeignKey("self", on_delete=models.CASCADE,related_name='folders')
# 	name = models.CharField(_('Folder Name'), max_length=70)

# 	def __str__(self):
# 		return self.name


class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    file = models.FileField(null=True, max_length=255)
    date_created = models.DateTimeField(default = timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userfiles')

    def __str__(self):
        return self.file.name
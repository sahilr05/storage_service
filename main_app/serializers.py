from django.db.models import fields
from rest_framework import serializers
from .models import File, Folder
import math
from main_app import models

class FolderSerializer(serializers.ModelSerializer):
    sub_folders = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()

    def get_creator(self, obj):
        return obj.user.username

    def get_sub_folders(self, obj):
        folders=''
        if obj.folders:
            folders = obj.folders.values_list('name')
        return folders
    class Meta:
        model = Folder
        fields=('name', 'creator', 'sub_folders')


class FileSerializer(serializers.ModelSerializer):    

    def get_size(self, obj):
        file_size = ''
        if obj.file and hasattr(obj.file, 'size'):
            file_size = obj.file.size
            
        return str(round(file_size/(1024*1024), 2))+' MB'
    
    def get_name(self, obj):
        file_name = ''
        if obj.file and hasattr(obj.file, 'name'):
            file_name = obj.file.name
        return file_name    
    
    def get_file_type(self, obj):
        file_name = obj.file.name
        return file_name.split('.')[-1]    

    def get_since_added(self, obj):
        date_added = obj.date_created
        return date_added

    def get_parent_folder(self, obj):
        parent_folder = obj.folder.name
        return parent_folder
        
    size = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    since_added = serializers.SerializerMethodField()    
    parent_folder = serializers.SerializerMethodField()
    class Meta:
        model = File
        fields = ('file_id', 'file', 'size', 'since_added', 'name', 'file_type', 'parent_folder')    
        
        

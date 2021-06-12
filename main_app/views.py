import os

from django.conf import settings
from django.http import Http404
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.models import File
from main_app.models import Folder
from main_app.serializers import FileSerializer
from main_app.serializers import FolderSerializer


class folder_list(APIView):
    def get(self, request):
        folders = Folder.objects.filter(folder=None)
        serializer = FolderSerializer(folders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class folder_detail(APIView):
    def get(self, request, pk):
        folder = Folder.objects.get(id=pk)
        folder_serializer = FolderSerializer(folder)

        files = folder.folder_files.all()
        file_serializer = FileSerializer(files, many=True)

        context = [folder_serializer.data, file_serializer.data]
        return Response(context)


class create_file(APIView):
    def post(self, request):
        parser_classes = (MultiPartParser,)  # NOQA

        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class file_detail(APIView):
    def get_object(self, pk):
        try:
            return File.objects.get(file_id=pk)
        except File.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        file = self.get_object(pk)
        serializer = FileSerializer(file)
        return Response(serializer.data)

    def put(self, request, pk):
        selected_file = self.get_object(pk)
        initial_path = selected_file.file.path
        selected_file.file.name = f"documents/{request.data['name']}"
        new_path = settings.MEDIA_ROOT + "/" + selected_file.file.name
        os.rename(initial_path, new_path)
        selected_file.save()
        serializer = FileSerializer(selected_file, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        file = self.get_object(pk)
        file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

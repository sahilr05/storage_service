import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.http import Http404
from haystack.query import SearchQuerySet
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.models import File as File_Model
from main_app.models import Folder
from main_app.serializers import FileSerializer
from main_app.serializers import FolderSerializer


def get_object(pk, pk_type):
    try:
        if pk_type:
            return File_Model.objects.get(file_id=pk)
        else:
            return Folder.objects.get(pk=pk)
    except File_Model.DoesNotExist:
        raise Http404


class FileSearchViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FileSerializer

    # search file by na,e
    def get_queryset(self, *args, **kwargs):
        params = self.request.query_params
        query = SearchQuerySet().all()
        keywords = params.get("q")
        if keywords:
            query = query.filter(name=keywords)
        return query


class folder_list(APIView):
    permission_classes = (IsAuthenticated,)

    # get list of folders
    def get(self, request):
        folders = Folder.objects.filter(folder=None, user=request.user)
        serializer = FolderSerializer(folders, many=True)
        return Response(serializer.data)

    # create folder
    def post(self, request):
        serializer = FolderSerializer(data=request.data, user=request.user)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class folder_detail(APIView):
    permission_classes = (IsAuthenticated,)

    # get folder detail
    def get(self, request, pk):
        folder = Folder.objects.get(id=pk)
        folder_serializer = FolderSerializer(folder)

        files = folder.folder_files.all()
        file_serializer = FileSerializer(files, many=True)

        context = [folder_serializer.data, file_serializer.data]
        return Response(context)

    # rename folder
    def patch(self, request, pk):
        folder = get_object(pk, 0)
        folder.name = request.data["name"]
        folder.save()
        return Response(status=status.HTTP_200_OK)


class create_file(APIView):
    permission_classes = (IsAuthenticated,)

    # create file
    def post(self, request):
        parser_classes = (MultiPartParser,)  # NOQA

        serializer = FileSerializer(data=request.data, user=request.user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class file_ops(APIView):
    permission_classes = (IsAuthenticated,)

    # get file detail
    def get(self, request, pk):
        file = get_object(pk, 1)
        serializer = FileSerializer(file)
        return Response(serializer.data)

    # rename file
    def patch(self, request, pk):
        selected_file = get_object(pk, 1)
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

    # delete file
    def delete(self, request, pk):
        file = get_object(pk, 1)
        file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # move file
    def put(self, request, pk, folder_pk):
        selected_file = get_object(pk, 1)
        selected_file.folder = Folder.objects.get(pk=folder_pk)
        selected_file.save()
        return Response(status=status.HTTP_200_OK)

    # copy file
    def post(self, request, pk):
        selected_file = get_object(pk, 1)
        file_copy = ContentFile(selected_file.file.read())
        new_file_name, ext = selected_file.file.name.split(".")
        new_file = File_Model(folder=selected_file.folder, user=selected_file.user)
        new_file.file.save(
            new_file_name.split("/")[-1] + "-copy" + "." + ext, file_copy
        )
        return Response(status=status.HTTP_201_CREATED)

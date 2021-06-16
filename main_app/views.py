import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.http import Http404
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.models import File as File_Model
from main_app.models import Folder
from main_app.models import StorageDetails
from main_app.serializers import FileSerializer
from main_app.serializers import FolderSerializer
from main_app.serializers import UserSerializer


def get_object(user, pk, pk_type):
    try:
        if pk_type:
            retreived_obj = File_Model.objects.get(file_id=pk)
            if retreived_obj.user == user:
                return retreived_obj
        else:
            retreived_obj = Folder.objects.get(pk=pk)
            if retreived_obj.user == user:
                return retreived_obj
    except File_Model.DoesNotExist:
        raise Http404


class CreateAccount(APIView):
    def post(self, request):
        data = request.data

        # throws 409 conflict error if existing username detected
        if (data["username"],) in User.objects.values_list("username"):
            return Response(
                {"409": "Conflict", "duplicate error": "user already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        AccountSerializer = UserSerializer(
            data={
                "username": data["username"],
                "email": data["email"],
                "password": data["password"],
            }
        )

        if AccountSerializer.is_valid():
            AccountSerializer.save()
            return Response(AccountSerializer.data, status=status.HTTP_201_CREATED)
        return Response(AccountSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileSearchViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FileSerializer

    # search file by name
    def get_queryset(self, *args, **kwargs):
        params = self.request.query_params
        keyword = params.get("name")
        if keyword:
            query = File_Model.objects.filter(name__icontains=keyword)
            return query
        return Response(status=status.HTTP_400_BAD_REQUEST)


class folder_list(APIView):
    permission_classes = (IsAuthenticated,)

    # get list of folders
    def get(self, request):
        folders = Folder.objects.filter(folder=None, user=request.user)
        serializer = FolderSerializer(folders, many=True)
        return Response(serializer.data)

    # create folder
    def post(self, request):
        serializer = FolderSerializer(data=request.data)
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
        context = folder_serializer.data

        files = folder.folder_files.all()

        if files:
            file_serializer = FileSerializer(files, many=True)
            context += file_serializer.data
        return Response(context)

    # rename folder
    def patch(self, request, pk):
        folder = get_object(request.user, pk, 0)
        folder.name = request.data["name"]
        folder.save()
        return Response(status=status.HTTP_200_OK)


class create_file(APIView):
    permission_classes = (IsAuthenticated,)

    # create file
    def post(self, request):
        parser_classes = (MultiPartParser,)  # NOQA

        if (request.data["file"].name,) in File_Model.objects.filter(
            user=request.user
        ).values_list("name"):
            return Response("File already exists", status=status.HTTP_409_CONFLICT)

        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, name=request.data["file"].name)
            current_user = request.user
            if (current_user.id,) in StorageDetails.objects.values_list("user"):
                last_disk_value = float(
                    StorageDetails.objects.get(user=current_user).disk_usage
                )
                disk_obj = StorageDetails.objects.get(user=current_user)
                if float(serializer.data["size"].split()[0]) + last_disk_value > 1024:
                    return Response(
                        "Not enough space available", status=status.HTTP_403_FORBIDDEN
                    )
                disk_obj.disk_usage = round(
                    float(serializer.data["size"].split()[0]) + last_disk_value,
                    2,
                )
                disk_obj.save()
            else:
                StorageDetails.objects.create(
                    user=current_user,
                    disk_usage=(round(float(serializer.data["size"].split()[0]), 2)),
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class file_ops(APIView):
    permission_classes = (IsAuthenticated,)

    # get file detail
    def get(self, request, pk):
        file = get_object(request.user, pk, 1)
        serializer = FileSerializer(file)
        return Response(serializer.data)

    # rename file
    def patch(self, request, pk):
        selected_file = get_object(request.user, pk, 1)
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
        file = get_object(request.user, pk, 1)
        storage_obj = StorageDetails.objects.get(user=request.user)
        storage_obj.disk_usage -= file.file.size / (1024 * 1024)
        storage_obj.disk_usage = round(storage_obj.disk_usage, 2)
        storage_obj.save()
        file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # move file
    def put(self, request, pk, folder_pk):
        selected_file = get_object(request.user, pk, 1)
        selected_file.folder = Folder.objects.get(pk=folder_pk)
        selected_file.save()
        return Response(status=status.HTTP_200_OK)

    # copy file
    def post(self, request, pk):
        selected_file = get_object(request.user, pk, 1)
        file_copy = ContentFile(selected_file.file.read())
        current_user = request.user

        # check upload limit
        if (current_user.id,) in StorageDetails.objects.values_list("user"):
            last_disk_value = float(
                StorageDetails.objects.get(user=current_user).disk_usage
            )
            disk_obj = StorageDetails.objects.get(user=current_user)
            if selected_file.file.size / (1024 * 1024) + last_disk_value > 1024:
                return Response(
                    "Not enough space available", status=status.HTTP_403_FORBIDDEN
                )
            disk_obj.disk_usage = round(
                (selected_file.file.size / (1024 * 1024) + last_disk_value), 2
            )
            disk_obj.save()

            new_file_name, ext = selected_file.file.name.split(".")
            new_file = File_Model(folder=selected_file.folder, user=selected_file.user)
            new_file.file.save(
                new_file_name.split("/")[-1] + "-copy" + "." + ext, file_copy
            )
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

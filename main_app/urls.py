from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from main_app import views

urlpatterns = [
    path("folder_list/", views.folder_list.as_view()),
    path("folder_detail/<int:pk>/", views.folder_detail.as_view()),
    path("file_detail/<int:pk>/", views.file_detail.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

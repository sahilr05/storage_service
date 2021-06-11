from django.contrib import admin
from django.urls import include
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("main_app.urls"), name="main_app"),
    path("api-auth/", include("rest_framework.urls"), name="rest_framework"),
]

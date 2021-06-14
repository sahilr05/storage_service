from django.contrib import admin
from django.urls import include
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("main_app.urls"), name="main_app"),
    path("login/", obtain_auth_token, name="api_token_auth"),
]

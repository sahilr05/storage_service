from django.contrib import admin
from django.urls import include
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authtoken.views import obtain_auth_token

import main_app

schema_view = get_schema_view(
    openapi.Info(
        title="Cloud service API's",
        default_version="v1",
        description="Find all APIs below",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("main_app.urls"), name="main_app"),
    path("login/", obtain_auth_token, name="api_token_auth"),
    path(
        "register/", main_app.views.CreateAccount.as_view(), name="create_account"
    ),  # noqa
    # swagger ui
    path(
        "swagger-ui/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

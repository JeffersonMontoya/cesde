
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from cesde_api import authentication



schema_view = get_schema_view(
    openapi.Info(
        title="TinCode Docs",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.tincode.es",
        contact=openapi.Contact(email="chechemontoya1997@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cesde/', include('cesde_api.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('login/', authentication.login),
    path('register/', authentication.register),
    path('profile/', authentication.profile),
]

"""cyberboy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import re_path, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

# from apps.profiles.urls import profile_urls
# from apps.profiles import urls as profiles_urls
from apps.profiles.views import Profile, UploadCSVData

root_path = 'api'
all_urls = [
    # # profile APIs
    # path(f'{root_path}/v1/login', Profile.as_view(actions={'post': 'login'}),
    #      name="Login Request", ),
    path(f'{root_path}/v1/upload-csv', UploadCSVData.as_view(actions={'post': 'upload_csv'}),
         name="Upload CSV", ),
    # profile APIs
    path(f'{root_path}/v1/people/list', Profile.as_view(actions={'get': 'list_people'}),
         name="List People", ),
    path(f'{root_path}/v1/people/<uuid:person_id>',
         Profile.as_view(actions={'put': 'update_people',
                                  'delete': 'delete_people'}), name="Manage People", ),
    path(f'{root_path}/v1/people/add',
         Profile.as_view(actions={'post': 'add_people'}), name="Add People", ),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Cyberboy Inc",
        default_version='v1',
        description="",
        terms_of_service="",
    ),
    public=False,
    patterns=all_urls,
    # permission_classes=[permissions.IsAuthenticated],
)

urlpatterns = all_urls + [
    re_path('admin/', admin.site.urls),
    # re_path(r'^people/', ),
    re_path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='Documentation'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

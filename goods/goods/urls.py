from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf.urls.static import static
from django.conf import settings

from goods.goods.views import (AdCreateView, AdDetailView, AdEntireLook, AdFastLook,
                         AdListView, FindByFilter, TagAllLook)

schema_view = get_schema_view(
    openapi.Info(
        title="Avito Clone API",
        default_version="v1",
        description="Here you can see an all requests of API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

app_name = "ad"
urlpatterns = [
    # swagger docs
    path("api/v1/docs/", schema_view.with_ui("swagger", cache_timeout=0)),
    # creating a new ad
    path("api/v1/ad/create/", AdCreateView.as_view()),
    # list all of ads
    path("api/v1/ad/all/", AdListView.as_view()),
    # edit ad by primary key
    path("api/v1/ad/edit/<int:pk>/", AdDetailView.as_view()),
    # look at ad without incrementing view counter
    path("api/v1/ad/<int:pk>/", AdFastLook.as_view()),
    # look at entire ad
    path("api/v1/ad/full/<int:pk>/", AdEntireLook.as_view()),
    # list all of tags
    path("api/v1/tag/all/", TagAllLook.as_view()),
    # find an ad by filters
    path("api/v1/ad/select", FindByFilter.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

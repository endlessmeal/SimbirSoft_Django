from django.urls import path, include
from ad.views import *

app_name = 'ad'
urlpatterns = [
    path('ad/create/', AdCreateView.as_view())
]

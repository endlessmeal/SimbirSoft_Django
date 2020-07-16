from django.urls import path
from goods.views import *

app_name = 'ad'
urlpatterns = [
    path('api/v1/ad/create/', AdCreateView.as_view()),
    path('api/v1/ad/all/', AdListView.as_view()),
    path('api/v1/ad/edit/<int:pk>/', AdUpdateView.as_view()),
    path('api/v1/ad/<int:pk>/', AdFastLook.as_view()),
    path('api/v1/ad/full/<int:pk>/', AdEntireLook.as_view()),
]

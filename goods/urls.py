from django.urls import path
from goods.views import *

app_name = 'ad'
urlpatterns = [
    path('ad/create/', AdCreateView.as_view()),
    path('ad/all/', AdListView.as_view()),
    path('ad/edit/<int:pk>/', AdUpdateView.as_view()),
    path('ad/<int:pk>/', AdFastLook.as_view()),
    path('ad/full/<int:pk>/', AdEntireLook.as_view()),
]

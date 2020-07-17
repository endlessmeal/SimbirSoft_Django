from django.urls import path
from goods.views import *

app_name = 'ad'
urlpatterns = [
    path('api/v1/ad/create/', AdCreateView.as_view()),  # creating a new ad
    path('api/v1/ad/all/', AdListView.as_view()),  # list all of ads
    path('api/v1/ad/edit/<int:pk>/', AdDetailView.as_view()),  # edit ad by primary key
    path('api/v1/ad/<int:pk>/', AdFastLook.as_view()),  # look at ad without incrementing view counter
    path('api/v1/ad/full/<int:pk>/', AdEntireLook.as_view()),  # look at entire ad
    path('api/v1/tag/all/', TagAllLook.as_view()),  # list all of tags
    path('api/v1/ad/select', FindByPrice.as_view()),  # find an ad by price
    path('api/v1/tag/select', FindByTag.as_view()),  # find an ad by tag
]

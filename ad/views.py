from rest_framework import generics
from ad.serializers import AdDetail


class AdCreateView(generics.CreateAPIView):
    serializer_class = AdDetail

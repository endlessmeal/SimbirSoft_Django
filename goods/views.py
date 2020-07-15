from rest_framework import generics
from goods.serializers import AdDetailSerializer, AdListSerializerCut
from goods.models import Ad


# creating a new ad (POST)
class AdCreateView(generics.CreateAPIView):
    serializer_class = AdDetailSerializer


# get all ads by id, title, price, (GET)
class AdListView(generics.ListAPIView):
    serializer_class = AdListSerializerCut
    queryset = Ad.objects.all()


# update an ad or delete (PUT, DELETE)
class AdUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdDetailSerializer
    queryset = Ad.objects.all()


# get a fast look at ad without increment view counter
class AdFastLook(generics.RetrieveAPIView):
    serializer_class = AdListSerializerCut
    queryset = Ad.objects.all()

# get a fast look at ad without increment view counter
class AdEntireLook(generics.RetrieveAPIView):
    serializer_class = AdDetailSerializer
    queryset = Ad.objects.all()
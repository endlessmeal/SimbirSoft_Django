from rest_framework import generics
from goods.serializers import AdDetailSerializer, AdListSerializerCut
from goods.models import Ad
from django.db.models import F
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response


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


# get an entire look at ad with increment view counter
class AdEntireLook(APIView):
    def get_object(self, pk):
        try:
            ad_current = Ad.objects.get(pk=pk)
            ad_current.views = F('views') + 1
            ad_current.save()
            return Ad.objects.get(pk=pk)
        except Ad.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        ad = self.get_object(pk)
        serializer = AdDetailSerializer(ad)
        return Response(serializer.data)



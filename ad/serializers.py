from rest_framework import serializers
from ad.models import Ad


class AdDetail(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'

from rest_framework import serializers
from api.models import DailyData, Hist90Data, HistData


class DailyDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyData
        exclude = ('id',)

    def create(self, validated_data):
        return DailyData.objects.create(**validated_data)



class Hist90DataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hist90Data
        exclude = ('id',)

    def create(self, validated_data):
        return Hist90Data.objects.create(**validated_data)



class HistDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = HistData
        exclude = ('id',)

    def create(self, validated_data):
        return HistData.objects.create(**validated_data)

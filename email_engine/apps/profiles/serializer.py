from rest_framework import serializers
from .models import People
from ..core.serializers import BaseSerializer


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ('last_login','id',)
        model = People
        fields = '__all__'


class UUIDSerializer(BaseSerializer):
    id = serializers.UUIDField(required=True)

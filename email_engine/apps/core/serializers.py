from rest_framework import serializers
from drf_yasg import openapi
from django.http import JsonResponse

from apps.core.exceptions import RequestValidationError


class GenericErrorSerializer(serializers.Serializer):
    success = serializers.BooleanField(required=True)
    error_msg = serializers.CharField(max_length=100, required=True)
    error_config = serializers.DictField(required=False)
    exception_name = serializers.CharField(max_length=100, required=False)


class GenericResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = serializers.DictField()


error_response = openapi.Response('Generic Error Serializer', GenericErrorSerializer)
success_response = openapi.Response('Generic Response Serializer', GenericResponseSerializer)


def custom_response(model_name, serializer):
    return openapi.Response(model_name, serializer)


def error_json_response(data):
    return JsonResponse(
        data=data,
        status=503,
    )


def response_400(exception: Exception):
    return JsonResponse(
        data={
            "success": False,
            "error_msg": str(exception),
            "error_config": exception.config() if hasattr(exception, 'config') else None,
            "exception_name": str(exception.__class__.__name__),
        },
        status=400,
    )


def response_200(data: dict):
    return JsonResponse(
        data={
            "success": True,
            "data": data,
        }
    )


class BaseSerializer(serializers.Serializer):
    @classmethod
    def validate_and_map(cls, data, many=False):
        ser = cls(data=data, many=many)
        if ser.is_valid():
            return ser.data
        raise RequestValidationError(str(cls.__name__), ser.errors)

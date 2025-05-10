from rest_framework import serializers
from .models import (
    Domain,
    ApiEndpoint,
    RequestTransformation,
    ResponseTransformation,
    ApiLog,
)


class RequestTransformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestTransformation
        fields = [
            "id",
            "endpoint",
            "source_field",
            "target_field",
            "transformation_type",
            "transformation_value",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ResponseTransformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseTransformation
        fields = [
            "id",
            "endpoint",
            "source_field",
            "target_field",
            "transformation_type",
            "transformation_value",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ApiEndpointSerializer(serializers.ModelSerializer):
    request_transformations = RequestTransformationSerializer(many=True, read_only=True)
    response_transformations = ResponseTransformationSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = ApiEndpoint
        fields = [
            "id",
            "domain",
            "path",
            "method",
            "target_url",
            "timeout",
            "is_active",
            "created_at",
            "updated_at",
            "request_transformations",
            "response_transformations",
        ]


class DomainSerializer(serializers.ModelSerializer):
    endpoints = ApiEndpointSerializer(many=True, read_only=True)

    class Meta:
        model = Domain
        fields = [
            "id",
            "name",
            "base_url",
            "description",
            "is_active",
            "created_at",
            "updated_at",
            "endpoints",
        ]


class ApiLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiLog
        fields = [
            "id",
            "endpoint",
            "request_method",
            "request_path",
            "request_headers",
            "request_body",
            "response_status",
            "response_headers",
            "response_body",
            "execution_time",
            "created_at",
        ]
        read_only_fields = fields

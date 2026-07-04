from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""
    detail = serializers.CharField()
    code = serializers.CharField(required=False)

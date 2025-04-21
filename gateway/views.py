from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Domain, ApiEndpoint, RequestTransformation, ResponseTransformation, ApiLog
from .serializers import (
    DomainSerializer, ApiEndpointSerializer, 
    RequestTransformationSerializer, ResponseTransformationSerializer,
    ApiLogSerializer
)

class DomainViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing domains.
    """
    queryset = Domain.objects.all().order_by('name')
    serializer_class = DomainSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'base_url', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    @action(detail=True, methods=['get'])
    def endpoints(self, request, pk=None):
        """Get all endpoints for a domain"""
        domain = self.get_object()
        endpoints = domain.endpoints.all()
        serializer = ApiEndpointSerializer(endpoints, many=True)
        return Response(serializer.data)

class ApiEndpointViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing API endpoints.
    """
    queryset = ApiEndpoint.objects.all().order_by('domain__name', 'path')
    serializer_class = ApiEndpointSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['domain__name', 'path', 'method', 'target_url']
    ordering_fields = ['domain__name', 'path', 'method', 'created_at', 'updated_at']
    
    @action(detail=True, methods=['get'])
    def request_transformations(self, request, pk=None):
        """Get all request transformations for an endpoint"""
        endpoint = self.get_object()
        transformations = endpoint.request_transformations.all()
        serializer = RequestTransformationSerializer(transformations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def response_transformations(self, request, pk=None):
        """Get all response transformations for an endpoint"""
        endpoint = self.get_object()
        transformations = endpoint.response_transformations.all()
        serializer = ResponseTransformationSerializer(transformations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get all logs for an endpoint"""
        endpoint = self.get_object()
        logs = endpoint.logs.all().order_by('-created_at')[:100]  # Limit to last 100 logs
        serializer = ApiLogSerializer(logs, many=True)
        return Response(serializer.data)

class RequestTransformationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing request transformations.
    """
    queryset = RequestTransformation.objects.all().order_by('endpoint__domain__name', 'endpoint__path')
    serializer_class = RequestTransformationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['endpoint__domain__name', 'endpoint__path', 'source_field', 'target_field']
    ordering_fields = ['endpoint__domain__name', 'endpoint__path', 'created_at', 'updated_at']

class ResponseTransformationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing response transformations.
    """
    queryset = ResponseTransformation.objects.all().order_by('endpoint__domain__name', 'endpoint__path')
    serializer_class = ResponseTransformationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['endpoint__domain__name', 'endpoint__path', 'source_field', 'target_field']
    ordering_fields = ['endpoint__domain__name', 'endpoint__path', 'created_at', 'updated_at']

class ApiLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing API logs.
    """
    queryset = ApiLog.objects.all().order_by('-created_at')
    serializer_class = ApiLogSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['endpoint__domain__name', 'endpoint__path', 'request_method', 'request_path', 'response_status']
    ordering_fields = ['created_at', 'execution_time', 'response_status']

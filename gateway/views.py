from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
import time

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


# Web Interface Views
def dashboard(request):
    domains_count = Domain.objects.filter(is_active=True).count()
    endpoints_count = ApiEndpoint.objects.filter(is_active=True).count()
    transformations_count = RequestTransformation.objects.filter(is_active=True).count() + ResponseTransformation.objects.filter(is_active=True).count()
    logs_count = ApiLog.objects.count()
    
    recent_endpoints = ApiEndpoint.objects.all().order_by('-updated_at')[:5]
    recent_logs = ApiLog.objects.all().order_by('-created_at')[:5]
    
    context = {
        'domains_count': domains_count,
        'endpoints_count': endpoints_count,
        'transformations_count': transformations_count,
        'logs_count': logs_count,
        'recent_endpoints': recent_endpoints,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'gateway/dashboard.html', context)


def rules_list(request):
    endpoints = ApiEndpoint.objects.all().order_by('-updated_at')
    
    context = {
        'endpoints': endpoints,
    }
    
    return render(request, 'gateway/rules.html', context)


def logs_list(request):
    logs = ApiLog.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(logs, 20)  # Show 20 logs per page
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'gateway/logs.html', context)


def create_rule(request):
    if request.method == 'POST':
        # Extract form data
        domain_id = request.POST.get('domain')
        method = request.POST.get('method')
        path = request.POST.get('path')
        target_url = request.POST.get('target_url')
        timeout = request.POST.get('timeout')
        is_active = request.POST.get('is_active') == 'on'
        
        # Create endpoint
        domain = get_object_or_404(Domain, id=domain_id)
        endpoint = ApiEndpoint.objects.create(
            domain=domain,
            method=method,
            path=path,
            target_url=target_url,
            timeout=int(timeout),
            is_active=is_active
        )
        
        # Process request transformations
        req_source_fields = request.POST.getlist('req_source_field[]')
        req_target_fields = request.POST.getlist('req_target_field[]')
        req_transform_types = request.POST.getlist('req_transform_type[]')
        req_transform_values = request.POST.getlist('req_transform_value[]')
        
        for i in range(len(req_source_fields)):
            if req_source_fields[i] and req_target_fields[i]:
                RequestTransformation.objects.create(
                    endpoint=endpoint,
                    source_field=req_source_fields[i],
                    target_field=req_target_fields[i],
                    transformation_type=req_transform_types[i],
                    transformation_value=req_transform_values[i] if i < len(req_transform_values) else '',
                    is_active=True
                )
        
        # Process response transformations
        res_source_fields = request.POST.getlist('res_source_field[]')
        res_target_fields = request.POST.getlist('res_target_field[]')
        res_transform_types = request.POST.getlist('res_transform_type[]')
        res_transform_values = request.POST.getlist('res_transform_value[]')
        
        for i in range(len(res_source_fields)):
            if res_source_fields[i] and res_target_fields[i]:
                ResponseTransformation.objects.create(
                    endpoint=endpoint,
                    source_field=res_source_fields[i],
                    target_field=res_target_fields[i],
                    transformation_type=res_transform_types[i],
                    transformation_value=res_transform_values[i] if i < len(res_transform_values) else '',
                    is_active=True
                )
        
        messages.success(request, 'Rule created successfully!')
        return redirect('gateway:rules')
    
    domains = Domain.objects.filter(is_active=True)
    
    context = {
        'domains': domains,
    }
    
    return render(request, 'gateway/rule_form.html', context)


def edit_rule(request, endpoint_id):
    endpoint = get_object_or_404(ApiEndpoint, id=endpoint_id)
    
    if request.method == 'POST':
        # Extract form data
        domain_id = request.POST.get('domain')
        method = request.POST.get('method')
        path = request.POST.get('path')
        target_url = request.POST.get('target_url')
        timeout = request.POST.get('timeout')
        is_active = request.POST.get('is_active') == 'on'
        
        # Update endpoint
        domain = get_object_or_404(Domain, id=domain_id)
        endpoint.domain = domain
        endpoint.method = method
        endpoint.path = path
        endpoint.target_url = target_url
        endpoint.timeout = int(timeout)
        endpoint.is_active = is_active
        endpoint.save()
        
        # Process request transformations
        req_transform_ids = request.POST.getlist('req_transform_id[]')
        req_source_fields = request.POST.getlist('req_source_field[]')
        req_target_fields = request.POST.getlist('req_target_field[]')
        req_transform_types = request.POST.getlist('req_transform_type[]')
        req_transform_values = request.POST.getlist('req_transform_value[]')
        
        # Delete existing transformations not in the form
        existing_req_ids = [int(id) for id in req_transform_ids if id]
        RequestTransformation.objects.filter(endpoint=endpoint).exclude(id__in=existing_req_ids).delete()
        
        for i in range(len(req_source_fields)):
            if req_source_fields[i] and req_target_fields[i]:
                transform_id = req_transform_ids[i] if i < len(req_transform_ids) and req_transform_ids[i] else None
                
                if transform_id:
                    # Update existing transformation
                    transform = get_object_or_404(RequestTransformation, id=transform_id)
                    transform.source_field = req_source_fields[i]
                    transform.target_field = req_target_fields[i]
                    transform.transformation_type = req_transform_types[i]
                    transform.transformation_value = req_transform_values[i] if i < len(req_transform_values) else ''
                    transform.save()
                else:
                    # Create new transformation
                    RequestTransformation.objects.create(
                        endpoint=endpoint,
                        source_field=req_source_fields[i],
                        target_field=req_target_fields[i],
                        transformation_type=req_transform_types[i],
                        transformation_value=req_transform_values[i] if i < len(req_transform_values) else '',
                        is_active=True
                    )
        
        # Process response transformations
        res_transform_ids = request.POST.getlist('res_transform_id[]')
        res_source_fields = request.POST.getlist('res_source_field[]')
        res_target_fields = request.POST.getlist('res_target_field[]')
        res_transform_types = request.POST.getlist('res_transform_type[]')
        res_transform_values = request.POST.getlist('res_transform_value[]')
        
        # Delete existing transformations not in the form
        existing_res_ids = [int(id) for id in res_transform_ids if id]
        ResponseTransformation.objects.filter(endpoint=endpoint).exclude(id__in=existing_res_ids).delete()
        
        for i in range(len(res_source_fields)):
            if res_source_fields[i] and res_target_fields[i]:
                transform_id = res_transform_ids[i] if i < len(res_transform_ids) and res_transform_ids[i] else None
                
                if transform_id:
                    # Update existing transformation
                    transform = get_object_or_404(ResponseTransformation, id=transform_id)
                    transform.source_field = res_source_fields[i]
                    transform.target_field = res_target_fields[i]
                    transform.transformation_type = res_transform_types[i]
                    transform.transformation_value = res_transform_values[i] if i < len(res_transform_values) else ''
                    transform.save()
                else:
                    # Create new transformation
                    ResponseTransformation.objects.create(
                        endpoint=endpoint,
                        source_field=res_source_fields[i],
                        target_field=res_target_fields[i],
                        transformation_type=res_transform_types[i],
                        transformation_value=res_transform_values[i] if i < len(res_transform_values) else '',
                        is_active=True
                    )
        
        messages.success(request, 'Rule updated successfully!')
        return redirect('gateway:rules')
    
    domains = Domain.objects.filter(is_active=True)
    
    context = {
        'endpoint': endpoint,
        'domains': domains,
    }
    
    return render(request, 'gateway/rule_form.html', context)


def toggle_rule(request, endpoint_id):
    endpoint = get_object_or_404(ApiEndpoint, id=endpoint_id)
    endpoint.is_active = not endpoint.is_active
    endpoint.save()
    
    status = 'enabled' if endpoint.is_active else 'disabled'
    messages.success(request, f'Rule {status} successfully!')
    
    return redirect('gateway:rules')


def delete_rule(request, endpoint_id):
    endpoint = get_object_or_404(ApiEndpoint, id=endpoint_id)
    endpoint.delete()
    
    messages.success(request, 'Rule deleted successfully!')
    
    return redirect('gateway:rules')


def clear_logs(request):
    ApiLog.objects.all().delete()
    
    messages.success(request, 'Logs cleared successfully!')
    
    return redirect('gateway:logs')


@csrf_exempt
def create_domain_ajax(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'true'
        
        # Check if domain already exists
        if Domain.objects.filter(name=name).exists():
            return JsonResponse({
                'success': False,
                'error': f'Domain "{name}" already exists'
            })
        
        # Create domain
        domain = Domain.objects.create(
            name=name,
            description=description,
            is_active=is_active
        )
        
        return JsonResponse({
            'success': True,
            'domain': {
                'id': domain.id,
                'name': domain.name
            }
        })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


def log_detail_ajax(request):
    log_id = request.GET.get('log_id')
    
    if not log_id:
        return JsonResponse({
            'success': False,
            'error': 'Log ID is required'
        })
    
    try:
        log = ApiLog.objects.get(id=log_id)
        
        return JsonResponse({
            'success': True,
            'log': {
                'id': log.id,
                'host': log.host,
                'path': log.path,
                'method': log.method,
                'status_code': log.status_code,
                'response_time': log.response_time,
                'request_headers': log.request_headers,
                'request_body': log.request_body,
                'response_headers': log.response_headers,
                'response_body': log.response_body,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except ApiLog.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Log not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

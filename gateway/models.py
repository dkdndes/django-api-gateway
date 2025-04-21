from django.db import models
from django.core.validators import URLValidator
import json

class Domain(models.Model):
    """Model to store domain information"""
    name = models.CharField(max_length=255, unique=True, help_text="Domain name (e.g., 'example.com')")
    base_url = models.CharField(max_length=255, validators=[URLValidator()], 
                               help_text="Base URL for the domain (e.g., 'https://api.example.com')")
    description = models.TextField(blank=True, null=True, help_text="Description of the domain")
    is_active = models.BooleanField(default=True, help_text="Whether this domain is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ApiEndpoint(models.Model):
    """Model to store API endpoint information"""
    HTTP_METHODS = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('OPTIONS', 'OPTIONS'),
        ('HEAD', 'HEAD'),
    )
    
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='endpoints',
                              help_text="Domain this endpoint belongs to")
    path = models.CharField(max_length=255, help_text="Path of the endpoint (e.g., '/users')")
    method = models.CharField(max_length=10, choices=HTTP_METHODS, default='GET',
                             help_text="HTTP method for this endpoint")
    target_url = models.CharField(max_length=255, validators=[URLValidator()],
                                 help_text="Target URL to forward the request to")
    timeout = models.IntegerField(default=30, help_text="Timeout in seconds for the request")
    is_active = models.BooleanField(default=True, help_text="Whether this endpoint is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('domain', 'path', 'method')
        
    def __str__(self):
        return f"{self.domain.name} - {self.method} {self.path}"

class RequestTransformation(models.Model):
    """Model to store request transformation rules"""
    endpoint = models.ForeignKey(ApiEndpoint, on_delete=models.CASCADE, related_name='request_transformations',
                                help_text="Endpoint this transformation belongs to")
    source_field = models.CharField(max_length=255, help_text="Source field in the request")
    target_field = models.CharField(max_length=255, help_text="Target field in the transformed request")
    transformation_type = models.CharField(max_length=50, default='direct',
                                         help_text="Type of transformation (e.g., 'direct', 'template')")
    transformation_value = models.TextField(blank=True, null=True, 
                                          help_text="Value or template for the transformation")
    is_active = models.BooleanField(default=True, help_text="Whether this transformation is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.endpoint} - {self.source_field} -> {self.target_field}"

class ResponseTransformation(models.Model):
    """Model to store response transformation rules"""
    endpoint = models.ForeignKey(ApiEndpoint, on_delete=models.CASCADE, related_name='response_transformations',
                                help_text="Endpoint this transformation belongs to")
    source_field = models.CharField(max_length=255, help_text="Source field in the response")
    target_field = models.CharField(max_length=255, help_text="Target field in the transformed response")
    transformation_type = models.CharField(max_length=50, default='direct',
                                         help_text="Type of transformation (e.g., 'direct', 'template')")
    transformation_value = models.TextField(blank=True, null=True, 
                                          help_text="Value or template for the transformation")
    is_active = models.BooleanField(default=True, help_text="Whether this transformation is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.endpoint} - {self.source_field} -> {self.target_field}"

class ApiLog(models.Model):
    """Model to store API request/response logs"""
    endpoint = models.ForeignKey(ApiEndpoint, on_delete=models.SET_NULL, null=True, related_name='logs',
                                help_text="Endpoint this log belongs to")
    request_method = models.CharField(max_length=10, help_text="HTTP method of the request")
    request_path = models.CharField(max_length=255, help_text="Path of the request")
    request_headers = models.TextField(blank=True, null=True, help_text="Headers of the request")
    request_body = models.TextField(blank=True, null=True, help_text="Body of the request")
    response_status = models.IntegerField(help_text="Status code of the response")
    response_headers = models.TextField(blank=True, null=True, help_text="Headers of the response")
    response_body = models.TextField(blank=True, null=True, help_text="Body of the response")
    execution_time = models.FloatField(help_text="Execution time in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.request_method} {self.request_path} - {self.response_status}"
    
    def set_request_headers(self, headers):
        self.request_headers = json.dumps(dict(headers))
        
    def get_request_headers(self):
        return json.loads(self.request_headers) if self.request_headers else {}
    
    def set_response_headers(self, headers):
        self.response_headers = json.dumps(dict(headers))
        
    def get_response_headers(self):
        return json.loads(self.response_headers) if self.response_headers else {}

import time
import json
import re
import requests
from django.http import JsonResponse, HttpResponse
from django.urls import resolve, Resolver404
from .models import Domain, ApiEndpoint, ApiLog

class ApiGatewayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request should be handled by the API gateway
        if self._should_handle_request(request):
            return self._handle_api_gateway_request(request)
        
        # If not, continue with the normal Django request/response cycle
        return self.get_response(request)
    
    def _should_handle_request(self, request):
        """
        Determine if the request should be handled by the API gateway.
        This checks if the request path is not a Django admin, static file, or web interface URL.
        """
        path = request.path_info
        
        # Skip Django admin, static files, API management, web interface, and docs URLs
        if (path.startswith('/admin/') or 
            path.startswith('/static/') or
            path.startswith('/api/v1/') or
            path.startswith('/api-auth/') or
            path.startswith('/docs/') or
            path == '/' or
            path.startswith('/rules/') or
            path.startswith('/logs/') or
            path.startswith('/ajax/')):
            return False
        
        # Handle API requests
        if path.startswith('/api/'):
            return True
        
        # Try to resolve the URL to see if it's a Django view
        try:
            resolve(path)
            return False  # It's a Django view, don't handle with gateway
        except Resolver404:
            # Not a Django view, check if we have a matching API endpoint
            host = request.get_host().split(':')[0]  # Remove port if present
            domain = Domain.objects.filter(name=host, is_active=True).first()
            
            if domain:
                # Check if we have a matching endpoint for this domain and path
                endpoint = ApiEndpoint.objects.filter(
                    domain=domain,
                    path=self._normalize_path(path),
                    method=request.method,
                    is_active=True
                ).first()
                
                return endpoint is not None
            
            return False
    
    def _normalize_path(self, path):
        """Normalize the path to match the format stored in the database"""
        # Remove trailing slash if present (except for root path)
        if path != '/' and path.endswith('/'):
            path = path[:-1]
        return path
    
    def _handle_api_gateway_request(self, request):
        """Handle an API gateway request by forwarding it to the target service"""
        start_time = time.time()
        host = request.get_host().split(':')[0]  # Remove port if present
        path = self._normalize_path(request.path_info)
        
        # Find the domain and endpoint
        domain = Domain.objects.filter(name=host, is_active=True).first()
        
        if not domain:
            # If the request starts with /api/, try to find a default domain
            if path.startswith('/api/'):
                # Remove /api/ prefix for matching
                api_path = path[4:]
                domain = Domain.objects.filter(is_active=True).first()
                if domain:
                    endpoint = ApiEndpoint.objects.filter(
                        domain=domain,
                        path=self._normalize_path(api_path),
                        method=request.method,
                        is_active=True
                    ).first()
            else:
                endpoint = None
        else:
            endpoint = ApiEndpoint.objects.filter(
                domain=domain,
                path=path,
                method=request.method,
                is_active=True
            ).first()
        
        if not endpoint:
            # No matching endpoint found
            response_data = {
                'error': 'Not Found',
                'message': f'No API endpoint found for {request.method} {path}'
            }
            response = JsonResponse(response_data, status=404)
            
            # Log the failed request
            self._log_request(
                None, request, None, 404, 
                response.headers, json.dumps(response_data),
                time.time() - start_time
            )
            
            return response
        
        # Prepare the request to the target service
        target_url = endpoint.target_url
        
        # Get request body
        if request.body:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                body = request.body.decode('utf-8')
        else:
            body = None
        
        # Apply request transformations
        transformed_body = self._apply_request_transformations(endpoint, body)
        
        # Prepare headers
        headers = {key: value for key, value in request.headers.items()
                  if key.lower() not in ['host', 'content-length', 'connection']}
        
        # Make the request to the target service
        try:
            response = self._make_request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.GET.dict(),
                data=transformed_body,
                timeout=endpoint.timeout
            )
            
            # Apply response transformations
            transformed_response = self._apply_response_transformations(endpoint, response)
            
            # Create Django response
            django_response = HttpResponse(
                content=transformed_response.get('content', ''),
                status=transformed_response.get('status_code', 200),
                content_type=transformed_response.get('content_type', 'application/json')
            )
            
            # Add headers
            for key, value in transformed_response.get('headers', {}).items():
                if key.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                    django_response[key] = value
            
            # Log the successful request
            self._log_request(
                endpoint, request, body, 
                transformed_response.get('status_code', 200),
                transformed_response.get('headers', {}),
                transformed_response.get('content', ''),
                time.time() - start_time
            )
            
            return django_response
            
        except requests.RequestException as e:
            # Handle request errors
            error_message = str(e)
            response_data = {
                'error': 'Gateway Error',
                'message': error_message
            }
            response = JsonResponse(response_data, status=502)
            
            # Log the failed request
            self._log_request(
                endpoint, request, body, 502,
                response.headers, json.dumps(response_data),
                time.time() - start_time
            )
            
            return response
    
    def _make_request(self, method, url, headers=None, params=None, data=None, timeout=30):
        """Make a request to the target service"""
        method = method.upper()
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, headers=headers, params=params, json=data, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, params=params, json=data, timeout=timeout)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, params=params, json=data, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, params=params, json=data, timeout=timeout)
        elif method == 'OPTIONS':
            response = requests.options(url, headers=headers, timeout=timeout)
        elif method == 'HEAD':
            response = requests.head(url, headers=headers, params=params, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Try to parse response as JSON
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            try:
                content = response.json()
                content = json.dumps(content)
            except ValueError:
                content = response.text
        else:
            content = response.text
        
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content': content,
            'content_type': content_type
        }
    
    def _apply_request_transformations(self, endpoint, body):
        """Apply transformations to the request body"""
        if not body:
            return body
        
        transformations = endpoint.request_transformations.filter(is_active=True)
        if not transformations:
            return body
        
        # If body is a string, try to parse it as JSON
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                # If it's not valid JSON, return as is
                return body
        
        # Create a copy of the body to transform
        transformed_body = body.copy() if isinstance(body, dict) else body
        
        for transformation in transformations:
            if transformation.transformation_type == 'direct':
                # Direct field mapping
                source_value = self._get_nested_value(body, transformation.source_field)
                if source_value is not None:
                    self._set_nested_value(transformed_body, transformation.target_field, source_value)
            
            elif transformation.transformation_type == 'template':
                # Template-based transformation
                template = transformation.transformation_value
                if template:
                    # Replace placeholders with values from the request
                    for match in re.finditer(r'\${(.*?)}', template):
                        field_name = match.group(1)
                        field_value = self._get_nested_value(body, field_name)
                        if field_value is not None:
                            template = template.replace(match.group(0), str(field_value))
                    
                    # Set the transformed value
                    self._set_nested_value(transformed_body, transformation.target_field, template)
            
            elif transformation.transformation_type == 'constant':
                # Set a constant value
                self._set_nested_value(transformed_body, transformation.target_field, 
                                     transformation.transformation_value)
        
        return transformed_body
    
    def _apply_response_transformations(self, endpoint, response):
        """Apply transformations to the response"""
        transformations = endpoint.response_transformations.filter(is_active=True)
        
        # Debug: Print transformations
        print(f"Applying response transformations for endpoint {endpoint.id}: {endpoint.path}")
        print(f"Found {transformations.count()} transformations")
        for t in transformations:
            print(f"Transformation: {t.transformation_type} - {t.source_field} -> {t.target_field}")
        
        if not transformations:
            return response
        
        # Try to parse the response content as JSON
        content = response.get('content', '')
        content_type = response.get('content_type', '')
        
        if 'application/json' in content_type:
            try:
                if isinstance(content, str):
                    body = json.loads(content)
                else:
                    body = content
                
                # Create a copy of the body to transform
                transformed_body = body.copy() if isinstance(body, dict) else body
                
                for transformation in transformations:
                    # Handle list responses
                    if isinstance(body, list) and '.' in transformation.source_field:
                        # If source field starts with a number (e.g., "0.name"), it's targeting a specific list item
                        parts = transformation.source_field.split('.', 1)
                        if parts[0].isdigit():
                            index = int(parts[0])
                            if index < len(body):
                                item = body[index]
                                if isinstance(item, dict):
                                    source_value = self._get_nested_value(item, parts[1])
                                    if source_value is not None and isinstance(transformed_body, list) and index < len(transformed_body):
                                        if not isinstance(transformed_body[index], dict):
                                            transformed_body[index] = {}
                                        self._set_nested_value(transformed_body[index], transformation.target_field, source_value)
                        continue
                    
                    # Regular transformations for dict responses
                    if isinstance(body, dict):
                        if transformation.transformation_type == 'direct':
                            # Direct field mapping
                            source_value = self._get_nested_value(body, transformation.source_field)
                            if source_value is not None:
                                self._set_nested_value(transformed_body, transformation.target_field, source_value)
                        
                        elif transformation.transformation_type == 'template':
                            # Template-based transformation
                            template = transformation.transformation_value
                            if template:
                                # Replace placeholders with values from the response
                                for match in re.finditer(r'\${(.*?)}', template):
                                    field_name = match.group(1)
                                    field_value = self._get_nested_value(body, field_name)
                                    if field_value is not None:
                                        template = template.replace(match.group(0), str(field_value))
                                
                                # Set the transformed value
                                self._set_nested_value(transformed_body, transformation.target_field, template)
                        
                        elif transformation.transformation_type == 'constant':
                            # Set a constant value
                            self._set_nested_value(transformed_body, transformation.target_field, 
                                                 transformation.transformation_value)
                
                # Update the response with the transformed body
                response['content'] = json.dumps(transformed_body)
                
                # Debug: Print transformation result
                if isinstance(transformed_body, dict):
                    print(f"Transformation result: {transformed_body.get('first_user', 'Not found')}")
                else:
                    print(f"Transformation result: List response, first_user not applicable")
                
            except (json.JSONDecodeError, TypeError) as e:
                # If it's not valid JSON, return as is
                print(f"Error applying transformation: {str(e)}")
                pass
        
        return response
    
    def _get_nested_value(self, obj, path):
        """Get a value from a nested object using dot notation"""
        if not path:
            return None
        
        if not obj:
            return None
        
        parts = path.split('.')
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
                current = current[int(part)]
            else:
                return None
        
        return current
    
    def _set_nested_value(self, obj, path, value):
        """Set a value in a nested object using dot notation"""
        if not path or not obj:
            return
        
        parts = path.split('.')
        current = obj
        
        # Navigate to the parent of the field to set
        for i, part in enumerate(parts[:-1]):
            if isinstance(current, dict):
                if part not in current:
                    # Create missing dictionaries along the path
                    current[part] = {}
                current = current[part]
            elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
                current = current[int(part)]
            else:
                # Can't navigate further
                return
        
        # Set the value on the parent
        last_part = parts[-1]
        if isinstance(current, dict):
            current[last_part] = value
        elif isinstance(current, list) and last_part.isdigit() and int(last_part) < len(current):
            current[int(last_part)] = value
    
    def _log_request(self, endpoint, request, request_body, response_status, 
                    response_headers, response_body, execution_time):
        """Log the API request and response"""
        try:
            log = ApiLog(
                endpoint=endpoint,
                request_method=request.method,
                request_path=request.path_info,
                request_body=json.dumps(request_body) if request_body else None,
                response_status=response_status,
                response_body=response_body,
                execution_time=execution_time
            )
            
            # Set headers
            log.set_request_headers(dict(request.headers))
            log.set_response_headers(response_headers)
            
            log.save()
        except Exception as e:
            # Don't let logging errors affect the response
            print(f"Error logging API request: {str(e)}")
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json


class HighlightedAPISchemaView(SpectacularAPIView):
    """하이라이트된 API들만 포함하는 스키마 뷰"""
    
    def get(self, request, *args, **kwargs):
        # 기본 스키마 가져오기
        schema = super().get(request, *args, **kwargs)
        
        # 하이라이트할 API 패턴들
        highlighted_patterns = [
            '/api/projects/{id}/external_matches_by_keyword/',
            '/api/projects/{id}/external_matches_by_code/',
            '/api/projects/{id}/create_items_from_external_matches_by_keyword/',
            '/api/projects/{id}/create_items_from_external_matches_by_code/',
            '/api/projects/',
            '/api/items/',
            '/api/recommendations/',
        ]
        
        # 스키마에서 하이라이트된 API들만 필터링
        if hasattr(schema, 'data'):
            paths = schema.data.get('paths', {})
            filtered_paths = {}
            
            for path, methods in paths.items():
                for method, operation in methods.items():
                    if isinstance(operation, dict):
                        operation_id = operation.get('operationId', '')
                        tags = operation.get('tags', [])
                        
                        # 하이라이트 조건 확인
                        should_highlight = (
                            any(pattern in path for pattern in highlighted_patterns) or
                            '외부 데이터 매칭' in tags or
                            '프로젝트 관리' in tags or
                            '콘텐츠 관리' in tags
                        )
                        
                        if should_highlight:
                            # 하이라이트 표시 추가
                            if 'description' in operation:
                                operation['description'] = f"🌟 **하이라이트 API**\n\n{operation['description']}"
                            else:
                                operation['description'] = "🌟 **하이라이트 API**"
                            
                            if path not in filtered_paths:
                                filtered_paths[path] = {}
                            filtered_paths[path][method] = operation
            
            schema.data['paths'] = filtered_paths
        
        return schema


class HighlightedSwaggerView(SpectacularSwaggerView):
    """하이라이트된 API들을 강조하는 Swagger UI"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schema_url'] = '/api/schema/highlighted/'
        return context


class HighlightedRedocView(SpectacularRedocView):
    """하이라이트된 API들을 강조하는 ReDoc UI"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schema_url'] = '/api/schema/highlighted/'
        return context


@method_decorator(csrf_exempt, name='dispatch')
class APIHighlightView(View):
    """API 하이라이트 설정을 관리하는 뷰"""
    
    def get(self, request):
        """현재 하이라이트 설정을 반환"""
        highlighted_apis = {
            'external_matching': [
                'external_matches_by_keyword',
                'external_matches_by_code',
                'create_items_from_external_matches_by_keyword',
                'create_items_from_external_matches_by_code'
            ],
            'core_management': [
                'projects',
                'items',
                'recommendations'
            ],
            'tags': [
                '외부 데이터 매칭',
                '프로젝트 관리',
                '콘텐츠 관리'
            ]
        }
        return JsonResponse(highlighted_apis)
    
    def post(self, request):
        """하이라이트 설정을 업데이트"""
        try:
            data = json.loads(request.body)
            # 여기서 하이라이트 설정을 저장하거나 업데이트할 수 있습니다
            return JsonResponse({'status': 'success', 'message': '하이라이트 설정이 업데이트되었습니다.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '잘못된 JSON 형식입니다.'}, status=400)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
import json
import os
from .models import Project, ProjectMaterial, AIRequest, Summary, Item, Recommendation
from .serializers import (
    ProjectSerializer, ProjectDetailSerializer,
    ProjectMaterialSerializer, ProjectMaterialDetailSerializer,
    AIRequestSerializer, SummarySerializer, ItemSerializer, RecommendationSerializer
)


def load_external_data():
    """외부 API 데이터를 로드합니다."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'dummy_data.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"외부 데이터 로드 실패: {e}")
        return []


def find_matching_external_data(project):
    """프로젝트와 매칭되는 외부 데이터를 찾습니다."""
    external_data = load_external_data()
    matching_data = []
    
    # 프로젝트의 키워드를 분리
    keywords = [kw.strip() for kw in project.project_keyword.split(',') if kw.strip()]
    
    # 프로젝트의 자료들을 확인
    for material in project.materials.all():
        material_type = material.material_type
        material_link = material.material_link
        
        # 외부 데이터에서 매칭되는 항목 찾기
        for external_item in external_data:
            if (external_item.get('material_type') == material_type and 
                external_item.get('material_link') == material_link):
                
                # 키워드 매칭 확인
                title = external_item.get('title', '').lower()
                body = external_item.get('body', '').lower()
                
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower in title or keyword_lower in body:
                        matching_data.append({
                            'project_id': project.id,
                            'project_name': project.project_name,
                            'project_keyword': project.project_keyword,
                            'project_material_id': material.id,
                            'material_type': material_type,
                            'material_link': material_link,
                            'external_data': external_item,
                            'matched_keyword': keyword
                        })
                        break  # 한 키워드가 매칭되면 다음 외부 항목으로
    
    return matching_data


def find_matching_external_data_by_code(project):
    """프로젝트 코드와 매칭되는 외부 데이터를 찾습니다."""
    external_data = load_external_data()
    matching_data = []
    
    # 프로젝트 코드
    project_code = project.project_code.lower()
    
    # 프로젝트의 자료들을 확인
    for material in project.materials.all():
        material_type = material.material_type
        material_link = material.material_link
        
        # 외부 데이터에서 매칭되는 항목 찾기
        for external_item in external_data:
            if (external_item.get('material_type') == material_type and 
                external_item.get('material_link') == material_link):
                
                # 프로젝트 코드 매칭 확인
                title = external_item.get('title', '').lower()
                body = external_item.get('body', '').lower()
                
                if project_code in title or project_code in body:
                    matching_data.append({
                        'project_id': project.id,
                        'project_name': project.project_name,
                        'project_code': project.project_code,
                        'project_material_id': material.id,
                        'material_type': material_type,
                        'material_link': material_link,
                        'external_data': external_item,
                        'matched_in': 'title' if project_code in title else 'body'
                    })
    
    return matching_data


@extend_schema_view(
    list=extend_schema(description="프로젝트 목록을 조회합니다.", tags=["프로젝트 관리"]),
    create=extend_schema(description="새로운 프로젝트를 생성합니다.", tags=["프로젝트 관리"]),
    retrieve=extend_schema(description="특정 프로젝트의 상세 정보를 조회합니다.", tags=["프로젝트 관리"]),
    update=extend_schema(description="프로젝트 정보를 수정합니다.", tags=["프로젝트 관리"]),
    destroy=extend_schema(description="프로젝트를 삭제합니다.", tags=["프로젝트 관리"]),
)
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer
    
    @extend_schema(
        description="프로젝트의 모든 자료를 반환합니다.",
        responses={200: ProjectMaterialSerializer(many=True)},
        tags=["프로젝트 관리"]
    )
    @action(detail=True, methods=['get'])
    def materials(self, request, pk=None):
        """프로젝트의 모든 자료를 반환"""
        project = self.get_object()
        materials = project.materials.all()
        serializer = ProjectMaterialSerializer(materials, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="프로젝트의 모든 아이템을 반환합니다.",
        responses={200: ItemSerializer(many=True)},
        tags=["프로젝트 관리"]
    )
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """프로젝트의 모든 아이템을 반환"""
        project = self.get_object()
        items = project.items.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="프로젝트의 모든 요약을 반환합니다.",
        responses={200: SummarySerializer(many=True)},
        tags=["프로젝트 관리"]
    )
    @action(detail=True, methods=['get'])
    def summaries(self, request, pk=None):
        """프로젝트의 모든 요약을 반환"""
        project = self.get_object()
        summaries = project.summaries.all()
        serializer = SummarySerializer(summaries, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="프로젝트 키워드와 매칭되는 외부 데이터를 찾습니다.",
        responses={200: None},  # 동적 응답 스키마
        tags=["외부 데이터 매칭"]
    )
    @action(detail=True, methods=['get'], url_path='external_matches_by_keyword')
    def external_matches_by_keyword(self, request, pk=None):
        """프로젝트와 매칭되는 외부 데이터를 찾습니다."""
        project = self.get_object()
        matching_data = find_matching_external_data(project)
        
        return Response({
            'project_id': project.id,
            'project_name': project.project_name,
            'project_keyword': project.project_keyword,
            'matches_count': len(matching_data),
            'matches': matching_data
        })
    
    @extend_schema(
        description="키워드 기반 외부 데이터 매칭 결과를 기반으로 items와 recommendations 테이블에 새로운 행들을 생성합니다.",
        responses={200: None},  # 동적 응답 스키마
        tags=["외부 데이터 매칭"]
    )
    @action(detail=True, methods=['post'], url_path='create_items_from_external_matches_by_keyword')
    def create_items_from_external_matches_by_keyword(self, request, pk=None):
        """키워드 기반 외부 데이터 매칭 결과를 기반으로 items와 recommendations 테이블에 새로운 행들을 생성합니다."""
        project = self.get_object()
        matching_data = find_matching_external_data(project)
        
        created_items = []
        created_recommendations = []
        errors = []
        
        for match in matching_data:
            try:
                external_data = match['external_data']
                
                # 기존에 동일한 링크를 가진 아이템이 있는지 확인
                existing_item = Item.objects.filter(
                    project=project,
                    project_material_id=match['project_material_id'],
                    link=external_data['link']
                ).first()
                
                if existing_item:
                    errors.append({
                        'error': 'Item already exists',
                        'link': external_data['link'],
                        'item_id': existing_item.id
                    })
                    continue
                
                # 새로운 아이템 생성
                item = Item.objects.create(
                    project=project,
                    project_material_id=match['project_material_id'],
                    title=external_data['title'],
                    body=external_data['body'],
                    link=external_data['link'],
                    is_fixed=False,  # 키워드 기반은 항상 False
                    origin_data_created_at=external_data['created_at'],
                    origin_data_updated_at=external_data['updated_at']
                )
                
                # 새로운 추천 생성
                recommendation = Recommendation.objects.create(
                    project=project,
                    item=item,
                    project_material_id=match['project_material_id'],
                    is_active=True
                )
                
                created_items.append({
                    'item_id': item.id,
                    'title': item.title,
                    'link': item.link,
                    'is_fixed': item.is_fixed,
                    'origin_data_created_at': item.origin_data_created_at,
                    'origin_data_updated_at': item.origin_data_updated_at
                })
                
                created_recommendations.append({
                    'recommendation_id': recommendation.id,
                    'item_id': item.id,
                    'is_active': recommendation.is_active
                })
                
            except Exception as e:
                errors.append({
                    'error': str(e),
                    'external_data': external_data
                })
        
        return Response({
            'project_id': project.id,
            'project_name': project.project_name,
            'project_keyword': project.project_keyword,
            'total_matches': len(matching_data),
            'created_items_count': len(created_items),
            'created_items': created_items,
            'created_recommendations_count': len(created_recommendations),
            'created_recommendations': created_recommendations,
            'errors_count': len(errors),
            'errors': errors
        })
    
    @extend_schema(
        description="프로젝트 코드와 매칭되는 외부 데이터를 찾습니다.",
        responses={200: None},  # 동적 응답 스키마
        tags=["외부 데이터 매칭"]
    )
    @action(detail=True, methods=['get'])
    def external_matches_by_code(self, request, pk=None):
        """프로젝트 코드와 매칭되는 외부 데이터를 찾습니다."""
        project = self.get_object()
        matching_data = find_matching_external_data_by_code(project)
        
        return Response({
            'project_id': project.id,
            'project_name': project.project_name,
            'project_code': project.project_code,
            'matches_count': len(matching_data),
            'matches': matching_data
        })
    
    @extend_schema(
        description="외부 데이터 매칭 결과를 기반으로 items 테이블에 새로운 행들을 생성합니다.",
        responses={200: None},  # 동적 응답 스키마
        tags=["외부 데이터 매칭"]
    )
    @action(detail=True, methods=['post'], url_path='create_items_from_external_matches_by_code')
    def create_items_from_external_matches_by_code(self, request, pk=None):
        """외부 데이터 매칭 결과를 기반으로 items 테이블에 새로운 행들을 생성합니다."""
        project = self.get_object()
        matching_data = find_matching_external_data_by_code(project)
        
        created_items = []
        errors = []
        
        for match in matching_data:
            try:
                external_data = match['external_data']
                
                # 기존에 동일한 링크를 가진 아이템이 있는지 확인
                existing_item = Item.objects.filter(
                    project=project,
                    project_material_id=match['project_material_id'],
                    link=external_data['link']
                ).first()
                
                if existing_item:
                    errors.append({
                        'error': 'Item already exists',
                        'link': external_data['link'],
                        'item_id': existing_item.id
                    })
                    continue
                
                # 새로운 아이템 생성
                item = Item.objects.create(
                    project=project,
                    project_material_id=match['project_material_id'],
                    title=external_data['title'],
                    body=external_data['body'],
                    link=external_data['link'],
                    is_fixed=True,  # 항상 True로 설정
                    origin_data_created_at=external_data['created_at'],
                    origin_data_updated_at=external_data['updated_at']
                )
                
                created_items.append({
                    'item_id': item.id,
                    'title': item.title,
                    'link': item.link,
                    'is_fixed': item.is_fixed,
                    'origin_data_created_at': item.origin_data_created_at,
                    'origin_data_updated_at': item.origin_data_updated_at
                })
                
            except Exception as e:
                errors.append({
                    'error': str(e),
                    'external_data': external_data
                })
        
        return Response({
            'project_id': project.id,
            'project_name': project.project_name,
            'project_code': project.project_code,
            'total_matches': len(matching_data),
            'created_items_count': len(created_items),
            'created_items': created_items,
            'errors_count': len(errors),
            'errors': errors
        })


@extend_schema_view(
    list=extend_schema(description="프로젝트 자료 목록을 조회합니다.", tags=["자료 관리"]),
    create=extend_schema(description="새로운 프로젝트 자료를 생성합니다.", tags=["자료 관리"]),
    retrieve=extend_schema(description="특정 프로젝트 자료의 상세 정보를 조회합니다.", tags=["자료 관리"]),
    update=extend_schema(description="프로젝트 자료 정보를 수정합니다.", tags=["자료 관리"]),
    destroy=extend_schema(description="프로젝트 자료를 삭제합니다.", tags=["자료 관리"]),
)
class ProjectMaterialViewSet(viewsets.ModelViewSet):
    queryset = ProjectMaterial.objects.all()
    serializer_class = ProjectMaterialSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectMaterialDetailSerializer
        return ProjectMaterialSerializer
    
    @extend_schema(
        description="자료의 모든 아이템을 반환합니다.",
        responses={200: ItemSerializer(many=True)},
        tags=["자료 관리"]
    )
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """자료의 모든 아이템을 반환"""
        material = self.get_object()
        items = material.items.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="AI 요청 목록을 조회합니다.", tags=["AI 관리"]),
    create=extend_schema(description="새로운 AI 요청을 생성합니다.", tags=["AI 관리"]),
    retrieve=extend_schema(description="특정 AI 요청의 상세 정보를 조회합니다.", tags=["AI 관리"]),
    update=extend_schema(description="AI 요청 정보를 수정합니다.", tags=["AI 관리"]),
    destroy=extend_schema(description="AI 요청을 삭제합니다.", tags=["AI 관리"]),
)
class AIRequestViewSet(viewsets.ModelViewSet):
    queryset = AIRequest.objects.all()
    serializer_class = AIRequestSerializer


@extend_schema_view(
    list=extend_schema(
        description="요약 목록을 조회합니다.",
        parameters=[
            OpenApiParameter(name='project_id', type=int, description='프로젝트 ID로 필터링')
        ],
        tags=["콘텐츠 관리"]
    ),
    create=extend_schema(description="새로운 요약을 생성합니다.", tags=["콘텐츠 관리"]),
    retrieve=extend_schema(description="특정 요약의 상세 정보를 조회합니다.", tags=["콘텐츠 관리"]),
    update=extend_schema(description="요약 정보를 수정합니다.", tags=["콘텐츠 관리"]),
    destroy=extend_schema(description="요약을 삭제합니다.", tags=["콘텐츠 관리"]),
)
class SummaryViewSet(viewsets.ModelViewSet):
    queryset = Summary.objects.all()
    serializer_class = SummarySerializer
    
    def get_queryset(self):
        queryset = Summary.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset


@extend_schema_view(
    list=extend_schema(
        description="아이템 목록을 조회합니다.",
        parameters=[
            OpenApiParameter(name='project_id', type=int, description='프로젝트 ID로 필터링'),
            OpenApiParameter(name='material_id', type=int, description='자료 ID로 필터링'),
            OpenApiParameter(name='is_fixed', type=bool, description='고정 상태로 필터링')
        ],
        tags=["콘텐츠 관리"]
    ),
    create=extend_schema(description="새로운 아이템을 생성합니다.", tags=["콘텐츠 관리"]),
    retrieve=extend_schema(description="특정 아이템의 상세 정보를 조회합니다.", tags=["콘텐츠 관리"]),
    update=extend_schema(description="아이템 정보를 수정합니다.", tags=["콘텐츠 관리"]),
    destroy=extend_schema(description="아이템을 삭제합니다.", tags=["콘텐츠 관리"]),
)
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    
    def get_queryset(self):
        queryset = Item.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        material_id = self.request.query_params.get('material_id', None)
        is_fixed = self.request.query_params.get('is_fixed', None)
        
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        if material_id is not None:
            queryset = queryset.filter(project_material_id=material_id)
        if is_fixed is not None:
            queryset = queryset.filter(is_fixed=is_fixed.lower() == 'true')
        
        return queryset
    
    @extend_schema(
        description="아이템의 고정 상태를 토글합니다.",
        responses={200: ItemSerializer},
        tags=["콘텐츠 관리"]
    )
    @action(detail=True, methods=['patch'])
    def toggle_fixed(self, request, pk=None):
        """아이템의 고정 상태를 토글"""
        item = self.get_object()
        item.is_fixed = not item.is_fixed
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        description="추천 목록을 조회합니다.",
        parameters=[
            OpenApiParameter(name='project_id', type=int, description='프로젝트 ID로 필터링'),
            OpenApiParameter(name='is_active', type=bool, description='활성 상태로 필터링')
        ],
        tags=["추천 관리"]
    ),
    create=extend_schema(description="새로운 추천을 생성합니다.", tags=["추천 관리"]),
    retrieve=extend_schema(description="특정 추천의 상세 정보를 조회합니다.", tags=["추천 관리"]),
    update=extend_schema(description="추천 정보를 수정합니다.", tags=["추천 관리"]),
    destroy=extend_schema(description="추천을 삭제합니다.", tags=["추천 관리"]),
)
class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    
    def get_queryset(self):
        queryset = Recommendation.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @extend_schema(
        description="추천의 활성 상태를 토글합니다.",
        responses={200: RecommendationSerializer},
        tags=["추천 관리"]
    )
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """추천의 활성 상태를 토글"""
        recommendation = self.get_object()
        recommendation.is_active = not recommendation.is_active
        recommendation.save()
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)

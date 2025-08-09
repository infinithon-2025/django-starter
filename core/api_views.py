from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
import json
import os
from .models import Project, ProjectMaterial, AIRequest, Summary, Item, Recommendation
from .serializers import (
    ProjectSerializer, ProjectDetailSerializer,
    ProjectMaterialSerializer, ProjectMaterialDetailSerializer,
    AIRequestSerializer, SummarySerializer, ItemSerializer, RecommendationSerializer
)

import google.generativeai as genai


# 프로젝트에 종속되지 않는 독립적인 API 키를 사용해야 합니다.
# 실제 API 키는 환경 변수로 관리하는 것을 권장합니다.
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


# 예제용 더미 키
genai.configure(api_key="xxxxx-xxxxx")


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
@method_decorator(csrf_exempt, name='dispatch')
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
        description="프로젝트의 최신 요약을 반환합니다.",
        responses={200: SummarySerializer(many=True)},
        tags=["프로젝트 관리"]
    )
    @action(detail=True, methods=['get'], url_path='latest-summary')
    def latest_summary(self, request, pk=None):
        """프로젝트의 최신 요약을 반환"""
        project = self.get_object()
        latest_summary = project.summaries.order_by('-created_at').first()
        
        if latest_summary:
            serializer = SummarySerializer([latest_summary], many=True)
            return Response(serializer.data)
        else:
            return Response([], status=status.HTTP_200_OK)
    
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
    
    @extend_schema(
        description="프로젝트 아이템들의 본문을 종합하여 AIRequest를 생성하고 요약본을 Summary 테이블에 저장합니다.",
        responses={201: SummarySerializer},
        tags=["AI 관리"]
    )
    @action(detail=True, methods=['post'], url_path='summarize-items')
    def summarize_items(self, request, pk=None):
        """
        프로젝트의 모든 아이템 본문을 합쳐 AIRequest 테이블에 저장하고, 
        결과를 Summary 테이블에도 저장합니다.
        """
        project = self.get_object()
        
        # is_active=True, is_fixed=True인 아이템만 필터링합니다.
        items = project.items.filter(is_active=True, is_fixed=True)
        
        if not items:
            return Response(
                {"detail": "활성화되고 고정된 아이템이 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # title(없는 경우도 있음)과 body를 합쳐서 사용합니다.
        input_texts = []
        for item in items:
            text_to_combine = item.body
            if item.title:
                text_to_combine = f"제목: {item.title}\n내용: {text_to_combine}"
            input_texts.append(text_to_combine)
        
        input_text = "\n\n".join(input_texts)
        
        # 1. 제미나이 API 모델 설정
        model = genai.GenerativeModel('gemini-1.5-flash')

        try:
            # 2. 제미나이 API 호출 및 결과 생성
            response = model.generate_content(
                f"하나의 프로젝트에 대한 다음의 자료를 보기 좋게 요약해줘\n\n자료: {input_text}"
            )
            output_text = response.text

        except Exception as e:
            return Response(
                {"detail": f"Gemini API 호출 실패: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 3. AIRequest 객체를 생성하고 저장합니다.
        ai_request = AIRequest.objects.create(
            input=input_text,
            output=output_text,
            description=f"'{project.project_name}' 프로젝트 아이템 요약 요청"
        )

        # 4. AIRequest의 output을 정제하여 Summary 테이블에 저장합니다.
        # 이 예제에서는 AIRequest의 output을 그대로 Summary의 content로 사용합니다.
        summary = Summary.objects.create(
            project=project,
            ai_request=ai_request,
            content=output_text
        )

        # 5. 생성된 summary 객체를 직렬화하여 응답으로 반환합니다.
        serializer = SummarySerializer(summary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(description="프로젝트 자료 목록을 조회합니다.", tags=["자료 관리"]),
    create=extend_schema(description="새로운 프로젝트 자료를 생성합니다.", tags=["자료 관리"]),
    retrieve=extend_schema(description="특정 프로젝트 자료의 상세 정보를 조회합니다.", tags=["자료 관리"]),
    update=extend_schema(description="프로젝트 자료 정보를 수정합니다.", tags=["자료 관리"]),
    destroy=extend_schema(description="프로젝트 자료를 삭제합니다.", tags=["자료 관리"]),
)
@method_decorator(csrf_exempt, name='dispatch')
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
@method_decorator(csrf_exempt, name='dispatch')
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
@method_decorator(csrf_exempt, name='dispatch')
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
@method_decorator(csrf_exempt, name='dispatch')
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
    
    @extend_schema(
        description="아이템의 활성 상태를 토글합니다.",
        responses={200: ItemSerializer},
        tags=["콘텐츠 관리"]
    )
    @action(detail=True, methods=['patch'], url_path='toggle_active')
    def toggle_active(self, request, pk=None):
        """아이템의 활성 상태를 토글"""
        item = self.get_object()
        was_active = item.is_active
        item.is_active = not item.is_active
        item.save()
        
        # 상태 변경 메시지 생성
        status_text = "활성화" if item.is_active else "비활성화"
        message = f"아이템 '{item.title}'이(가) {status_text}되었습니다."
        
        serializer = self.get_serializer(item)
        response_data = serializer.data
        response_data['message'] = message
        return Response(response_data)
    
    @extend_schema(
        description="아이템에 대한 매칭되는 추천이 있는지 확인합니다.",
        responses={200: None},  # 동적 응답 스키마
        tags=["콘텐츠 관리"]
    )
    @action(detail=True, methods=['get'], url_path='matching_recommendation')
    def matching_recommendation(self, request, pk=None):
        """아이템에 대한 매칭되는 추천 확인"""
        item = self.get_object()
        
        # 해당 아이템에 대한 추천 찾기
        recommendation = Recommendation.objects.filter(
            item_id=item.id,
            is_active=True
        ).first()
        
        if recommendation:
            # 추천이 있는 경우
            response_data = {
                'item_id': item.id,
                'item_title': item.title,
                'has_recommendation': True,
                'recommendation': {
                    'id': recommendation.id,
                    'project_id': recommendation.project_id,
                    'project_material_id': recommendation.project_material_id,
                    'is_active': recommendation.is_active,
                    'created_at': recommendation.created_at,
                    'updated_at': recommendation.updated_at
                },
                'message': f"아이템 '{item.title}'에 대한 활성 추천이 있습니다."
            }
        else:
            # 추천이 없는 경우
            response_data = {
                'item_id': item.id,
                'item_title': item.title,
                'has_recommendation': False,
                'recommendation': None,
                'message': f"아이템 '{item.title}'에 대한 활성 추천이 없습니다."
            }
        
        return Response(response_data)


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
@method_decorator(csrf_exempt, name='dispatch')
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
        description="추천의 활성 상태를 토글합니다. False로 변경 시 연관된 아이템이 삭제됩니다.",
        responses={200: RecommendationSerializer},
        tags=["추천 관리"]
    )
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """추천의 활성 상태를 토글하고, False로 변경 시 연관된 아이템 삭제"""
        recommendation = self.get_object()
        was_active = recommendation.is_active
        recommendation.is_active = not recommendation.is_active
        recommendation.save()
        
        # False로 토글된 경우 연관된 아이템 삭제
        if was_active and not recommendation.is_active:
            try:
                # 연관된 아이템 찾기 및 삭제
                associated_item = Item.objects.filter(id=recommendation.item_id).first()
                if associated_item:
                    item_id = associated_item.id
                    associated_item.delete()
                    message = f"추천이 비활성화되었고, 연관된 아이템(ID: {item_id})이 삭제되었습니다."
                else:
                    message = "추천이 비활성화되었습니다. (연관된 아이템을 찾을 수 없습니다.)"
            except Exception as e:
                message = f"추천이 비활성화되었습니다. (아이템 삭제 중 오류: {str(e)})"
        else:
            message = f"추천이 {'활성화' if recommendation.is_active else '비활성화'}되었습니다."
        
        serializer = self.get_serializer(recommendation)
        response_data = serializer.data
        response_data['message'] = message
        return Response(response_data)
    
    @extend_schema(
        description="특정 아이템에 대한 추천을 찾습니다.",
        parameters=[
            OpenApiParameter(name='item_id', type=int, description='아이템 ID', required=True)
        ],
        responses={200: RecommendationSerializer(many=True)},
        tags=["추천 관리"]
    )
    @action(detail=False, methods=['get'], url_path='by_item')
    def by_item(self, request):
        """특정 아이템에 대한 추천 찾기"""
        item_id = request.query_params.get('item_id')
        
        if not item_id:
            return Response({
                'error': 'item_id 파라미터가 필요합니다.'
            }, status=400)
        
        try:
            item_id = int(item_id)
        except ValueError:
            return Response({
                'error': 'item_id는 유효한 정수여야 합니다.'
            }, status=400)
        
        # 해당 아이템에 대한 모든 추천 찾기 (활성/비활성 모두)
        recommendations = Recommendation.objects.filter(item_id=item_id)
        
        if recommendations.exists():
            serializer = self.get_serializer(recommendations, many=True)
            return Response({
                'item_id': item_id,
                'recommendations_count': recommendations.count(),
                'recommendations': serializer.data,
                'message': f"아이템 ID {item_id}에 대한 추천 {recommendations.count()}개를 찾았습니다."
            })
        else:
            return Response({
                'item_id': item_id,
                'recommendations_count': 0,
                'recommendations': [],
                'message': f"아이템 ID {item_id}에 대한 추천이 없습니다."
            })

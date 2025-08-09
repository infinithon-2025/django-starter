from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ProjectViewSet, ProjectMaterialViewSet, AIRequestViewSet,
    SummaryViewSet, ItemViewSet, RecommendationViewSet
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'materials', ProjectMaterialViewSet)
router.register(r'ai-requests', AIRequestViewSet)
router.register(r'summaries', SummaryViewSet)
router.register(r'items', ItemViewSet)
router.register(r'recommendations', RecommendationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

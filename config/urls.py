from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from core.views import health
from core.api_docs import HighlightedAPISchemaView, HighlightedSwaggerView, HighlightedRedocView, APIHighlightView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", health, name="health"),
    path("", include("core.urls")),
    
    # API 문서
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # 하이라이트된 API 문서
    path('api/schema/highlighted/', HighlightedAPISchemaView.as_view(), name='schema-highlighted'),
    path('api/docs/highlighted/', HighlightedSwaggerView.as_view(), name='swagger-ui-highlighted'),
    path('api/redoc/highlighted/', HighlightedRedocView.as_view(), name='redoc-highlighted'),
    path('api/highlight/', APIHighlightView.as_view(), name='api-highlight'),
]

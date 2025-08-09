from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import markdown
from .models import Project, ProjectMaterial, AIRequest, Summary, Item, Recommendation


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'author_email', 'project_code', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('project_name', 'author_email', 'project_code', 'project_keyword')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('기본 정보', {
            'fields': ('author_email', 'project_name', 'project_code', 'project_keyword')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectMaterial)
class ProjectMaterialAdmin(admin.ModelAdmin):
    list_display = ('material_type', 'project', 'material_link', 'created_at')
    list_filter = ('material_type', 'created_at', 'updated_at')
    search_fields = ('project__project_name', 'material_link', 'project__project_code')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('기본 정보', {
            'fields': ('project', 'material_type', 'material_link')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    search_fields = ('input', 'output', 'description')
    fieldsets = (
        ('AI 요청 정보', {
            'fields': ('input', 'output', 'description')
        }),
        ('시간 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('project', 'ai_request', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('project__project_name', 'content', 'project__project_code')
    readonly_fields = ('created_at', 'updated_at', 'content_preview')
    fieldsets = (
        ('요약 정보', {
            'fields': ('project', 'ai_request', 'content')
        }),
        ('Markdown 미리보기', {
            'fields': ('content_preview',),
            'classes': ('collapse',)
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        if obj.content:
            # Markdown을 HTML로 변환
            html_content = markdown.markdown(obj.content, extensions=['extra', 'codehilite'])
            
            # CSS 스타일을 별도 변수로 정의
            css_style = '''
                <style>
                    /* 모든 요소에 대한 강제 스타일 적용 */
                    .markdown-preview, .markdown-preview * {{
                        color: #000000 !important;
                        font-weight: 400 !important;
                        text-shadow: none !important;
                        -webkit-font-smoothing: antialiased !important;
                        -moz-osx-font-smoothing: grayscale !important;
                    }}
                    
                    /* 제목 스타일 강제 적용 */
                    .markdown-preview h1, .markdown-preview h2, .markdown-preview h3, .markdown-preview h4, .markdown-preview h5, .markdown-preview h6 {{
                        color: #000000 !important;
                        font-weight: 700 !important;
                        margin-top: 20px !important;
                        margin-bottom: 10px !important;
                        text-shadow: none !important;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                    }}
                    
                    .markdown-preview h1 {{
                        font-size: 24px !important;
                        color: #000000 !important;
                        font-weight: 800 !important;
                    }}
                    
                    .markdown-preview h2 {{
                        font-size: 20px !important;
                        color: #000000 !important;
                        font-weight: 800 !important;
                    }}
                    
                    .markdown-preview h3 {{
                        font-size: 18px !important;
                        color: #000000 !important;
                        font-weight: 700 !important;
                    }}
                    
                    .markdown-preview h4 {{
                        font-size: 16px !important;
                        color: #000000 !important;
                        font-weight: 700 !important;
                    }}
                    
                    /* 단락과 목록 스타일 */
                    .markdown-preview p {{
                        color: #000000 !important;
                        margin-bottom: 12px !important;
                        font-weight: 400 !important;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                    }}
                    
                    .markdown-preview ul, .markdown-preview ol {{
                        color: #000000 !important;
                        margin-bottom: 12px !important;
                        padding-left: 20px !important;
                        font-weight: 400 !important;
                    }}
                    
                    .markdown-preview li {{
                        color: #000000 !important;
                        margin-bottom: 6px !important;
                        font-weight: 400 !important;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                    }}
                    
                    /* 강조 텍스트 */
                    .markdown-preview strong, .markdown-preview b {{
                        color: #000000 !important;
                        font-weight: 700 !important;
                    }}
                    
                    .markdown-preview em, .markdown-preview i {{
                        color: #000000 !important;
                        font-style: italic !important;
                        font-weight: 400 !important;
                    }}
                    
                    /* 코드 블록 */
                    .markdown-preview code {{
                        background-color: #f8f9fa !important;
                        color: #e83e8c !important;
                        padding: 2px 4px !important;
                        border-radius: 3px !important;
                        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
                        font-weight: 600 !important;
                    }}
                    
                    .markdown-preview pre {{
                        background-color: #f8f9fa !important;
                        padding: 12px !important;
                        border-radius: 5px !important;
                        overflow-x: auto !important;
                        border: 1px solid #e9ecef !important;
                    }}
                    
                    /* 인용구 */
                    .markdown-preview blockquote {{
                        border-left: 4px solid #007bff !important;
                        padding-left: 15px !important;
                        margin: 15px 0 !important;
                        color: #000000 !important;
                        font-style: italic !important;
                        font-weight: 400 !important;
                    }}
                    
                    /* 추가 강제 스타일 */
                    .markdown-preview div, .markdown-preview span {{
                        color: #000000 !important;
                        font-weight: 400 !important;
                    }}
                </style>
            '''
            
            return format_html(
                '<div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); color: #000000 !important; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif; line-height: 1.6; font-weight: 400 !important;">{}{}</div>',
                mark_safe(css_style),
                mark_safe(html_content)
            )
        return "내용이 없습니다."
    
    content_preview.short_description = "Markdown 미리보기"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'body', 'project', 'project_material', 'is_fixed', 'is_active', 'created_at')
    list_filter = ('is_fixed', 'is_active', 'created_at', 'updated_at', 'project_material__material_type')
    search_fields = ('title', 'body', 'project__project_name', 'project__project_code')
    readonly_fields = ('created_at', 'updated_at', 'origin_data_created_at', 'origin_data_updated_at')
    fieldsets = (
        ('기본 정보', {
            'fields': ('project', 'project_material', 'channel_name', 'title', 'body', 'link')
        }),
        ('상태 정보', {
            'fields': ('is_fixed', 'is_active')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at', 'origin_data_created_at', 'origin_data_updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('item', 'project', 'project_material', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at', 'project_material__material_type')
    search_fields = ('item__title', 'project__project_name', 'project__project_code')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('추천 정보', {
            'fields': ('project', 'item', 'project_material', 'is_active')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

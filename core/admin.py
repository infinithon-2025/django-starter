from django.contrib import admin
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
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('요약 정보', {
            'fields': ('project', 'ai_request', 'content')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel_name', 'project', 'project_material', 'is_fixed', 'created_at')
    list_filter = ('is_fixed', 'created_at', 'updated_at', 'project_material__material_type')
    search_fields = ('title', 'channel_name', 'body', 'project__project_name', 'project__project_code')
    readonly_fields = ('created_at', 'updated_at', 'origin_data_created_at', 'origin_data_updated_at')
    fieldsets = (
        ('기본 정보', {
            'fields': ('project', 'project_material', 'channel_name', 'title', 'body', 'link')
        }),
        ('상태 정보', {
            'fields': ('is_fixed',)
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
